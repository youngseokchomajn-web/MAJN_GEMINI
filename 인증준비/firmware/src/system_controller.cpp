#include "system_controller.h"

#include <ArduinoJson.h>
#include <Preferences.h>
#include "safety_manager.h"
#include "power_manager.h"
#include "amplifier_manager.h"
#include "vibration_controller.h"
#include "ota_ble_service.h"
#if defined(MAJN_WIFI_CONTROL)
#include "wifi_manager.h"
#endif

extern volatile bool systemActive;
extern volatile unsigned long activeStateStartTime;

namespace MajnSystemCtrl {

static volatile uint32_t gLastClientActivity = 0;
static volatile uint32_t gTargetDurationMs = 15 * 60 * 1000; // Default 15 minutes
const uint32_t MAX_ALLOWED_DURATION_MS = 30 * 60 * 1000;    // Maximum device runtime watchdog (30 min)
static SemaphoreHandle_t sCmdMutex = nullptr;
static char sCurrentPreset[16] = "pink";

void setRunningDurationMinutes(uint16_t minutes) {
    if (minutes < 1) minutes = 1;
    if (minutes > 30) minutes = 30;
    gTargetDurationMs = (uint32_t)minutes * 60 * 1000;
    Serial.printf("[SystemCtrl] Target running duration set to %u minutes (%u ms)\n", minutes, gTargetDurationMs);
}

uint16_t getRunningDurationMinutes() {
    return (uint16_t)(gTargetDurationMs / (60 * 1000));
}

uint32_t getTargetDurationMs() {
    return gTargetDurationMs;
}

uint32_t getRemainingSeconds() {
    if (!systemActive || activeStateStartTime == 0) {
        return (uint32_t)(gTargetDurationMs / 1000);
    }
    uint32_t elapsed = millis() - activeStateStartTime;
    if (elapsed >= gTargetDurationMs) return 0;
    return (gTargetDurationMs - elapsed) / 1000;
}

static const char* stateName(MajnBle::SystemState state) {
    switch (state) {
        case MajnBle::SystemState::BOOT: return "BOOT";
        case MajnBle::SystemState::SELF_TEST: return "SELF_TEST";
        case MajnBle::SystemState::READY: return "READY";
        case MajnBle::SystemState::RUNNING: return "RUNNING";
        case MajnBle::SystemState::STOPPING: return "STOPPING";
        case MajnBle::SystemState::FAULT: return "FAULT";
    }
    return "FAULT";
}

void init() {
    gLastClientActivity = millis();
    if (!sCmdMutex) {
        sCmdMutex = xSemaphoreCreateMutex();
    }
}

bool isSystemActive() {
    return systemActive;
}

const char* getCurrentStateName() {
    return stateName(MajnSafety::getSystemState(systemActive));
}

static volatile bool sRebootPending = false;
static uint32_t sRebootAt = 0;

static void scheduleReboot(uint32_t delayMs) {
    sRebootPending = true;
    sRebootAt = millis() + delayMs;
}

void tickSystem() {
    if (sRebootPending && millis() >= sRebootAt) {
        Serial.println("[SystemCtrl] Executing scheduled reboot now.");
        esp_restart();
    }
}

void triggerSafeStop() {
    activeStateStartTime = 0;
    systemActive = false;
    MajnSafety::requestSafeStop();
}

void triggerEmergencyStop() {
    activeStateStartTime = 0;
    systemActive = false;
    MajnSafety::requestEmergencyStop();
}

void noteClientActivity() {
    gLastClientActivity = millis();
}

uint32_t getLastClientActivity() {
    return gLastClientActivity;
}

void checkClientTimeout(uint32_t timeoutMs) {
    tickSystem();
    if (systemActive && (millis() - gLastClientActivity > timeoutMs)) {
        Serial.printf("[SystemCtrl] Client connection timeout (%u ms). Safe Stop triggered!\n", timeoutMs);
        triggerSafeStop();
    }
}

static void buildAckJson(int id, const char* cmd, const char* status, const char* state, String& outJson) {
    JsonDocument doc;
    doc["type"] = "ack";
    doc["id"] = id;
    doc["cmd"] = cmd;
    doc["status"] = status;
    doc["state"] = state;

    doc["amp_status"] = MajnAmplifier::getStatusString();
    uint8_t aState = 0, cFault = 0, gFault = 0;
    if (MajnAmplifier::getDiagnostics(aState, cFault, gFault)) {
        doc["amp_state"] = aState;
        doc["chan_fault"] = cFault;
        doc["glob_fault"] = gFault;
        char diagBuf[64];
        snprintf(diagBuf, sizeof(diagBuf), "Amp:S=0x%02X,CF=0x%02X,GF=0x%02X [%s]", aState, cFault, gFault, MajnAmplifier::getStatusString());
        doc["diag"] = diagBuf;
    } else {
        char diagBuf[64];
        snprintf(diagBuf, sizeof(diagBuf), "Amp:[%s]", MajnAmplifier::getStatusString());
        doc["diag"] = diagBuf;
    }

    serializeJson(doc, outJson);
}

void resetFault() {
    if (!MajnSafety::isSafetyLockTriggered()) {
        return;
    }
    uint8_t aState = 0, cFault = 0, gFault = 0;
    if (MajnAmplifier::getDiagnostics(aState, cFault, gFault) && cFault == 0 && gFault == 0) {
        if (MajnAmplifier::enterStandbyState()) {
            MajnSafety::resetSafetyLock();
        }
    }
}

bool handleJsonCommand(const char* jsonStr, String& responseJson) {
    noteClientActivity();

    struct MutexGuard {
        SemaphoreHandle_t m;
        bool locked;
        MutexGuard(SemaphoreHandle_t mutex) : m(mutex), locked(false) {
            if (m && xSemaphoreTake(m, pdMS_TO_TICKS(1000)) == pdTRUE) {
                locked = true;
            }
        }
        ~MutexGuard() {
            if (m && locked) {
                xSemaphoreGive(m);
            }
        }
    } guard(sCmdMutex);

    if (sCmdMutex && !guard.locked) {
        Serial.println("[SystemCtrl] handleJsonCommand: Mutex acquire timed out (busy).");
        buildAckJson(-1, "BUSY", "rejected", getCurrentStateName(), responseJson);
        return false;
    }

    if (!jsonStr || strlen(jsonStr) == 0) {
        buildAckJson(-1, "UNKNOWN", "rejected", getCurrentStateName(), responseJson);
        return false;
    }

    JsonDocument doc;
    DeserializationError err = deserializeJson(doc, jsonStr);
    if (err) {
        buildAckJson(-1, "UNKNOWN", "rejected", getCurrentStateName(), responseJson);
        return false;
    }

    int id = doc["id"] | -1;
    const char* cmd = doc["cmd"] | "";

    // Unified OTA Protection Gate: Reject all control commands during active Wi-Fi or BLE firmware update
    bool isAnyOtaActive = MajnBleOta::isOtaInProgress();
#if defined(MAJN_WIFI_CONTROL)
    if (MajnWiFi::isOtaInProgress()) {
        isAnyOtaActive = true;
    }
#endif
    if (isAnyOtaActive && strcmp(cmd, "PING") != 0 && strcmp(cmd, "STATUS") != 0) {
        Serial.printf("[SystemCtrl] Command '%s' rejected: Firmware OTA update is in progress.\n", cmd);
        buildAckJson(id, cmd, "rejected", "OTA_ACTIVE", responseJson);
        return false;
    }

    if (strcmp(cmd, "PING") == 0) {
        buildAckJson(id, cmd, "applied", getCurrentStateName(), responseJson);
        return true;
    }
    if (strcmp(cmd, "STATUS") == 0) {
        buildAckJson(id, cmd, "applied", getCurrentStateName(), responseJson);
        return true;
    }

    if (strcmp(cmd, "START") == 0) {
        if (MajnSafety::isSafetyLockTriggered()) {
            buildAckJson(id, cmd, "fault", "FAULT", responseJson);
            return false;
        }

        float f = doc["frequency_hz"] | MajnVibration::getTargetFrequency();
        float a = doc["amplitude"] | (MajnVibration::getTargetAmplitude() > 0.05f ? MajnVibration::getTargetAmplitude() : 0.4f);

        if (f < 30.0f || f > 65.0f || a < 0.0f || a > 0.5f) {
            Serial.printf("[SystemCtrl] START rejected: Invalid parameters f=%.1f, a=%.2f (Allowed 30~65Hz, 0~0.5)\n", f, a);
            buildAckJson(id, cmd, "rejected", getCurrentStateName(), responseJson);
            return false;
        }

        if (!doc["duration_min"].isNull()) {
            uint16_t dm = doc["duration_min"].as<uint16_t>();
            if (dm >= 1 && dm <= 30) {
                setRunningDurationMinutes(dm);
            }
        }

        // Auto-retry amplifier init if not ready
        if (!MajnAmplifier::isAmplifierReady()) {
            if (!MajnAmplifier::initAmplifier()) {
                Serial.println("[SystemCtrl] START rejected: Amplifier init failed.");
                systemActive = false;
                buildAckJson(id, cmd, "failed", getCurrentStateName(), responseJson);
                return false;
            }
        }

        // Enter Play state
        if (!MajnAmplifier::enterPlayState()) {
            Serial.println("[SystemCtrl] START rejected: enterPlayState() failed.");
            systemActive = false;
            buildAckJson(id, cmd, "failed", getCurrentStateName(), responseJson);
            return false;
        }

        // Check diagnostics registers
        uint8_t aState = 0, cFault = 0, gFault = 0;
        if (!MajnAmplifier::getDiagnostics(aState, cFault, gFault) || cFault != 0 || gFault != 0) {
            Serial.printf("[SystemCtrl] START rejected: Fault detected (CF=0x%02X, GF=0x%02X).\n", cFault, gFault);
            systemActive = false;
            MajnAmplifier::enterStandbyState();
            buildAckJson(id, cmd, "failed", "FAULT", responseJson);
            return false;
        }

        systemActive = true;
        activeStateStartTime = millis();
        MajnVibration::setTarget(f, a);
        buildAckJson(id, cmd, "applied", "RUNNING", responseJson);
        return true;
    }

    if (strcmp(cmd, "SET_DURATION") == 0) {
        if (!doc["duration_min"].isNull()) {
            uint16_t dm = doc["duration_min"].as<uint16_t>();
            if (dm >= 1 && dm <= 30) {
                setRunningDurationMinutes(dm);
                buildAckJson(id, cmd, "applied", getCurrentStateName(), responseJson);
                return true;
            }
        }
        buildAckJson(id, cmd, "rejected", getCurrentStateName(), responseJson);
        return false;
    }

    if (strcmp(cmd, "STOP") == 0) {
        triggerSafeStop();
        buildAckJson(id, cmd, "applied", getCurrentStateName(), responseJson);
        return true;
    }

    if (strcmp(cmd, "RESET_WIFI_CRED") == 0) {
        Preferences prefs;
        prefs.begin("majn", false);
        prefs.remove("wifi_pass");
        prefs.end();
        Serial.println("[SystemCtrl] Wi-Fi passphrase cleared from NVS via authenticated command. Rebooting...");
        scheduleReboot(500);
        buildAckJson(id, cmd, "applied", "REBOOTING", responseJson);
        return true;
    }

    if (strcmp(cmd, "ESTOP") == 0) {
        triggerEmergencyStop();
        buildAckJson(id, cmd, "applied", "FAULT", responseJson);
        return true;
    }

    if (strcmp(cmd, "RESET_FAULT") == 0) {
        if (!MajnSafety::isSafetyLockTriggered()) {
            buildAckJson(id, cmd, "applied", getCurrentStateName(), responseJson);
            return true;
        }

        uint8_t aState = 0, cFault = 0, gFault = 0;
        if (!MajnAmplifier::getDiagnostics(aState, cFault, gFault) || cFault != 0 || gFault != 0) {
            buildAckJson(id, cmd, "rejected", "FAULT", responseJson);
            return false;
        }

        if (!MajnAmplifier::enterStandbyState()) {
            buildAckJson(id, cmd, "rejected", "FAULT", responseJson);
            return false;
        }

        MajnSafety::resetSafetyLock();
        buildAckJson(id, cmd, "applied", "READY", responseJson);
        return true;
    }

    if (strcmp(cmd, "SET_VIBRATION") == 0) {
        if (MajnSafety::isSafetyLockTriggered()) {
            buildAckJson(id, cmd, "rejected", "FAULT", responseJson);
            return false;
        }
        float f = doc["frequency_hz"] | MajnVibration::getTargetFrequency();
        float a = doc["amplitude"] | MajnVibration::getTargetAmplitude();
        if (f < 30.0f || f > 65.0f || a < 0.0f || a > 0.5f) {
            buildAckJson(id, cmd, "rejected", getCurrentStateName(), responseJson);
            return false;
        }
        MajnVibration::setTarget(f, a);
        buildAckJson(id, cmd, "applied", getCurrentStateName(), responseJson);
        return true;
    }

    if (strcmp(cmd, "SET_FREQUENCY") == 0) {
        if (MajnSafety::isSafetyLockTriggered()) {
            buildAckJson(id, cmd, "rejected", "FAULT", responseJson);
            return false;
        }
        if (doc["frequency_hz"].isNull()) {
            buildAckJson(id, cmd, "rejected", getCurrentStateName(), responseJson);
            return false;
        }
        float f = doc["frequency_hz"].as<float>();
        if (f < 30.0f || f > 65.0f) {
            buildAckJson(id, cmd, "rejected", getCurrentStateName(), responseJson);
            return false;
        }
        MajnVibration::setTarget(f, MajnVibration::getTargetAmplitude());
        buildAckJson(id, cmd, "applied", getCurrentStateName(), responseJson);
        return true;
    }

    if (strcmp(cmd, "SET_AMPLITUDE") == 0) {
        if (MajnSafety::isSafetyLockTriggered()) {
            buildAckJson(id, cmd, "rejected", "FAULT", responseJson);
            return false;
        }
        if (doc["amplitude"].isNull()) {
            buildAckJson(id, cmd, "rejected", getCurrentStateName(), responseJson);
            return false;
        }
        float a = doc["amplitude"].as<float>();
        if (a < 0.0f || a > 0.5f) {
            buildAckJson(id, cmd, "rejected", getCurrentStateName(), responseJson);
            return false;
        }
        MajnVibration::setTarget(MajnVibration::getTargetFrequency(), a);
        buildAckJson(id, cmd, "applied", getCurrentStateName(), responseJson);
        return true;
    }

    if (strcmp(cmd, "SET_VOLUME") == 0) {
        if (MajnSafety::isSafetyLockTriggered()) {
            buildAckJson(id, cmd, "rejected", "FAULT", responseJson);
            return false;
        }
        if (doc["volume"].isNull()) {
            buildAckJson(id, cmd, "rejected", getCurrentStateName(), responseJson);
            return false;
        }
        int v = doc["volume"].as<int>();
        if (v < 0 || v > 100) {
            buildAckJson(id, cmd, "rejected", getCurrentStateName(), responseJson);
            return false;
        }
        bool ok = MajnAmplifier::setVolume((uint8_t)v);
        buildAckJson(id, cmd, ok ? "applied" : "failed", getCurrentStateName(), responseJson);
        return ok;
    }

    if (strcmp(cmd, "SET_PRESET") == 0) {
        if (MajnSafety::isSafetyLockTriggered()) {
            buildAckJson(id, cmd, "rejected", "FAULT", responseJson);
            return false;
        }
        if (doc["preset"].isNull()) {
            buildAckJson(id, cmd, "rejected", getCurrentStateName(), responseJson);
            return false;
        }
        const char* p = doc["preset"].as<const char*>();
        if (!p || strlen(p) == 0) {
            buildAckJson(id, cmd, "rejected", getCurrentStateName(), responseJson);
            return false;
        }
        strncpy(sCurrentPreset, p, sizeof(sCurrentPreset) - 1);
        sCurrentPreset[sizeof(sCurrentPreset) - 1] = '\0';
        buildAckJson(id, cmd, "applied", getCurrentStateName(), responseJson);
        return true;
    }

    if (strcmp(cmd, "REBOOT") == 0) {
        scheduleReboot(500);
        buildAckJson(id, cmd, "applied", "REBOOTING", responseJson);
        Serial.println("[SystemCtrl] Remote reboot requested. Scheduled in 500ms.");
        return true;
    }

    buildAckJson(id, cmd, "rejected", getCurrentStateName(), responseJson);
    return false;
}

void getTelemetryJson(String& outJson, const AccelData& accel) {
    JsonDocument doc;
    doc["type"] = "telemetry";
    doc["state"] = getCurrentStateName();
    doc["safety_lock"] = MajnSafety::isSafetyLockTriggered();
    doc["target_freq"] = MajnVibration::getTargetFrequency();
    doc["current_amp"] = MajnVibration::getCurrentAmplitude();
    doc["target_amp"] = MajnVibration::getTargetAmplitude();
    doc["duration_min"] = getRunningDurationMinutes();
    doc["remaining_sec"] = getRemainingSeconds();
    doc["fw_version"] = "v1.2-wireless";
    doc["build_date"] = "2026-10-31";

    // Distinguish measured IMU vs board location
    JsonObject imu = doc["board_imu"].to<JsonObject>();
    imu["x"] = accel.x_g;
    imu["y"] = accel.y_g;
    imu["z"] = accel.z_g;
    imu["note"] = "PCB on-board sensor only (NOT mattress pad)";

    doc["amp_status"] = MajnAmplifier::getStatusString();
    uint8_t aState = 0, cFault = 0, gFault = 0;
    if (MajnAmplifier::getDiagnostics(aState, cFault, gFault)) {
        doc["amp_diag"] = (cFault == 0 && gFault == 0) ? "OK" : "FAULT";
        doc["amp_state"] = aState;
        doc["chan_fault"] = cFault;
        doc["glob_fault"] = gFault;
    } else {
        doc["amp_diag"] = "OFFLINE";
    }

    serializeJson(doc, outJson);
}

} // namespace MajnSystemCtrl
