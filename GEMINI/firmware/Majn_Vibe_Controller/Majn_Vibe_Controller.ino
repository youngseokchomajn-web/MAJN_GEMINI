/*
  Majn Smart Bassinet - Vibration Control Firmware (Phase 1/2) - Sync Version
  Platform: ESP32 (Arduino IDE Compatible Single File)
  
  Features:
  - LSM6DSOX SPI Driver & TAS5805M I2C/I2S Driver Integration
  - FreeRTOS Task Allocation for audio synthesis (Core 1) and PID control loop (Core 1)
  - 1024-point Sine Lookup Table (LUT) for efficient digital audio stream
  - Hardware Safety Shock Interrupt (GPIO34) & 30-min Timeout limit
  - Soft-start & Soft-stop Volume Ramping
*/

#include <Arduino.h>
#include <SPI.h>
#include <Wire.h>
#include "driver/i2s.h"

// -------------------------------------------------------------------------
// Hardware Pin Mappings (Based on PCB Design & Spec v1.1)
// -------------------------------------------------------------------------
#define PIN_SPI_CS_XL       5   // LSM6DSOX SPI CS
#define PIN_SPI_MOSI        23  // VSPI MOSI
#define PIN_SPI_MISO        19  // VSPI MISO
#define PIN_SPI_SCLK        18  // VSPI SCLK

#define PIN_I2C_SDA         21  // I2C SDA
#define PIN_I2C_SCL         27  // I2C SCL (GPIO27)

#define PIN_BOOST_EN        4   // MP3426 Boost Converter Enable Pin (Active High)
#define PIN_SAFETY_INT1     34  // LSM6DSOX INT1 (RTC Interrupt Pin)

// I2S Pins for TI TAS5805M Digital Audio Input
#define PIN_I2S_BCLK        26  // I2S Bit Clock (GPIO26)
#define PIN_I2S_LRCLK       25  // I2S Frame Clock (GPIO25)
#define PIN_I2S_DOUT        22  // I2S Data Out (GPIO22, mapped to SDIN on U4)

#define I2S_NUM             I2S_NUM_0
#define SAMPLE_RATE         16000   // 16kHz sampling rate
#define LUT_SIZE            1024

// -------------------------------------------------------------------------
// [A] PID Controller Class Definition
// -------------------------------------------------------------------------
class PIDController {
public:
    PIDController(float kp, float ki, float kd, float target) 
        : _kp(kp), _ki(ki), _kd(kd), _target(target), _integral(0.0f), _prevError(0.0f), _minOut(0.0f), _maxOut(255.0f) {}
    
    void reset() {
        _integral = 0.0f;
        _prevError = 0.0f;
    }
    
    void setTunings(float kp, float ki, float kd) {
        _kp = kp;
        _ki = ki;
        _kd = kd;
    }
    
    void setTarget(float target) {
        _target = target;
    }
    
    void setOutputLimits(float minOut, float maxOut) {
        _minOut = minOut;
        _maxOut = maxOut;
    }
    
    float compute(float feedback, float dt) {
        if (dt <= 0.0f) return 0.0f;
        
        float error = _target - feedback;
        float pOut = _kp * error;
        
        _integral += error * dt;
        float iOut = _ki * _integral;
        
        if (iOut > _maxOut) {
            iOut = _maxOut;
            _integral = _maxOut / _ki;
        } else if (iOut < _minOut) {
            iOut = _minOut;
            _integral = _minOut / _ki;
        }
        
        float derivative = (error - _prevError) / dt;
        float dOut = _kd * derivative;
        _prevError = error;
        
        float totalOutput = pOut + iOut + dOut;
        if (totalOutput > _maxOut) {
            totalOutput = _maxOut;
        } else if (totalOutput < _minOut) {
            totalOutput = _minOut;
        }
        
        return totalOutput;
    }

private:
    float _kp;
    float _ki;
    float _kd;
    float _target;
    float _integral;
    float _prevError;
    float _minOut;
    float _maxOut;
};

// -------------------------------------------------------------------------
// [B] TAS5805M Class Definition
// -------------------------------------------------------------------------
#define TAS5805M_I2C_ADDR   0x2C
#define REG_DEVICE_CTRL_1   0x02
#define REG_DEVICE_CTRL_2   0x03
#define REG_SIG_CH_CTRL     0x28
#define REG_MASTER_VOL      0x4C
#define REG_ANALOG_GAIN     0x5C
#define REG_AGL_CTRL        0x60
#define REG_BOOK_SEL        0x7F

class TAS5805M {
public:
    TAS5805M(uint8_t i2cAddress = TAS5805M_I2C_ADDR) : _addr(i2cAddress) {}
    
