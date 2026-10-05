#include "ota_ble_service.h"
#include <Update.h>
#include <ArduinoJson.h>
#include "safety_manager.h"

namespace {
BLECharacteristic* gOtaControl = nullptr;
BLECharacteristic* gOtaData = nullptr;

bool gOtaRunning = false;
size_t gTotalBytesExpected = 0;
size_t gBytesReceived = 0;
uint32_t gLastProgressNotify = 0;

void notifyOtaStatus(const char* status, int progressPercent, const char* errorMsg = nullptr) {
    if (!gOtaControl) return;
    JsonDocument doc;
    doc["type"] = "ota_status";
    doc["status"] = status;
    doc["progress"] = progressPercent;
    if (errorMsg) {
        doc["error"] = errorMsg;
    }
    String out;
    serializeJson(doc, out);
    gOtaControl->setValue(out.c_str());
    gOtaControl->notify();
}

class OtaControlCallbacks : public BLECharacteristicCallbacks {
    void onWrite(BLECharacteristic* characteristic) override {
        String val = characteristic->getValue();
        if (val.length() == 0) return;

        JsonDocument doc;
        DeserializationError err = deserializeJson(doc, val.c_str());
        if (err) {
            notifyOtaStatus("error", 0, "JSON parse error");
            return;
        }

        const char* cmd = doc["cmd"] | "";

        if (strcmp(cmd, "OTA_BEGIN") == 0) {
            size_t fwSize = doc["size"] | 0;
            if (fwSize == 0) {
                notifyOtaStatus("error", 0, "Invalid firmware size");
                return;
            }

            Serial.printf("[BLE-OTA] Starting OTA transfer. Size: %u bytes\n", fwSize);
            MajnSafety::requestSafeStop(); // Ensure motor/amp is stopped

            if (!Update.begin(fwSize, U_FLASH)) {
                Serial.printf("[BLE-OTA] Update.begin failed. Error: %d\n", Update.getError());
                notifyOtaStatus("error", 0, "Update.begin failed");
                return;
            }

            gOtaRunning = true;
            gTotalBytesExpected = fwSize;
            gBytesReceived = 0;
            notifyOtaStatus("ready", 0);
            return;
        }

        if (strcmp(cmd, "OTA_END") == 0) {
            if (!gOtaRunning) return;

            Serial.printf("[BLE-OTA] Finishing OTA transfer. Total: %u bytes\n", gBytesReceived);
            if (Update.end(true)) {
                if (Update.isFinished()) {
                    Serial.println("[BLE-OTA] Update SUCCESS! Rebooting in 500ms...");
                    notifyOtaStatus("success", 100);
                    vTaskDelay(pdMS_TO_TICKS(500));
                    ESP.restart();
                    return;
                } else {
                    Serial.println("[BLE-OTA] Update not finished properly.");
                    notifyOtaStatus("error", 0, "Update incomplete");
                }
            } else {
                Serial.printf("[BLE-OTA] Update.end failed. Error: %d\n", Update.getError());
                notifyOtaStatus("error", 0, "Update.end failed");
            }
            gOtaRunning = false;
            return;
        }

        if (strcmp(cmd, "OTA_ABORT") == 0) {
            Serial.println("[BLE-OTA] Update aborted by client.");
            Update.abort();
            gOtaRunning = false;
            notifyOtaStatus("aborted", 0);
            return;
        }
    }
};

class OtaDataCallbacks : public BLECharacteristicCallbacks {
    void onWrite(BLECharacteristic* characteristic) override {
        if (!gOtaRunning) return;

        uint8_t* data = characteristic->getData();
        size_t len = characteristic->getLength();

        if (len > 0 && data) {
            size_t written = Update.write(data, len);
            if (written != len) {
                Serial.printf("[BLE-OTA] Write error: expected %u, wrote %u\n", len, written);
                notifyOtaStatus("error", (int)((gBytesReceived * 100) / gTotalBytesExpected), "Write error");
                Update.abort();
                gOtaRunning = false;
                return;
            }

            gBytesReceived += written;

            // Notify progress every 5% or 500ms
            if (millis() - gLastProgressNotify > 300) {
                gLastProgressNotify = millis();
                int pct = (int)((gBytesReceived * 100) / gTotalBytesExpected);
                notifyOtaStatus("progress", pct);
            }
        }
    }
};

}

namespace MajnBleOta {

void initBleOta(BLEServer* server) {
    BLEService* otaService = server->createService(OTA_SERVICE_UUID);

    gOtaControl = otaService->createCharacteristic(
        OTA_CONTROL_UUID,
        BLECharacteristic::PROPERTY_WRITE | BLECharacteristic::PROPERTY_NOTIFY
    );
    gOtaControl->addDescriptor(new BLE2902());
    gOtaControl->setCallbacks(new OtaControlCallbacks());

    gOtaData = otaService->createCharacteristic(
        OTA_DATA_UUID,
        BLECharacteristic::PROPERTY_WRITE | BLECharacteristic::PROPERTY_WRITE_NR
    );
    gOtaData->setCallbacks(new OtaDataCallbacks());

    otaService->start();
    Serial.println("[BLE-OTA] Web Bluetooth OTA Service ready.");
}

bool isOtaInProgress() {
    return gOtaRunning;
}

}
