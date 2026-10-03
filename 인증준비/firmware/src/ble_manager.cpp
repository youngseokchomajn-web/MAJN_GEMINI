#include "ble_manager.h"

#include <BLEDevice.h>
#include <BLEServer.h>
#include <BLEUtils.h>
#include <BLE2902.h>
#include <ArduinoJson.h>

extern volatile bool safetyLockTriggered;
extern volatile bool systemActive;
extern volatile float targetFrequency;
extern volatile float currentAmplitudeScale;
extern volatile float targetAmplitudeScale;
extern volatile unsigned long activeStateStartTime;
extern void requestSafeStop();
extern void requestEmergencyStop();
extern void setVibrationTarget(float frequencyHz, float amplitudeScale);
extern void setOutputVolume(uint8_t volume);
extern void setSoundPreset(const char* preset);
extern bool ampStandbyLatched;
extern MajnBle::SystemState getSystemState();

namespace {
BLEServer* gServer = nullptr;
BLECharacteristic* gCommand = nullptr;
BLECharacteristic* gTelemetry = nullptr;
BLECharacteristic* gEvent = nullptr;
volatile bool gConnected = false;
volatile uint32_t gLastClientActivity = 0;
uint32_t gLastTelemetry = 0;

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
    String out;
    serializeJson(doc, out);
    gEvent->setValue(out.c_str());
    gEvent->notify();
}

class ServerCallbacks : public BLEServerCallbacks {
    void onConnect(BLEServer*) override {
        gConnected = true;
        gLastClientActivity = millis();
        Serial.println("[BLE] Client connected.");
    }
    void onDisconnect(BLEServer* server) override {
        gConnected = false;
        Serial.println("[BLE] Client disconnected. Requesting safe stop.");
        requestSafeStop();
        server->startAdvertising();
    }
};

class CommandCallbacks : public BLECharacteristicCallbacks {
    void onWrite(BLECharacteristic* characteristic) override {
        gLastClientActivity = millis();
        std::string raw = characteristic->getValue();
        if (raw.empty()) return;

        JsonDocument doc;
        DeserializationError err = deserializeJson(doc, raw);
        if (err) {
            sendAck(-1, "UNKNOWN", "rejected", "FAULT");
            return;
        }

        int id = doc["id"] | -1;
        const char* cmd = doc["cmd"] | "";

        if (strcmp(cmd, "PING") == 0) {
            sendAck(id, cmd, "applied", stateName(getSystemState()));
            return;
        }
        if (strcmp(cmd, "STATUS") == 0) {
            sendAck(id, cmd, "applied", stateName(getSystemState()));
            return;
        }
        if (strcmp(cmd, "START") == 0) {
            if (safetyLockTriggered) {
                sendAck(id, cmd, "fault", "FAULT");
                return;
            }
            systemActive = true;
            activeStateStartTime = millis();
            if (doc.containsKey("frequency_hz")) {
                float f = doc["frequency_hz"];
                if (f >= 30.0f && f <= 65.0f) targetFrequency = f;
            }
            targetAmplitudeScale = constrain((float)(doc["amplitude"] | (targetAmplitudeScale > 0.05f ? targetAmplitudeScale : 0.2f)), 0.0f, 0.5f);
            sendAck(id, cmd, "applied", "RUNNING");
            return;
        }
        if (strcmp(cmd, "STOP") == 0) {
            requestSafeStop();
            sendAck(id, cmd, "applied", "READY");
            return;
        }
        if (strcmp(cmd, "ESTOP") == 0) {
            requestEmergencyStop();
            sendAck(id, cmd, "applied", "FAULT");
            return;
        }
        if (strcmp(cmd, "SET_VIBRATION") == 0) {
            float f = doc["frequency_hz"] | targetFrequency;
            float a = doc["amplitude"] | targetAmplitudeScale;
            if (f < 30.0f || f > 65.0f || a < 0.0f || a > 0.5f) {
                sendAck(id, cmd, "rejected", stateName(getSystemState()));
                return;
            }
            setVibrationTarget(f, a);
            sendAck(id, cmd, "applied", stateName(getSystemState()));
            return;
        }
        if (strcmp(cmd, "SET_FREQUENCY") == 0) {
            float f = doc["frequency_hz"] | targetFrequency;
            if (f < 30.0f || f > 65.0f) {
                sendAck(id, cmd, "rejected", stateName(getSystemState()));
                return;
            }
            setVibrationTarget(f, targetAmplitudeScale);
            sendAck(id, cmd, "applied", stateName(getSystemState()));
            return;
        }
        if (strcmp(cmd, "SET_AMPLITUDE") == 0) {
            float a = doc["amplitude"] | targetAmplitudeScale;
            if (a < 0.0f || a > 0.5f) {
                sendAck(id, cmd, "rejected", stateName(getSystemState()));
                return;
            }
            setVibrationTarget(targetFrequency, a);
            sendAck(id, cmd, "applied", stateName(getSystemState()));
            return;
        }
        if (strcmp(cmd, "SET_VOLUME") == 0) {
            uint8_t v = doc["volume"] | 0;
            if (v > 100) {
                sendAck(id, cmd, "rejected", stateName(getSystemState()));
                return;
            }
            setOutputVolume(v);
            sendAck(id, cmd, "applied", stateName(getSystemState()));
            return;
        }
        if (strcmp(cmd, "SET_PRESET") == 0) {
            const char* p = doc["preset"] | "pink";
            setSoundPreset(p);
            sendAck(id, cmd, "applied", stateName(getSystemState()));
            return;
        }

        sendAck(id, cmd, "rejected", stateName(getSystemState()));
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
    BLEAdvertising* advertising = BLEDevice::getAdvertising();
    advertising->addServiceUUID(MajnBle::SERVICE_UUID);
    advertising->setScanResponse(true);
    advertising->start();

    Serial.println("[BLE] Advertising as MAJN-Bassinet.");
    return true;
}

bool bleClientConnected() {
    return gConnected;
}

void bleRegisterHeartbeat() {
    if (gConnected) gLastClientActivity = millis();
}

void bleLoop() {
    if (gConnected && millis() - gLastClientActivity > MajnBle::HEARTBEAT_TIMEOUT_MS) {
        Serial.println("[BLE] Heartbeat timeout. Safe stop.");
        requestSafeStop();
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
    doc["firmware"] = "0.2.0-ble";
    doc["uptime_ms"] = millis();
    doc["state"] = stateName(state);
    doc["safety_lock"] = safetyLock;
    doc["frequency_hz"] = frequencyHz;
    doc["amplitude_scale"] = amplitudeScale;
    JsonObject acc = doc["accel_g"].to<JsonObject>();
    acc["x"] = ax;
    acc["y"] = ay;
    acc["z"] = az;
    doc["pvdd_v"] = nullptr;
    doc["vdd_3v3_v"] = nullptr;
    doc["amp_temp_c"] = nullptr;

    String out;
    serializeJson(doc, out);
    gTelemetry->setValue(out.c_str());
    gTelemetry->notify();
}
