#pragma once

#include <Arduino.h>
#include <BLEDevice.h>
#include <BLEServer.h>
#include <BLEUtils.h>
#include <BLE2902.h>

namespace MajnBleOta {

// Dedicated BLE OTA Service & Characteristic UUIDs
#define OTA_SERVICE_UUID      "00000004-6a6e-4d41-4a4e-000000000001"
#define OTA_CONTROL_UUID      "00000005-6a6e-4d41-4a4e-000000000001"
#define OTA_DATA_UUID         "00000006-6a6e-4d41-4a4e-000000000001"

void initBleOta(BLEServer* server);
bool isOtaInProgress();

}
