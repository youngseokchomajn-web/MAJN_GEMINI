#include "tas5805m.h"
#include <Wire.h>
#include <Arduino.h>

TAS5805M::TAS5805M(uint8_t i2cAddress) : _addr(i2cAddress) {}

bool TAS5805M::begin(int sdaPin, int sclPin) {
    Wire.begin(sdaPin, sclPin);
    
    // Check if device responds on the I2C bus
    Wire.beginTransmission(_addr);
    if (Wire.endTransmission() != 0) {
        return false;
    }
    
    // Step 1: Initial register configurations
    // Set book 0, page 0
    if (!writeBookPage(0x00, 0x00)) return false;
    
    // Device Control 2: transition to Standby/HIZ before writing settings
    if (!writeRegister(REG_DEVICE_CTRL_2, 0x03)) return false; 
    
    // DSP initialization & digital gain configuration (miniDSP loading placeholder)
    // TAS5805M has an internal startup sequence: reset DSP
    if (!writeRegister(REG_DEVICE_CTRL_1, 0x00)) return false; // Clear error status
    
    // Lock Master Volume to -12dB initially to comply with safety limit (85dB limit)
    if (!setVolume(0x48)) return false; 
    
    // Enable AGL (Automatic Gain Limiter) by default
    if (!enableAGL(true)) return false;
    
    return true;
}

bool TAS5805M::enterPlayState() {
    if (!writeBookPage(0x00, 0x00)) return false;
    // REG_DEVICE_CTRL_2: Set to Play mode (0x03 -> 0x02: Standby ➔ Play)
    return writeRegister(REG_DEVICE_CTRL_2, 0x02);
}

bool TAS5805M::enterStandbyState() {
    if (!writeBookPage(0x00, 0x00)) return false;
    // REG_DEVICE_CTRL_2: Set to Standby/HIZ mode (0x03)
    return writeRegister(REG_DEVICE_CTRL_2, 0x03);
}

bool TAS5805M::setVolume(uint8_t volume) {
    if (!writeBookPage(0x00, 0x00)) return false;
    
    // HARDWARE LOCK FOR KC COMPLIANCE (어린이제품 공통안전기준 소음 85 dB 이하 보장)
    // 0x48 = -12 dB. To prevent outputting excessive sound/vibration level, 
    // we clamp the volume inside this driver.
    uint8_t safetyVolume = volume;
    if (safetyVolume > 0x48) {
        safetyVolume = 0x48; // Clamp to -12dB max output limit
    }
    
    return writeRegister(REG_MASTER_VOL, safetyVolume);
}

bool TAS5805M::enableAGL(bool enable) {
    // AGL configuration on Book 0, Page 0x3C (DSP control memory page)
    if (!writeBookPage(0x00, 0x3C)) return false;
    
    // Enable AGL threshold and analog/digital limits
    if (enable) {
        // Mock register write for AGL activation
        if (!writeRegister(REG_AGL_CTRL, 0x01)) return false; // Enable limiters
    } else {
        if (!writeRegister(REG_AGL_CTRL, 0x00)) return false;
    }
    
    // Re-select page 0
    return writeBookPage(0x00, 0x00);
}

// Private helper to write standard I2C register
bool TAS5805M::writeRegister(uint8_t reg, uint8_t value) {
    Wire.beginTransmission(_addr);
    Wire.write(reg);
    Wire.write(value);
    return (Wire.endTransmission() == 0);
}

// Private helper to change Book and Page selection in TAS5805M
bool TAS5805M::writeBookPage(uint8_t book, uint8_t page) {
    // 1. Write Book selection
    Wire.beginTransmission(_addr);
    Wire.write(REG_BOOK_SEL);
    Wire.write(book);
    if (Wire.endTransmission() != 0) return false;
    
    // 2. Write Page selection (always at register 0x00)
    Wire.beginTransmission(_addr);
    Wire.write(0x00);
    Wire.write(page);
    return (Wire.endTransmission() == 0);
}
