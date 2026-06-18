#ifndef TAS5805M_H
#define TAS5805M_H

#include <stdint.h>

// TAS5805M Default I2C Address (ADDR pin pulled down: 0x2C, ADDR pulled up: 0x2D)
#define TAS5805M_I2C_ADDR   0x2C

// TAS5805M Essential Registers
#define REG_DEVICE_CTRL_1   0x02
#define REG_DEVICE_CTRL_2   0x03
#define REG_SIG_CH_CTRL     0x28
#define REG_MASTER_VOL      0x4C
#define REG_ANALOG_GAIN     0x5C
#define REG_AGL_CTRL        0x60
#define REG_BOOK_SEL        0x7F

class TAS5805M {
public:
    TAS5805M(uint8_t i2cAddress = TAS5805M_I2C_ADDR);
    
    // Initialize I2C interface and configure basic parameters
    bool begin(int sdaPin, int sclPin);
    
    // Enter Play state from standby
    bool enterPlayState();
    
    // Enter Standby (HIZ) state
    bool enterStandbyState();
    
    // Set digital volume and lock it to max safety threshold (85dB limit compliance)
    // Range: 0 (Mute) to 255 (0dB), default safety limit is -12dB (0x48)
    bool setVolume(uint8_t volume);
    
    // Enable Automatic Gain Limiter (AGL) for speaker protection and peak control
    bool enableAGL(bool enable);

private:
    uint8_t _addr;
    bool writeRegister(uint8_t reg, uint8_t value);
    bool writeBookPage(uint8_t book, uint8_t page);
};

#endif // TAS5805M_H
