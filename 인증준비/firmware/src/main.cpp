#include <Arduino.h>
#include <esp_ota_ops.h>

#include "ble_protocol.h"
#include "ble_manager.h"
#include "system_controller.h"
#if defined(MAJN_WIFI_CONTROL)
#include "wifi_manager.h"
#endif
#include "safety_manager.h"
#include "power_manager.h"
#include "amplifier_manager.h"
#include "imu_manager.h"
#include "vibration_controller.h"
#include "ota_manager.h"

// -------------------------------------------------------------------------
// Global Operational State & FreeRTOS Orchestration
// -------------------------------------------------------------------------
volatile bool systemActive = false;
volatile unsigned long activeStateStartTime = 0;
const unsigned long MAX_RUNNING_TIME_MS = 30 * 60 * 1000; // Device-level runtime safety timeout (30 minutes). Not a claim of KC regulatory requirement.

static AccelData latestAccel = {0, 0, 0, 0.0f, 0.0f, 1.0f};

TaskHandle_t commTaskHandle = NULL;
TaskHandle_t controlTaskHandle = NULL;
TaskHandle_t audioTaskHandle = NULL;

// -------------------------------------------------------------------------
// Hardware Emergency Shutdown Callback (Invoked by SafetyManager)
// -------------------------------------------------------------------------
void hardwareEmergencyShutdown() {
    // 1. Hardware Mute/Shutdown amplifier outputs immediately
    MajnAmplifier::shutdownAmplifier();
    // 2. Disable 12V Boost Regulator to kill high-voltage power rail
    MajnPower::disableBoost();
}

// -------------------------------------------------------------------------
// Core 1 Task: Real-time Audio Synthesis Stream
// -------------------------------------------------------------------------
void AudioOutputTask(void *pvParameters) {
    (void)pvParameters;
    Serial.println("[Core 1] I2S Audio Task Running.");

    for (;;) {
        MajnVibration::renderAudioBlock();
    }
}

// -------------------------------------------------------------------------
// Core 1 Task: Closed-loop Vibration Control (50Hz / 20ms)
// -------------------------------------------------------------------------
void VibrationControlTask(void *pvParameters) {
    (void)pvParameters;
    Serial.println("[Core 1] Vibration Control Task Running (50Hz).");

    TickType_t xLastWakeTime = xTaskGetTickCount();
    const TickType_t xFrequency = pdMS_TO_TICKS(20);
    const float dt = 0.02f;

    for (;;) {
        vTaskDelayUntil(&xLastWakeTime, xFrequency);

        if (MajnSafety::isSafetyLockTriggered()) {
            continue;
        }

        // Device-level automatic run-time cutoff (30 minutes software safety watchdog)
        if (systemActive && (activeStateStartTime > 0) && (millis() - activeStateStartTime > MAX_RUNNING_TIME_MS)) {
            Serial.println("[Safety] 30 minutes limit exceeded. Soft Stop engaged.");
            MajnSafety::requestSafeStop();
        }

        // Advance PID & Soft Start/Stop Ramping
        MajnVibration::tickControlLoop(dt);

        // Active Hardware Fail-safe Supervisor (Every 100ms: 5 ticks of 20ms)
        static uint8_t sAmpSuperviseCounter = 0;
        if (++sAmpSuperviseCounter >= 5) {
            sAmpSuperviseCounter = 0;
            if (systemActive) {
                if (!MajnAmplifier::isAmplifierReady()) {
                    Serial.println("[Safety] CRITICAL: systemActive is TRUE but Amplifier is NOT ready! Engaging Emergency Stop.");
                    MajnSafety::requestEmergencyStop();
                } else {
                    uint8_t aState = 0, cFault = 0, gFault = 0;
                    if (!MajnAmplifier::getDiagnostics(aState, cFault, gFault)) {
                        Serial.println("[Safety] CRITICAL: TAS5805M I2C communication lost! Engaging Emergency Stop.");
                        MajnSafety::requestEmergencyStop();
                    } else if (cFault != 0 || gFault != 0) {
                        Serial.printf("[Safety] CRITICAL: TAS5805M Hardware Fault! CFault=0x%02X, GFault=0x%02X. Engaging Emergency Stop.\n", cFault, gFault);
                        MajnSafety::requestEmergencyStop();
                    }
                }
            }
        }

        // Read accelerometer sensor
        MajnImu::readAcceleration(latestAccel);
    }
}

// -------------------------------------------------------------------------
// Core 0 Task: Wi-Fi SoftAP + BLE Dual Communication & Telemetry
// -------------------------------------------------------------------------
void WiFiBTCommunicationTask(void *pvParameters) {
    (void)pvParameters;
    Serial.println("[Core 0] Dual Wi-Fi SoftAP + BLE Task Running.");
    
    uint8_t bleNotifyCounter = 0;

    for (;;) {
#if defined(MAJN_WIFI_CONTROL)
        MajnWiFi::handleClient();
        MajnWiFi::updateTelemetry(latestAccel);
#endif
        bleLoop();
        
        // Paced BLE telemetry notifications (Every 50ms: 5 ticks of 10ms)
        // Prevents BLE buffer congestion and reduces 2.4GHz RF contention with Wi-Fi
        if (++bleNotifyCounter >= 5) {
            bleNotifyCounter = 0;
            bleNotifyTelemetry(
                MajnSafety::getSystemState(systemActive),
                MajnSafety::isSafetyLockTriggered(),
                MajnVibration::getTargetFrequency(),
                MajnVibration::getCurrentAmplitude(),
                latestAccel.x_g,
                latestAccel.y_g,
                latestAccel.z_g
            );
        }

        vTaskDelay(pdMS_TO_TICKS(10));
    }
}