    bool begin(int sdaPin, int sclPin) {
        Wire.begin(sdaPin, sclPin);
        
        Wire.beginTransmission(_addr);
        if (Wire.endTransmission() != 0) {
            return false;
        }
        
        if (!writeBookPage(0x00, 0x00)) return false;
        if (!writeRegister(REG_DEVICE_CTRL_2, 0x03)) return false; 
        if (!writeRegister(REG_DEVICE_CTRL_1, 0x00)) return false; 
        if (!setVolume(0x48)) return false; 
        if (!enableAGL(true)) return false;
        return true;
    }
    
    bool enterPlayState() {
        if (!writeBookPage(0x00, 0x00)) return false;
        return writeRegister(REG_DEVICE_CTRL_2, 0x02);
    }
    
    bool enterStandbyState() {
        if (!writeBookPage(0x00, 0x00)) return false;
        return writeRegister(REG_DEVICE_CTRL_2, 0x03);
    }
    
    bool setVolume(uint8_t volume) {
        if (!writeBookPage(0x00, 0x00)) return false;
        
        uint8_t safetyVolume = volume;
        if (safetyVolume > 0x48) {
            safetyVolume = 0x48; // Clamped to -12dB max limit
        }
        return writeRegister(REG_MASTER_VOL, safetyVolume);
    }
    
    bool enableAGL(bool enable) {
        if (!writeBookPage(0x00, 0x3C)) return false;
        if (enable) {
            if (!writeRegister(REG_AGL_CTRL, 0x01)) return false;
        } else {
            if (!writeRegister(REG_AGL_CTRL, 0x00)) return false;
        }
        return writeBookPage(0x00, 0x00);
    }

private:
    uint8_t _addr;
    
    bool writeRegister(uint8_t reg, uint8_t value) {
        Wire.beginTransmission(_addr);
        Wire.write(reg);
        Wire.write(value);
        return (Wire.endTransmission() == 0);
    }
    
    bool writeBookPage(uint8_t book, uint8_t page) {
        Wire.beginTransmission(_addr);
        Wire.write(REG_BOOK_SEL);
        Wire.write(book);
        if (Wire.endTransmission() != 0) return false;
        
        Wire.beginTransmission(_addr);
        Wire.write(0x00);
        Wire.write(page);
        return (Wire.endTransmission() == 0);
    }
};

// -------------------------------------------------------------------------
// [C] LSM6DSOX Class Definition
// -------------------------------------------------------------------------
#define REG_WHO_AM_I        0x0F
#define REG_CTRL1_XL        0x10
#define REG_CTRL2_G         0x11
#define REG_INT1_CTRL       0x0D
#define REG_INT2_CTRL       0x0E
#define REG_OUTX_L_A        0x28
#define REG_OUTX_H_A        0x29
#define REG_OUTY_L_A        0x2A
#define REG_OUTY_H_A        0x2B
#define REG_OUTZ_L_A        0x2C
#define REG_OUTZ_H_A        0x2D
#define REG_TAP_CFG0        0x56
#define REG_TAP_CFG1        0x57
#define REG_TAP_CFG2        0x58
#define REG_TAP_THS_6D      0x59
#define REG_INT_DUR2        0x5A
#define REG_WAKE_UP_THS     0x5B
#define REG_WAKE_UP_DUR     0x5C
#define REG_FREE_FALL       0x5D
#define REG_MD1_CFG         0x5E

#define SPI_SPEED   10000000 

struct AccelData {
    int16_t x;
    int16_t y;
    int16_t z;
    float x_g;
    float y_g;
    float z_g;
};

class LSM6DSOX {
public:
    LSM6DSOX(int csPin) : _cs(csPin) {}
    
    bool begin() {
        pinMode(_cs, OUTPUT);
        deselect();
        SPI.begin();
        
        uint8_t whoAmI = readRegister(REG_WHO_AM_I);
        if (whoAmI != 0x6C) {
            return false;
        }
        writeRegister(REG_CTRL1_XL, 0x40); // 104Hz, +-2g
        writeRegister(REG_CTRL2_G, 0x00);  // Disable Gyro
        return true;
    }
    
    bool readAccel(AccelData &data) {
        select();
        SPI.transfer(REG_OUTX_L_A | 0x80);
        uint8_t xl = SPI.transfer(0x00);
        uint8_t xh = SPI.transfer(0x00);
        uint8_t yl = SPI.transfer(0x00);
        uint8_t yh = SPI.transfer(0x00);
        uint8_t zl = SPI.transfer(0x00);
        uint8_t zh = SPI.transfer(0x00);
        deselect();
        
        data.x = (int16_t)((xh << 8) | xl);
        data.y = (int16_t)((yh << 8) | yl);
        data.z = (int16_t)((zh << 8) | zl);
        
        const float factor = 0.000061035f;
        data.x_g = (float)data.x * factor;
        data.y_g = (float)data.y * factor;
        data.z_g = (float)data.z * factor;
        return true;
    }
    
