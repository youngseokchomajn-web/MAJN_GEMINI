#include "ble_manager.h"

#include <BLEDevice.h>
#include <BLEServer.h>
#include <BLEUtils.h>
#include <BLE2902.h>
#include <BLESecurity.h>
#include <Preferences.h>
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
uint32_t gBlePin = 123456;

const char* stateName(MajnBle::SystemState state) {
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

        // Delegate entire command execution, range validation, amplifier sequencing, OTA locking, and ACK to Unified Command Manager
        String responseJson;
        MajnSystemCtrl::handleJsonCommand(raw.c_str(), responseJson);

        if (gConnected && gEvent && responseJson.length() > 0) {
            gEvent->setValue(responseJson.c_str());
            gEvent->notify();
        }
    }
};

class SecurityCallbacks : public BLESecurityCallbacks {
    uint32_t onPassKeyRequest() override {
        return gBlePin;
    }
    void onPassKeyNotify(uint32_t pass_key) override {
        Serial.printf("[BLE-SEC] Passkey display notification: %06u\n", pass_key);
    }
    bool onSecurityRequest() override {
        return true;
    }
    bool onConfirmPIN(uint32_t pin) override {
        return pin == gBlePin;
    }
    void onAuthenticationComplete(esp_ble_auth_cmpl_t desc) override {
        if (desc.success) {
            Serial.println("[BLE-SEC] Pairing & Bonding complete successfully!");
        } else {
            Serial.printf("[BLE-SEC] Authentication failed! Reason: 0x%02X\n", desc.fail_reason);
        }
    }
};
}

bool initBleServer() {
    // 1. Retrieve or generate persistent 6-digit BLE PIN in NVS
    Preferences prefs;
    prefs.begin("majn", false);
    uint32_t pin = prefs.getUInt("ble_pin", 0);
    if (pin < 100000 || pin > 999999) {
        pin = 100000 + (esp_random() % 900000);
        prefs.putUInt("ble_pin", pin);
        Serial.println("**************************************************");
        Serial.printf("[SECURITY] Generated NEW BLE 6-Digit Passkey PIN: %06u\n", pin);
        Serial.println("**************************************************");
    } else {
        Serial.println("[BLE] Loaded BLE Passkey PIN from NVS.");
    }
    prefs.end();
    gBlePin = pin;

    // 2. Initialize BLE Device
    BLEDevice::init("MAJN-Bassinet");

    // 3. Configure MITM passkey entry & bonding
    BLESecurity *pSecurity = new BLESecurity();
    pSecurity->setPassKey(true, gBlePin);
    pSecurity->setCapability(ESP_IO_CAP_OUT);
    pSecurity->setAuthenticationMode(true, true, true);
    BLESecurity::setEncryptionLevel(ESP_BLE_SEC_ENCRYPT_MITM);
    BLEDevice::setSecurityCallbacks(new SecurityCallbacks());

    gServer = BLEDevice::createServer();
    gServer->setCallbacks(new ServerCallbacks());

    // 4. Create GATT service & characteristics with MITM encrypted read/write permissions
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

    gCommand->setAccessPermissions(ESP_GATT_PERM_READ_ENC_MITM | ESP_GATT_PERM_WRITE_ENC_MITM);
    gTelemetry->setAccessPermissions(ESP_GATT_PERM_READ_ENC_MITM | ESP_GATT_PERM_WRITE_ENC_MITM);
    gEvent->setAccessPermissions(ESP_GATT_PERM_READ_ENC_MITM | ESP_GATT_PERM_WRITE_ENC_MITM);

    gTelemetry->addDescriptor(new BLE2902());
    gEvent->addDescriptor(new BLE2902());
    gCommand->setCallbacks(new CommandCallbacks());

    service->start();

    // 5. Initialize Web Bluetooth Wireless OTA GATT Service (also protected by MITM)
    MajnBleOta::initBleOta(gServer);

    // 6. Start Advertising
    BLEAdvertising* advertising = BLEDevice::getAdvertising();
    advertising->addServiceUUID(MajnBle::SERVICE_UUID);
    advertising->addServiceUUID(OTA_SERVICE_UUID);
    advertising->setScanResponse(true);
    advertising->setMinPreferred(0x06); // Helper for fast iOS connection (7.5ms)
    advertising->setMaxPreferred(0x12); // Helper for iOS max interval (22.5ms)
    advertising->start();

    Serial.println("[BLE] Advertising as MAJN-Bassinet with MITM Encryption & Passkey Security.");
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
    if (gConnected && MajnSystemCtrl::isSystemActive() && 
        (millis() - MajnSystemCtrl::getLastClientActivity() > MajnBle::HEARTBEAT_TIMEOUT_MS)) {
        Serial.println("[BLE] Client activity timeout (5s) while RUNNING. Safe Stop triggered.");
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
