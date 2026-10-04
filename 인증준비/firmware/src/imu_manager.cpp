#include "imu_manager.h"
#include <SPI.h>
#include "safety_manager.h"

namespace {
LSM6DSOX gAccel(PIN_SPI_CS_XL);
bool gImuReady = false;
}

namespace MajnImu {

bool initImu() {
    pinMode(PIN_SAFETY_INT1, INPUT);
    gImuReady = false;

#if defined(MAJN_BLE_ONLY_TEST)
    Serial.println("[IMU] BLE-only test mode: LSM6DSOX bypassed (Virtual Baseline Active).");
    return true;
#else
    SPI.begin(PIN_SPI_SCLK, PIN_SPI_MISO, PIN_SPI_MOSI, PIN_SPI_CS_XL);
    if (!gAccel.begin()) {
        Serial.println("[WARN] LSM6DSOX sensor not detected over SPI.");
        return false;
    }

    gAccel.configureSafetyInterrupt(1.5f, 20);
    attachInterrupt(digitalPinToInterrupt(PIN_SAFETY_INT1), MajnSafety::safetyLockISR, RISING);
    gImuReady = true;
    Serial.println("[IMU] LSM6DSOX Initialized over SPI with 1.5g Hardware Interrupt.");
    return true;
#endif
}

bool readAcceleration(AccelData &data) {
#if defined(MAJN_BLE_ONLY_TEST)
    data.x_g = 0.0f;
    data.y_g = 0.0f;
    data.z_g = 1.0f; // 1g static baseline
    return true;
#else
    if (gImuReady) {
        return gAccel.readAccel(data);
    }
    data.x_g = 0.0f;
    data.y_g = 0.0f;
    data.z_g = 1.0f;
    return false;
#endif
}

bool isImuReady() {
    return gImuReady;
}

}
