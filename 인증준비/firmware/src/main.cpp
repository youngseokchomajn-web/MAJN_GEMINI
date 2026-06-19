#include <Arduino.h>
#include <SPI.h>
#include <Wire.h>
#include "driver/i2s.h"
#include "tas5805m.h"
#include "lsm6dsox.h"
#include "pid_control.h"

// -------------------------------------------------------------------------
// Hardware Pin Mappings (Based on PCB Design & Spec v1.1)
// -------------------------------------------------------------------------
#define PIN_SPI_CS_XL       5   // LSM6DSOX SPI CS
#define PIN_SPI_MOSI        23  // VSPI MOSI
#define PIN_SPI_MISO        19  // VSPI MISO
#define PIN_SPI_SCLK        18  // VSPI SCLK

#define PIN_I2C_SDA         21  // I2C SDA
#define PIN_I2C_SCL         27  // I2C SCL (Matched to GPIO27 in design json)

#define PIN_BOOST_EN        4   // MP3426 Boost Converter Enable Pin (Active High)
#define PIN_SAFETY_INT1     34  // LSM6DSOX INT1 (input-only GPIO34, no internal pull)
#define PIN_AMP_PDN         15  // TAS5805M PDN# (active-low: HIGH=enable, LOW=shutdown/mute)

// I2S Pins for TI TAS5805M Digital Audio Input
#define PIN_I2S_BCLK        26  // I2S Bit Clock (GPIO26)
#define PIN_I2S_LRCLK       25  // I2S Frame Clock (GPIO25)
#define PIN_I2S_DOUT        22  // I2S Data Out (GPIO22, mapped to SDIN on U4)

#define I2S_NUM             I2S_NUM_0
#define SAMPLE_RATE         16000   // 16kHz sampling rate for smooth low-frequency vibration
#define LUT_SIZE            1024

// -------------------------------------------------------------------------
// Global Variables & Control Structures
// -------------------------------------------------------------------------
TAS5805M amp;
LSM6DSOX accel(PIN_SPI_CS_XL);
// Target amplitude in displacement micrometers: default 12.0 um (Safety spec target 10~12 um)
PIDController pid(0.01f, 0.002f, 0.0005f, 12.0f); 

volatile bool safetyLockTriggered = false;
volatile bool systemActive = true;

// Vibration wave state
volatile float targetFrequency = 45.0f; // Target vibration frequency (30~65Hz)
volatile float currentAmplitudeScale = 0.0f; // 0.0f (Mute) to 1.0f (Full output)
volatile float targetAmplitudeScale = 0.5f;  // Soft-start target amplitude scaling factor

// Soft Start/Stop config
const float RAMP_STEP_20MS = 0.005f; // Ramping rate (approx. 2 seconds to full scale)

// Safety Constraints (KC Infant Safety Standard)
const unsigned long MAX_RUNNING_TIME_MS = 30 * 60 * 1000; // 30 minutes automatic shutdown
unsigned long activeStateStartTime = 0;

// Sine wave Lookup Table for fast real-time wave synthesis
int16_t sineLut[LUT_SIZE];

// FreeRTOS Tasks
TaskHandle_t commTaskHandle = NULL;
TaskHandle_t controlTaskHandle = NULL;
TaskHandle_t audioTaskHandle = NULL;

// -------------------------------------------------------------------------
// ISR: Critical Hardware Emergency Safety Shutdown
// -------------------------------------------------------------------------
void IRAM_ATTR safetyLockISR() {
    safetyLockTriggered = true;
    systemActive = false;
    
    // HARDWARE SHUTDOWN: Immediately disable MP3426 12V Boost Regulator to cut PVDD power to TAS5805M.
    digitalWrite(PIN_BOOST_EN, LOW);
    // Also assert TAS5805M PDN# low to mute the amplifier instantly (belt-and-suspenders).
    digitalWrite(PIN_AMP_PDN, LOW);
}

// -------------------------------------------------------------------------
// Look-Up Table Init
// -------------------------------------------------------------------------
void initSineLut() {
    for (int i = 0; i < LUT_SIZE; i++) {
        sineLut[i] = (int16_t)(sin(2.0f * PI * (float)i / (float)LUT_SIZE) * 32767.0f);
    }
}

