#include "ble_manager.h"

#include <BLEDevice.h>
#include <BLEServer.h>
#include <BLEUtils.h>
#include <BLE2902.h>
#include <ArduinoJson.h>
#include "soc/rtc_cntl_reg.h"

#include "safety_manager.h"
#include "power_manager.h"
#include "amplifier_manager.h"
#include "vibration_controller.h"
#include "system_controller.h"
#include "ota_ble_service.h"

extern volatile bool systemActive;
extern volatile unsigned long activeStateStartTime;

namespace {
BLEServer* gServer = nullptr;
BLECharacteristic* gCommand = nullptr;
BLECharacteristic* gTelemetry = nullptr;
BLECharacteristic* gEvent = nullptr;
volatile bool gConnected = false;
volatile uint32_t gLastClientActivity = 0;
uint32_t gLastTelemetry = 0;
char gCurrentPreset[16] = "pink";

const char* stateName(MajnBle::SystemState state) {
    switch (state) {
        case MajnBle::SystemState::BOOT: return "BOOT";
        case MajnBle::SystemState::SELF_TEST: return "SELF_TEST";
        case MajnBle::SystemState::READY: return "READY";
        case MajnBle::SystemState::RUNNING: return "RUNNING";
        case MajnBle::SystemState::FAULT: return "FAULT";
    }
    return "FAULT";
}

void sendAck(int id, const char* cmd, const char* status, const char* state) {
    if (!gConnected || !gEvent) return;
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

    String out;
    serializeJson(doc, out);
    gEvent->setValue(out.c_str());
    gEvent->notify();
}

class ServerCallbacks : public BLEServerCallbacks {
    void onConnect(BLEServer*) override {
        gConnected = true;
        gLastClientActivity = millis();
        MajnSystemCtrl::noteClientActivity();
        Serial.println("[BLE] Client connected.");
    }
    void onDisconnect(BLEServer* server) override {
        gConnected = false;
        Serial.println("[BLE] Client disconnected. Requesting safe stop.");
        MajnSystemCtrl::triggerSafeStop();
        server->startAdvertising();
    }
};

class CommandCallbacks : public BLECharacteristicCallbacks {
    void onWrite(BLECharacteristic* characteristic) override {
        gLastClientActivity = millis();
        MajnSystemCtrl::noteClientActivity();
        String raw = characteristic->getValue();
        if (raw.length() == 0) return;

        // Reject active vibration/hardware commands during wireless OTA update
        if (MajnBleOta::isOtaInProgress()) {
            JsonDocument doc;
            DeserializationError err = deserializeJson(doc, raw.c_str());
            const char* cmd = doc["cmd"] | "";
            if (strcmp(cmd, "PING") != 0 && strcmp(cmd, "STATUS") != 0) {
                int id = doc["id"] | -1;
                sendAck(id, cmd, "rejected", "OTA_ACTIVE");
                return;
            }
        }

        // Delegate entire command execution, range validation, amplifier sequencing, and ACK to Unified Command Manager
        String responseJson;
        MajnSystemCtrl::handleJsonCommand(raw.c_str(), responseJson);

        if (gConnected && gEvent && responseJson.length() > 0) {
            gEvent->setValue(responseJson.c_str());
            gEvent->notify();
        }
    }
};
}

bool initBleServer() {
    BLEDevice::init("MAJN-Bassinet");
    gServer = BLEDevice::createServer();
    gServer->setCallbacks(new ServerCallbacks());

    BLEService* service = gServer->createService(MajnBle::SERVICE_UUID);
    gCommand = service->createCharacteristic(
        MajnBle::COMMAND_UUID,
        BLECharacteristic::PROPERTY_WRITE | BLECharacteristic::PROPERTY_WRITE_NR
    );
    gTelemetry = service->createCharacteristic(
        MajnBle::TELEMETRY_UUID,
        BLECharacteristic::PROPERTY_READ | BLECharacteristic::PROPERTY_NOTIFY
    );
    gEvent = service->createCharacteristic(
        MajnBle::EVENT_UUID,
        BLECharacteristic::PROPERTY_NOTIFY
    );

    gTelemetry->addDescriptor(new BLE2902());
    gEvent->addDescriptor(new BLE2902());
    gCommand->setCallbacks(new CommandCallbacks());

    service->start();

    // Initialize Web Bluetooth Wireless OTA GATT Service
    MajnBleOta::initBleOta(gServer);

    BLEAdvertising* advertising = BLEDevice::getAdvertising();
    advertising->addServiceUUID(MajnBle::SERVICE_UUID);
    advertising->addServiceUUID(OTA_SERVICE_UUID);
    advertising->setScanResponse(true);
    advertising->setMinPreferred(0x06); // Helper for fast iOS connection (7.5ms)
    advertising->setMinPreferred(0x12); // Helper for iOS max interval (22.5ms)
    advertising->start();

    Serial.println("[BLE] Advertising as MAJN-Bassinet with Wireless OTA Service.");
    return true;
}

bool bleClientConnected() {
    return gConnected;
}

void bleRegisterHeartbeat() {
    if (gConnected) {
        gLastClientActivity = millis();
        MajnSystemCtrl::noteClientActivity();
    }
}

void bleLoop() {
    if (gConnected && millis() - gLastClientActivity > MajnBle::HEARTBEAT_TIMEOUT_MS) {
        Serial.println("[BLE] Heartbeat timeout (5s). Requesting safe stop.");
        MajnSystemCtrl::triggerSafeStop();
        gLastClientActivity = millis();
    }
}

void bleNotifyTelemetry(
    MajnBle::SystemState state,
    bool safetyLock,
    float frequencyHz,
    float amplitudeScale,
    float ax,
    float ay,
    float az
) {
    if (!gConnected || !gTelemetry) return;
    if (millis() - gLastTelemetry < MajnBle::TELEMETRY_PERIOD_MS) return;
    gLastTelemetry = millis();

    JsonDocument doc;
    doc["type"] = "telemetry";
    doc["protocol"] = MajnBle::PROTOCOL_VERSION;
    doc["firmware"] = "v1.2-wireless";
    doc["uptime_ms"] = millis();
    doc["state"] = stateName(state);
    doc["safety_lock"] = safetyLock;
    doc["frequency_hz"] = frequencyHz;
    doc["amplitude_scale"] = amplitudeScale;
    doc["duration_min"] = MajnSystemCtrl::getRunningDurationMinutes();
    doc["remaining_sec"] = MajnSystemCtrl::getRemainingSeconds();
    doc["amp_ready"] = MajnAmplifier::isAmplifierReady();
    doc["amp_status"] = MajnAmplifier::getStatusString();

    String out;
    serializeJson(doc, out);
    gTelemetry->setValue(out.c_str());
    gTelemetry->notify();
}
