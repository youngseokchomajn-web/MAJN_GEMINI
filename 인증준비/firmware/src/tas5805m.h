#ifndef TAS5805M_H
#define TAS5805M_H

#include <stdint.h>

// TAS5805M I2C Addresses (TI Datasheet Table: 4.7kΩ->0x2C, 15kΩ->0x2D, 47kΩ->0x2E, 100kΩ->0x2F)
#define TAS5805M_I2C_ADDR_4K7       0x2C  // Standard 4.7k pull-up to DVDD (Schematic R12)
#define TAS5805M_I2C_ADDR_15K       0x2D  // 15k pull-up to DVDD
#define TAS5805M_I2C_ADDR_47K       0x2E  // 47k pull-up to DVDD
#define TAS5805M_I2C_ADDR_100K      0x2F  // 100k pull-up to DVDD
#define TAS5805M_I2C_ADDR_DEFAULT   TAS5805M_I2C_ADDR_4K7
#define TAS5805M_I2C_ADDR           TAS5805M_I2C_ADDR_DEFAULT

// TAS5805M Essential Registers
#define REG_DEVICE_CTRL_1   0x02
#define REG_DEVICE_CTRL_2   0x03
#define REG_SIG_CH_CTRL     0x28
#define REG_MASTER_VOL      0x4C
#define REG_ANALOG_GAIN     0x5C
#define REG_AGL_CTRL        0x60
#define REG_SS_CTRL0        0x6B
#define REG_SS_CTRL1        0x6C
#define REG_CHAN_FAULT      0x70
#define REG_GLOBAL_FAULT1   0x71
#define REG_GLOBAL_FAULT2   0x72
#define REG_WARNING         0x73
#define REG_FAULT_CLEAR     0x78
#define REG_BOOK_SEL        0x7F

class TAS5805M {
public:
    TAS5805M(uint8_t i2cAddress = TAS5805M_I2C_ADDR);
    
    // Initialize I2C interface and configure basic parameters
    bool begin(int sdaPin, int sclPin);
    
    // Enter Play state from standby (logs latched faults, then clears, then requests Play)
    bool enterPlayState();
    
    // Enter Standby (HIZ) state
    bool enterStandbyState();
    
    // Set digital volume
    bool setVolume(uint8_t volume);
    
    // Enable Automatic Gain Limiter (AGL)
    bool enableAGL(bool enable);

    // Enable EMI Spread Spectrum (3~6dB peak EMI reduction)
    bool enableSpreadSpectrum(bool enable);

    // Read operational state and fault registers
    bool readRegister(uint8_t reg, uint8_t &val);
    bool getDiagnostics(uint8_t &state, uint8_t &chanFault, uint8_t &globalFault1);
    bool getFullDiagnostics(uint8_t &state, uint8_t &chanFault, uint8_t &globalFault1, uint8_t &globalFault2, uint8_t &warning);
    uint8_t getI2CAddress() const;

private:
    uint8_t _addr;
    bool writeRegister(uint8_t reg, uint8_t value);
    bool writeBookPage(uint8_t book, uint8_t page);
};

#endif // TAS5805M_H