// -------------------------------------------------------------------------
// ESP32 I2S Peripheral Setup
// -------------------------------------------------------------------------
bool initI2S() {
    i2s_config_t i2s_config = {
        .mode = (i2s_mode_t)(I2S_MODE_MASTER | I2S_MODE_TX),
        .sample_rate = SAMPLE_RATE,
        .bits_per_sample = I2S_BITS_PER_SAMPLE_16BIT,
        .channel_format = I2S_CHANNEL_FMT_RIGHT_LEFT, // Stereo
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
    
    if (i2s_driver_install(I2S_NUM, &i2s_config, 0, NULL) != ESP_OK) {
        return false;
    }
    if (i2s_set_pin(I2S_NUM, &pin_config) != ESP_OK) {
        return false;
    }
    return true;
}

// -------------------------------------------------------------------------
// Core 1 Task: Real-time I2S Audio Sine Synthesis (Samples generated from LUT)
// -------------------------------------------------------------------------
void AudioOutputTask(void *pvParameters) {
    (void)pvParameters;
    int16_t buffer[512]; // DMA write block
    float lut_phase = 0.0f;
    
    Serial.println("[Core 1] I2S Audio Output Task Started.");
    
    for (;;) {
        if (!systemActive || safetyLockTriggered) {
            // Write silence to I2S
            memset(buffer, 0, sizeof(buffer));
            size_t bytes_written;
            i2s_write(I2S_NUM, buffer, sizeof(buffer), &bytes_written, portMAX_DELAY);
            vTaskDelay(pdMS_TO_TICKS(50));
            continue;
        }
        
        // Populate buffer with scaled sine wave
        float step = (targetFrequency * (float)LUT_SIZE) / (float)SAMPLE_RATE;
        
        for (int i = 0; i < 256; i++) { // 256 samples (Stereo = 512 int16_t elements)
            int index = (int)lut_phase % LUT_SIZE;
            int16_t sample = (int16_t)((float)sineLut[index] * currentAmplitudeScale);
            
            buffer[i * 2]     = sample; // Left
            buffer[i * 2 + 1] = sample; // Right
            
            lut_phase += step;
            if (lut_phase >= (float)LUT_SIZE) {
                lut_phase -= (float)LUT_SIZE;
            }
        }
        
        size_t bytes_written;
        i2s_write(I2S_NUM, buffer, sizeof(buffer), &bytes_written, portMAX_DELAY);
    }
}

// -------------------------------------------------------------------------
// Core 1 Task: Sensor Reading, Double Integration, PID & Safety Logic (50Hz)
// -------------------------------------------------------------------------
void VibrationControlTask(void *pvParameters) {
    (void)pvParameters;
    
    Serial.println("[Core 1] Real-time Vibration Control Task Started (50Hz).");
    
    TickType_t xLastWakeTime = xTaskGetTickCount();
    const TickType_t xFrequency = pdMS_TO_TICKS(20); // 20ms delta time (50Hz)
    
    AccelData accelData;
    float dt = 0.02f;
    
    // Leaky integrators for double integration
    float accel_dc = 0.0f;
    float vel = 0.0f;
    float disp = 0.0f;
    float measured_amplitude_um = 0.0f;
    float disp_envelope = 0.0f;
    
    activeStateStartTime = millis();
    
    for (;;) {
        vTaskDelayUntil(&xLastWakeTime, xFrequency);
        
        if (safetyLockTriggered) {
            continue;
        }
        
        // 1. Safe Time Limit Check (30 mins automatic cut-off)
        if (millis() - activeStateStartTime > MAX_RUNNING_TIME_MS) {
            Serial.println("[Safety] 30 minutes run-time exceeded. Initiating Soft Stop.");
            systemActive = false;
        }
        
        // 2. Soft Start / Soft Stop Ramping
        if (systemActive) {
            if (currentAmplitudeScale < targetAmplitudeScale) {
                currentAmplitudeScale += RAMP_STEP_20MS;
                if (currentAmplitudeScale > targetAmplitudeScale) currentAmplitudeScale = targetAmplitudeScale;
            } else if (currentAmplitudeScale > targetAmplitudeScale) {
                currentAmplitudeScale -= RAMP_STEP_20MS;
                if (currentAmplitudeScale < targetAmplitudeScale) currentAmplitudeScale = targetAmplitudeScale;
            }
        } else {
            // Ramp down to zero (Soft Stop)
            if (currentAmplitudeScale > 0.0f) {
                currentAmplitudeScale -= RAMP_STEP_20MS;
                if (currentAmplitudeScale < 0.0f) currentAmplitudeScale = 0.0f;
            } else {
                // Completely ramped down, enter Standby State
                amp.enterStandbyState();
            }
        }
        
        // 3. Read Accel sensor data over SPI (fast 10MHz bus)
        if (accel.readAccel(accelData)) {
            // Double integration to displacement (Z-axis only for micro-vibrations)
            // Remove DC gravity offset using exponential moving average (EMA)
            accel_dc = 0.995f * accel_dc + 0.005f * accelData.z_g;
            float accel_ac_g = accelData.z_g - accel_dc;
            float accel_m_s2 = accel_ac_g * 9.80665f;
            
            // Leaky integration to velocity (m/s)
            vel = 0.99f * vel + accel_m_s2 * dt;
            
            // Leaky integration to displacement (m)
            disp = 0.99f * disp + vel * dt;
            
            // Convert to micrometers
            float current_z_disp_um = disp * 1000000.0f;
            
            // Amplitude Envelope Detection (EMA of absolute value * pi/2)
            disp_envelope = 0.98f * disp_envelope + 0.02f * abs(current_z_disp_um);
            measured_amplitude_um = disp_envelope * 1.5708f;
            
            // 4. Compute PID output (only adjust target scale if system is active and running)
            if (systemActive && currentAmplitudeScale > 0.05f) {
                float pid_output = pid.compute(measured_amplitude_um, dt);
                
                // Adjust target scale slowly
                targetAmplitudeScale += pid_output * 0.01f;
                if (targetAmplitudeScale > 1.0f) targetAmplitudeScale = 1.0f;
                if (targetAmplitudeScale < 0.05f) targetAmplitudeScale = 0.05f;
            }
        }
    }
}

// -------------------------------------------------------------------------
// Core 0 Task: Wi-Fi, Bluetooth, & MLC Monitoring
// -------------------------------------------------------------------------
void WiFiBTCommunicationTask(void *pvParameters) {
    (void)pvParameters;
    Serial.println("[Core 0] Wi-Fi & BT Communication Task Started.");
    
    for (;;) {
        if (safetyLockTriggered) {
            Serial.println("[Core 0] Critical Shock Triggered! Safety Lock Active.");
            vTaskDelay(pdMS_TO_TICKS(1000));
            continue;
        }
        
        // Handle Wi-Fi, Cloud MQTT, & BLE SoC commands here
        vTaskDelay(pdMS_TO_TICKS(100));
    }
}

// -------------------------------------------------------------------------
// ESP32 Main Setup
// -------------------------------------------------------------------------
void setup() {
    Serial.begin(115200);
    while (!Serial);
    
    Serial.println("=========================================");
    Serial.println("  Majung Smart Bassinet Firmware Initializing... ");
    Serial.println("=========================================");
    
    // Configure safety shutdown pin
    pinMode(PIN_BOOST_EN, OUTPUT);
    digitalWrite(PIN_BOOST_EN, HIGH); // Enable MP3426 12V Boost Regulator

    // Release TAS5805M from shutdown (PDN# active-low; HIGH = enable). Must precede I2C/I2S init.
    pinMode(PIN_AMP_PDN, OUTPUT);
    digitalWrite(PIN_AMP_PDN, HIGH);
    delay(10);

    // GPIO34 is input-only and has NO internal pull resistor (ESP32 GPIO34-39).
    // LSM6DSOX INT1 is push-pull (actively driven), so plain INPUT is correct here.
    pinMode(PIN_SAFETY_INT1, INPUT);
    
    // Initialize Sine Wave Table
    initSineLut();
    
    // Initialize SPI for LSM6DSOX sensor
    SPI.begin(PIN_SPI_SCLK, PIN_SPI_MISO, PIN_SPI_MOSI, PIN_SPI_CS_XL);
    if (!accel.begin()) {
        Serial.println("[ERROR] LSM6DSOX Accelerometer Initialization Failed.");
        while (1);
    }
    Serial.println("[OK] LSM6DSOX Accelerometer Initialized via SPI.");
    
    // Initialize I2C for TAS5805M amplifier
    if (!amp.begin(PIN_I2C_SDA, PIN_I2C_SCL)) {
        Serial.println("[ERROR] TAS5805M Amplifier Initialization Failed.");
        while (1);
    }
    Serial.println("[OK] TAS5805M Amplifier Initialized via I2C.");
    
    // Initialize I2S Audio Driver
    if (!initI2S()) {
        Serial.println("[ERROR] I2S initialization failed.");
        while (1);
    }
    Serial.println("[OK] I2S Driver Configured for TAS5805M.");
    
    // Configure Safety Shock Interrupt (Trigger at 1.5g shock limit, latched)
    accel.configureSafetyInterrupt(1.5f, 20);
    
    // Enable TAS5805M to Play State
    amp.enterPlayState();
    
    // Initialize PID Controller output limits (-1.0 to 1.0 step adjustments)
    pid.setOutputLimits(-1.0f, 1.0f);
    
    // Attach Hardware Safety ISR (Interrupt triggers safetyLockISR immediately)
    attachInterrupt(digitalPinToInterrupt(PIN_SAFETY_INT1), safetyLockISR, RISING);
    Serial.println("[OK] Safety Lock Hardware ISR Attached to GPIO34.");
    
    // -------------------------------------------------------------------------
    // FreeRTOS Task Allocation
    // -------------------------------------------------------------------------
    // 1. Comm Task on Core 0
    xTaskCreatePinnedToCore(
        WiFiBTCommunicationTask,
        "CommTask",
        4096,
        NULL,
        1,
        &commTaskHandle,
        0
    );
    
    // 2. Control Task on Core 1 (High priority)
    xTaskCreatePinnedToCore(
        VibrationControlTask,
        "ControlTask",
        4096,
        NULL,
        4,
        &controlTaskHandle,
        1
    );
    
    // 3. I2S Audio Task on Core 1 (Real-time stream, highest priority)
    xTaskCreatePinnedToCore(
        AudioOutputTask,
        "AudioTask",
        4096,
        NULL,
        5,
        &audioTaskHandle,
        1
    );
    
    Serial.println("[OK] Dual Core Task Allocation Completed.");
}

void loop() {
    vTaskDelay(pdMS_TO_TICKS(1000));
}