    bool configureSafetyInterrupt(float threshold_g, uint8_t duration_ms) {
        uint8_t thresh_val = (uint8_t)(threshold_g / 0.03125f);
        if (thresh_val > 0x3F) thresh_val = 0x3F;
        writeRegister(REG_WAKE_UP_THS, thresh_val);
        
        uint8_t dur_val = duration_ms / 10;
        if (dur_val > 0x0F) dur_val = 0x0F;
        writeRegister(REG_WAKE_UP_DUR, dur_val);
        
        writeRegister(REG_MD1_CFG, 0x20); // Route Wake-Up to INT1
        
        uint8_t tapCfg0 = readRegister(REG_TAP_CFG0);
        writeRegister(REG_TAP_CFG0, tapCfg0 | 0x01); // Latch interrupt
        return true;
    }

private:
    int _cs;
    
    uint8_t readRegister(uint8_t reg) {
        select();
        SPI.transfer(reg | 0x80);
        uint8_t value = SPI.transfer(0x00);
        deselect();
        return value;
    }
    
    void writeRegister(uint8_t reg, uint8_t value) {
        select();
        SPI.transfer(reg & 0x7F);
        SPI.transfer(value);
        deselect();
    }
    
    void select() {
        SPI.beginTransaction(SPISettings(SPI_SPEED, MSBFIRST, SPI_MODE3));
        digitalWrite(_cs, LOW);
    }
    
    void deselect() {
        digitalWrite(_cs, HIGH);
        SPI.endTransaction();
    }
};

// -------------------------------------------------------------------------
// [D] Main Soothing Control Program
// -------------------------------------------------------------------------
TAS5805M amp;
LSM6DSOX accel(PIN_SPI_CS_XL);
PIDController pid(0.01f, 0.002f, 0.0005f, 12.0f); // Target 12um displacement

volatile bool safetyLockTriggered = false;
volatile bool systemActive = true;

volatile float targetFrequency = 45.0f; // Soothing freq
volatile float currentAmplitudeScale = 0.0f;
volatile float targetAmplitudeScale = 0.5f;

const float RAMP_STEP_20MS = 0.005f; 
const unsigned long MAX_RUNNING_TIME_MS = 30 * 60 * 1000; // 30 mins limit
unsigned long activeStateStartTime = 0;

int16_t sineLut[LUT_SIZE];
TaskHandle_t commTaskHandle = NULL;
TaskHandle_t controlTaskHandle = NULL;
TaskHandle_t audioTaskHandle = NULL;

void IRAM_ATTR safetyLockISR() {
    safetyLockTriggered = true;
    systemActive = false;
    digitalWrite(PIN_BOOST_EN, LOW); // Immediate MP3426 12V shutdown
}

void initSineLut() {
    for (int i = 0; i < LUT_SIZE; i++) {
        sineLut[i] = (int16_t)(sin(2.0f * PI * (float)i / (float)LUT_SIZE) * 32767.0f);
    }
}

bool initI2S() {
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
    
    if (i2s_driver_install(I2S_NUM, &i2s_config, 0, NULL) != ESP_OK) {
        return false;
    }
    if (i2s_set_pin(I2S_NUM, &pin_config) != ESP_OK) {
        return false;
    }
    return true;
}

void AudioOutputTask(void *pvParameters) {
    (void)pvParameters;
    int16_t buffer[512];
    float lut_phase = 0.0f;
    
    for (;;) {
        if (!systemActive || safetyLockTriggered) {
            memset(buffer, 0, sizeof(buffer));
            size_t bytes_written;
            i2s_write(I2S_NUM, buffer, sizeof(buffer), &bytes_written, portMAX_DELAY);
            vTaskDelay(pdMS_TO_TICKS(50));
            continue;
        }
        
        float step = (targetFrequency * (float)LUT_SIZE) / (float)SAMPLE_RATE;
        for (int i = 0; i < 256; i++) {
            int index = (int)lut_phase % LUT_SIZE;
            int16_t sample = (int16_t)((float)sineLut[index] * currentAmplitudeScale);
            buffer[i * 2]     = sample;
            buffer[i * 2 + 1] = sample;
            lut_phase += step;
            if (lut_phase >= (float)LUT_SIZE) {
                lut_phase -= (float)LUT_SIZE;
            }
        }
        size_t bytes_written;
        i2s_write(I2S_NUM, buffer, sizeof(buffer), &bytes_written, portMAX_DELAY);
    }
}

