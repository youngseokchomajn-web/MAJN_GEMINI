#include "vibration_controller.h"
#include "driver/i2s.h"
#include "pid_control.h"
#include "safety_manager.h"
#include "amplifier_manager.h"

namespace {
constexpr size_t LUT_SIZE = 1024;
constexpr int SAMPLE_RATE = 48000; // 48kHz standard rate for TAS5805M auto-clock detection
int16_t gSineLut[LUT_SIZE];

volatile float gTargetFrequency = 45.0f;
volatile float gCurrentAmplitude = 0.0f;
volatile float gTargetAmplitude = 0.0f;
const float RAMP_STEP_20MS = 0.005f;

PIDController gPid(0.01f, 0.002f, 0.0005f, 12.0f);
bool gI2sReady = false;
float gLutPhase = 0.0f;
}

extern volatile bool systemActive;

namespace MajnVibration {

void initVibrationController() {
    // Generate Sine Wave LUT
    for (size_t i = 0; i < LUT_SIZE; i++) {
        gSineLut[i] = (int16_t)(sin(2.0f * PI * (float)i / (float)LUT_SIZE) * 32767.0f);
    }
    gPid.setOutputLimits(-1.0f, 1.0f);

#if defined(MAJN_BLE_ONLY_TEST)
    Serial.println("[Vibration] BLE-only test mode: I2S peripheral disabled.");
    gI2sReady = false;
#else
    i2s_config_t i2s_config = {
        .mode = (i2s_mode_t)(I2S_MODE_MASTER | I2S_MODE_TX),
        .sample_rate = SAMPLE_RATE,
        .bits_per_sample = I2S_BITS_PER_SAMPLE_16BIT,
        .channel_format = I2S_CHANNEL_FMT_RIGHT_LEFT,
        .communication_format = I2S_COMM_FORMAT_STAND_I2S,
        .intr_alloc_flags = ESP_INTR_FLAG_LEVEL1,
        .dma_buf_count = 4,
        .dma_buf_len = 512,
        .use_apll = false,
        .tx_desc_auto_clear = true
    };
    
    i2s_pin_config_t pin_config = {
        .bck_io_num = PIN_I2S_BCLK,
        .ws_io_num = PIN_I2S_LRCLK,
        .data_out_num = PIN_I2S_DOUT,
        .data_in_num = I2S_PIN_NO_CHANGE
    };
    
    if (i2s_driver_install(I2S_NUM_0, &i2s_config, 0, NULL) == ESP_OK &&
        i2s_set_pin(I2S_NUM_0, &pin_config) == ESP_OK) {
        gI2sReady = true;
        Serial.println("[Vibration] I2S 48kHz driver configured (TAS5805M compliant).");
    } else {
        Serial.println("[WARN] I2S driver failed to configure.");
        gI2sReady = false;
    }
#endif
}

void setTarget(float frequencyHz, float amplitudeScale) {
    gTargetFrequency = constrain(frequencyHz, 30.0f, 65.0f);
    gTargetAmplitude = constrain(amplitudeScale, 0.0f, 0.5f);
}

float getTargetFrequency() {
    return gTargetFrequency;
}

float getCurrentAmplitude() {
    return gCurrentAmplitude;
}

float getTargetAmplitude() {
    return gTargetAmplitude;
}

void tickControlLoop(float dt) {
    if (MajnSafety::isSafetyLockTriggered()) {
        gCurrentAmplitude = 0.0f;
        gTargetAmplitude = 0.0f;
        return;
    }

    // Soft Start / Stop Ramping
    if (systemActive) {
        if (gCurrentAmplitude < gTargetAmplitude) {
            gCurrentAmplitude += RAMP_STEP_20MS;
            if (gCurrentAmplitude > gTargetAmplitude) gCurrentAmplitude = gTargetAmplitude;
        } else if (gCurrentAmplitude > gTargetAmplitude) {
            gCurrentAmplitude -= RAMP_STEP_20MS;
            if (gCurrentAmplitude < gTargetAmplitude) gCurrentAmplitude = gTargetAmplitude;
        }
    } else {
        if (gCurrentAmplitude > 0.0f) {
            gCurrentAmplitude -= RAMP_STEP_20MS;
            if (gCurrentAmplitude < 0.0f) gCurrentAmplitude = 0.0f;
        } else {
            MajnAmplifier::enterStandbyState();
        }
    }
}

void renderAudioBlock() {
#if !defined(MAJN_BLE_ONLY_TEST)
    if (!gI2sReady) {
        vTaskDelay(pdMS_TO_TICKS(50));
        return;
    }

    int16_t buffer[512];
    if (!systemActive || MajnSafety::isSafetyLockTriggered() || gCurrentAmplitude <= 0.001f) {
        memset(buffer, 0, sizeof(buffer));
        size_t bytes_written;
        i2s_write(I2S_NUM_0, buffer, sizeof(buffer), &bytes_written, portMAX_DELAY);
        vTaskDelay(pdMS_TO_TICKS(20));
        return;
    }

    float step = (gTargetFrequency * (float)LUT_SIZE) / (float)SAMPLE_RATE;
    for (int i = 0; i < 256; i++) {
        int index = (int)gLutPhase % LUT_SIZE;
        int16_t sample = (int16_t)((float)gSineLut[index] * gCurrentAmplitude);
        buffer[i * 2]     = sample;
        buffer[i * 2 + 1] = sample;
        gLutPhase += step;
        if (gLutPhase >= (float)LUT_SIZE) gLutPhase -= (float)LUT_SIZE;
    }

    size_t bytes_written;
    i2s_write(I2S_NUM_0, buffer, sizeof(buffer), &bytes_written, portMAX_DELAY);
#else
    vTaskDelay(pdMS_TO_TICKS(100));
#endif
}

}