// -------------------------------------------------------------------------
// ESP32 Main Setup & Orchestration
// -------------------------------------------------------------------------
void setup() {
    Serial.begin(115200);

    Serial.println("=========================================");
    Serial.println("  MAJN Smart Bassinet Firmware Initializing");
#if defined(MAJN_BLE_ONLY_TEST)
    Serial.println("  [MODE: BLE-ONLY TEST BENCH - HARDWARE SAFE]");
#else
    Serial.println("  [MODE: FULL HARDWARE BRING-UP]");
#endif
    Serial.println("=========================================");

    // 0. Initialize Common System Controller
    MajnSystemCtrl::init();

    // 1. Initialize Safety Layer (Lowest level gatekeeper)
    MajnSafety::initSafety();

#if defined(MAJN_WIFI_CONTROL)
    // Wi-Fi SoftAP & HTTP Server (Brought up FIRST so network is discoverable immediately)
    if (!MajnWiFi::initWiFiServer("MAJN-Bassinet", "majn-secure-2026")) {
        Serial.println("[FATAL] Wi-Fi SoftAP initialization failed.");
        MajnSafety::requestEmergencyStop();
        while (1);
    }
    Serial.println("[OK] Wi-Fi SoftAP & Web Server Initialized (SSID: MAJN-Bassinet, IP: 192.168.4.1).");
#endif

    // 2. Power Sequencing: BOOST_EN held LOW initially
    MajnPower::initPower();

    // 3. Sensor Layer (LSM6DSOX SPI or Virtual Baseline)
    if (!MajnImu::initImu()) {
        Serial.println("[WARN] IMU initialization failed or sensor not detected.");
    }

    // 4. Vibration Control & I2S Peripheral (Start clocks first)
    MajnVibration::initVibrationController();

    // 5. Power up 12V Boost Regulator and Settle only after clocks are stable
    MajnPower::enableBoost();

    // 6. Amplifier Layer (TAS5805M I2C & PDN - detects stable I2S clocks)
    if (!MajnAmplifier::initAmplifier()) {
        Serial.println("[WARN] Amplifier initialization failed! Disabling 12V Boost for safety.");
        MajnPower::disableBoost();
    } else {
        // Safe default: boot into Standby (Hi-Z), NOT Play state!
        MajnAmplifier::enterStandbyState();
        Serial.println("[OK] Amplifier initialized successfully and placed in STANDBY.");
    }

    // 7. BLE GATT Server (Starts advertising MAJN-Bassinet for Web Bluetooth & Automated BLE OTA)
    if (!initBleServer()) {
        Serial.println("[FATAL] BLE server initialization failed.");
        MajnSafety::requestEmergencyStop();
        while (1);
    }
    Serial.println("[OK] BLE GATT Server Initialized.");

    // -------------------------------------------------------------------------
    // Dual Core FreeRTOS Task Spawning
    // -------------------------------------------------------------------------
    xTaskCreatePinnedToCore(WiFiBTCommunicationTask, "CommTask", 4096, NULL, 1, &commTaskHandle, 0);
    xTaskCreatePinnedToCore(VibrationControlTask, "ControlTask", 4096, NULL, 4, &controlTaskHandle, 1);
    xTaskCreatePinnedToCore(AudioOutputTask, "AudioTask", 4096, NULL, 5, &audioTaskHandle, 1);

    // 8. Wireless OTA Engine (Disabled to prevent Wi-Fi/BLE coexist memory crash)
    // MajnOta::initOta();

    Serial.println("[OK] System Tasks Running. Ready for BLE Connection.");

    // -------------------------------------------------------------------------
    // 8. Explicit OTA Rollback Verification Gate
    // Executed ONLY after full hardware, safety layers, and tasks are alive.
    // -------------------------------------------------------------------------
    const esp_partition_t *runningPartition = esp_ota_get_running_partition();
    esp_ota_img_states_t otaState;
    if (runningPartition && esp_ota_get_state_partition(runningPartition, &otaState) == ESP_OK) {
        if (otaState == ESP_OTA_IMG_PENDING_VERIFY) {
            Serial.println("[OTA-Boot] Firmware booted in PENDING_VERIFY state. Running comprehensive health diagnostics...");
            
            bool tasksHealthy = (commTaskHandle != NULL && controlTaskHandle != NULL && audioTaskHandle != NULL);
            bool heapHealthy = (ESP.getFreeHeap() >= 30000);
            bool safetyHealthy = (!systemActive && !MajnSafety::isSafetyLockTriggered());
            
            if (tasksHealthy && heapHealthy && safetyHealthy) {
                esp_err_t err = esp_ota_mark_app_valid_cancel_rollback();
                Serial.printf("[OTA-Boot] Diagnostics PASSED (Heap: %u, Tasks: OK, Safety: OK). Marked app VALID (result: %s).\n",
                              ESP.getFreeHeap(), esp_err_to_name(err));
            } else {
                Serial.printf("[OTA-Boot] Diagnostics FAILED! (Heap: %u, Tasks: %s, Safety: %s). Initiating automatic rollback...\n",
                              ESP.getFreeHeap(), tasksHealthy ? "OK" : "FAIL", safetyHealthy ? "OK" : "LOCK");
                esp_err_t err = esp_ota_mark_app_invalid_rollback_and_reboot();
                Serial.printf("[OTA-Boot] Rollback trigger returned: %s\n", esp_err_to_name(err));
            }
        } else {
            Serial.printf("[OTA-Boot] Running partition '%s' is in state %d (not PENDING_VERIFY).\n",
                          runningPartition->label, otaState);
        }
    }
}

void loop() {
    vTaskDelay(pdMS_TO_TICKS(1000));
}
