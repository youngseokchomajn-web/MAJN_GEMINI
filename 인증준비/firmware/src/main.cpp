#include <Arduino.h>

#include "ble_protocol.h"
#include "ble_manager.h"
#include "safety_manager.h"
#include "power_manager.h"
#include "amplifier_manager.h"
#include "imu_manager.h"
#include "vibration_controller.h"

// -------------------------------------------------------------------------
// Global Operational State & FreeRTOS Orchestration
// -------------------------------------------------------------------------
volatile bool systemActive = false;
volatile unsigned long activeStateStartTime = 0;
const unsigned long MAX_RUNNING_TIME_MS = 30 * 60 * 1000; // 30 minutes KC auto-stop

static AccelData latestAccel = {0, 0, 0, 0.0f, 0.0f, 1.0f};

TaskHandle_t commTaskHandle = NULL;
TaskHandle_t controlTaskHandle = NULL;
TaskHandle_t audioTaskHandle = NULL;

// -------------------------------------------------------------------------
// Hardware Emergency Shutdown Callback (Invoked by SafetyManager)
// -------------------------------------------------------------------------
void hardwareEmergencyShutdown() {
    MajnPower::disableBoost();
    MajnAmplifier::shutdownAmplifier();
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

    activeStateStartTime = millis();

    for (;;) {
        vTaskDelayUntil(&xLastWakeTime, xFrequency);

        if (MajnSafety::isSafetyLockTriggered()) {
            continue;
        }

        // Automatic run-time cutoff (KC infant safety standard: 30 minutes)
        if (systemActive && (millis() - activeStateStartTime > MAX_RUNNING_TIME_MS)) {
            Serial.println("[Safety] 30 minutes limit exceeded. Soft Stop engaged.");
            MajnSafety::requestSafeStop();
        }

        // Advance PID & Soft Start/Stop Ramping
        MajnVibration::tickControlLoop(dt);

        // Read accelerometer sensor
        MajnImu::readAcceleration(latestAccel);
    }
}

// -------------------------------------------------------------------------
// Core 0 Task: BLE Communication, Heartbeat Supervision & Telemetry
// -------------------------------------------------------------------------
void WiFiBTCommunicationTask(void *pvParameters) {
    (void)pvParameters;
    Serial.println("[Core 0] BLE Communication Task Running.");

    for (;;) {
        bleLoop();
        bleNotifyTelemetry(
            MajnSafety::getSystemState(systemActive),
            MajnSafety::isSafetyLockTriggered(),
            MajnVibration::getTargetFrequency(),
            MajnVibration::getCurrentAmplitude(),
            latestAccel.x_g,
            latestAccel.y_g,
            latestAccel.z_g
        );
        vTaskDelay(pdMS_TO_TICKS(20));
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

    // 1. Initialize Safety Layer (Lowest level gatekeeper)
    MajnSafety::initSafety();

    // 2. Power Sequencing: BOOST_EN held LOW initially
    MajnPower::initPower();

    // 3. Sensor Layer (LSM6DSOX SPI or Virtual Baseline)
    MajnImu::initImu();

    // 4. Power up 12V Boost Regulator and Settle
    MajnPower::enableBoost();

    // 5. Amplifier Layer (TAS5805M I2C & PDN)
    MajnAmplifier::initAmplifier();

    // 6. Vibration Control & I2S Peripheral
    MajnVibration::initVibrationController();

    // 7. BLE GATT Server (Starts advertising MAJN-Bassinet)
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

    Serial.println("[OK] System Tasks Running. Ready for BLE Connection.");
}

void loop() {
    vTaskDelay(pdMS_TO_TICKS(1000));
}
