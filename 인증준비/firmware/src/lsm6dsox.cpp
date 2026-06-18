#include "lsm6dsox.h"
#include <SPI.h>
#include <Arduino.h>

#define SPI_SPEED   10000000 // 10MHz SPI Speed

LSM6DSOX::LSM6DSOX(int csPin) : _cs(csPin) {}

bool LSM6DSOX::begin() {
    pinMode(_cs, OUTPUT);
    deselect();
    
    // Initialize SPI bus (should be initialized in main.cpp, but ensure safety here)
    SPI.begin();
    
    // Verify device connection by reading WHO_AM_I
    uint8_t whoAmI = readRegister(REG_WHO_AM_I);
    if (whoAmI != 0x6C) { // LSM6DSOX Device ID is 0x6C
        return false;
    }
    
    // Configure Accelerometer: ODR = 104 Hz, Scale = +-2g, LPF2 enabled
    // 0x40 ➔ ODR = 104Hz, Full Scale = +-2g (1 LSB = 0.061 mg)
    writeRegister(REG_CTRL1_XL, 0x40);
    
    // Disable Gyro to save power (ODR = 0)
    writeRegister(REG_CTRL2_G, 0x00);
    
    return true;
}

bool LSM6DSOX::readAccel(AccelData &data) {
    select();
    
    // SPI Read address (MSB must be 1 for read operation in LSM6DSOX SPI)
    SPI.transfer(REG_OUTX_L_A | 0x80);
    
    // Read 6 bytes of accel data sequentially (X_L, X_H, Y_L, Y_H, Z_L, Z_H)
    uint8_t xl = SPI.transfer(0x00);
    uint8_t xh = SPI.transfer(0x00);
    uint8_t yl = SPI.transfer(0x00);
    uint8_t yh = SPI.transfer(0x00);
    uint8_t zl = SPI.transfer(0x00);
    uint8_t zh = SPI.transfer(0x00);
    
    deselect();
    
    // Combine high and low bytes
    data.x = (int16_t)((xh << 8) | xl);
    data.y = (int16_t)((yh << 8) | yl);
    data.z = (int16_t)((zh << 8) | zl);
    
    // Convert raw 16-bit to float (g unit)
    // +-2g Full Scale ➔ factor = 2.0 / 32768.0 = 0.000061 g/LSB
    const float factor = 0.000061035f;
    data.x_g = (float)data.x * factor;
    data.y_g = (float)data.y * factor;
    data.z_g = (float)data.z * factor;
    
    return true;
}

bool LSM6DSOX::configureSafetyInterrupt(float threshold_g, uint8_t duration_ms) {
    // 1. Configure threshold and parameters for Free Fall or Wake Up event
    // For impact/shock detection, we configure the Wake-Up threshold
    
    // Wake-up configuration: ODR = 104Hz, threshold LSB depends on FS (at +-2g, 1 LSB = FS / 64 = 31.25 mg)
    uint8_t thresh_val = (uint8_t)(threshold_g / 0.03125f);
    if (thresh_val > 0x3F) thresh_val = 0x3F; // Max 6 bits
    
    // Write Wake-up threshold (REG_WAKE_UP_THS: 0x5B)
    writeRegister(REG_WAKE_UP_THS, thresh_val);
    
    // Write Wake-up duration (REG_WAKE_UP_DUR: 0x5C)
    // duration_ms converted to ODR samples (1 sample = ~10ms at 104Hz)
    uint8_t dur_val = duration_ms / 10;
    if (dur_val > 0x0F) dur_val = 0x0F; // Max 4 bits
    writeRegister(REG_WAKE_UP_DUR, dur_val);
    
    // 2. Enable routing wake-up event to INT1 pin
    // REG_INT1_CTRL (0x0D): Map INT1_WU (Wake-up event on INT1)
    // Wake-up routing is in REG_MD1_CFG (0x5E) on LSM6DSOX: Bit 5 = INT1_WU
    writeRegister(REG_MD1_CFG, 0x20); // Route Wake-Up to INT1
    
    // Enable interrupt latched mode (REG_TAP_CFG0: Bit 0 = LIR, latched interrupt)
    uint8_t tapCfg0 = readRegister(REG_TAP_CFG0);
    writeRegister(REG_TAP_CFG0, tapCfg0 | 0x01); // Latch interrupt signal until cleared
    
    return true;
}

// Private helper to read a register over SPI
uint8_t LSM6DSOX::readRegister(uint8_t reg) {
    select();
    SPI.transfer(reg | 0x80); // Read bit (bit 0 = 1)
    uint8_t value = SPI.transfer(0x00);
    deselect();
    return value;
}

// Private helper to write a register over SPI
void LSM6DSOX::writeRegister(uint8_t reg, uint8_t value) {
    select();
    SPI.transfer(reg & 0x7F); // Write bit (bit 0 = 0)
    SPI.transfer(value);
    deselect();
}

void LSM6DSOX::select() {
    SPI.beginTransaction(SPISettings(SPI_SPEED, MSBFIRST, SPI_MODE3));
    digitalWrite(_cs, LOW);
}

void LSM6DSOX::deselect() {
    digitalWrite(_cs, HIGH);
    SPI.endTransaction();
}