void VibrationControlTask(void *pvParameters) {
    (void)pvParameters;
    TickType_t xLastWakeTime = xTaskGetTickCount();
    const TickType_t xFrequency = pdMS_TO_TICKS(20); // 50Hz
    
    AccelData accelData;
    float dt = 0.02f;
    float accel_dc = 0.0f;
    float vel = 0.0f;
    float disp = 0.0f;
    float measured_amplitude_um = 0.0f;
    float disp_envelope = 0.0f;
    
    activeStateStartTime = millis();
    
    for (;;) {
        vTaskDelayUntil(&xLastWakeTime, xFrequency);
        if (safetyLockTriggered) continue;
        
        if (millis() - activeStateStartTime > MAX_RUNNING_TIME_MS) {
            systemActive = false; // Soft Stop
        }
        
        if (systemActive) {
            if (currentAmplitudeScale < targetAmplitudeScale) {
                currentAmplitudeScale += RAMP_STEP_20MS;
                if (currentAmplitudeScale > targetAmplitudeScale) currentAmplitudeScale = targetAmplitudeScale;
            } else if (currentAmplitudeScale > targetAmplitudeScale) {
                currentAmplitudeScale -= RAMP_STEP_20MS;
                if (currentAmplitudeScale < targetAmplitudeScale) currentAmplitudeScale = targetAmplitudeScale;
            }
        } else {
            if (currentAmplitudeScale > 0.0f) {
                currentAmplitudeScale -= RAMP_STEP_20MS;
                if (currentAmplitudeScale < 0.0f) currentAmplitudeScale = 0.0f;
            } else {
                amp.enterStandbyState();
            }
        }
        
        if (accel.readAccel(accelData)) {
            accel_dc = 0.995f * accel_dc + 0.005f * accelData.z_g;
            float accel_ac_g = accelData.z_g - accel_dc;
            float accel_m_s2 = accel_ac_g * 9.80665f;
            
            vel = 0.99f * vel + accel_m_s2 * dt;
            disp = 0.99f * disp + vel * dt;
            float current_z_disp_um = disp * 1000000.0f;
            
            disp_envelope = 0.98f * disp_envelope + 0.02f * abs(current_z_disp_um);
            measured_amplitude_um = disp_envelope * 1.5708f;
            
            if (systemActive && currentAmplitudeScale > 0.05f) {
                float pid_output = pid.compute(measured_amplitude_um, dt);
                targetAmplitudeScale += pid_output * 0.01f;
                if (targetAmplitudeScale > 1.0f) targetAmplitudeScale = 1.0f;
                if (targetAmplitudeScale < 0.05f) targetAmplitudeScale = 0.05f;
            }
        }
    }
}

void WiFiBTCommunicationTask(void *pvParameters) {
    (void)pvParameters;
    for (;;) {
        if (safetyLockTriggered) {
            vTaskDelay(pdMS_TO_TICKS(1000));
            continue;
        }
        // Wi-Fi and bluetooth handling code stub
        vTaskDelay(pdMS_TO_TICKS(100));
    }
}

void setup() {
    Serial.begin(115200);
    
    pinMode(PIN_BOOST_EN, OUTPUT);
    digitalWrite(PIN_BOOST_EN, HIGH); 
    pinMode(PIN_SAFETY_INT1, INPUT_PULLDOWN);
    
    initSineLut();
    
    SPI.begin(PIN_SPI_SCLK, PIN_SPI_MISO, PIN_SPI_MOSI, PIN_SPI_CS_XL);
    if (!accel.begin()) {
        Serial.println("[ERROR] LSM6DSOX Accelerometer Initialization Failed.");
        while (1);
    }
    
    if (!amp.begin(PIN_I2C_SDA, PIN_I2C_SCL)) {
        Serial.println("[ERROR] TAS5805M Amplifier Initialization Failed.");
        while (1);
    }
    
    if (!initI2S()) {
        Serial.println("[ERROR] I2S initialization failed.");
        while (1);
    }
    
    accel.configureSafetyInterrupt(1.5f, 20);
    amp.enterPlayState();
    pid.setOutputLimits(-1.0f, 1.0f);
    
    attachInterrupt(digitalPinToInterrupt(PIN_SAFETY_INT1), safetyLockISR, RISING);
    
    xTaskCreatePinnedToCore(WiFiBTCommunicationTask, "CommTask", 4096, NULL, 1, &commTaskHandle, 0);
    xTaskCreatePinnedToCore(VibrationControlTask, "ControlTask", 4096, NULL, 4, &controlTaskHandle, 1);
    xTaskCreatePinnedToCore(AudioOutputTask, "AudioTask", 4096, NULL, 5, &audioTaskHandle, 1);
}

void loop() {
    vTaskDelay(pdMS_TO_TICKS(1000));
}
