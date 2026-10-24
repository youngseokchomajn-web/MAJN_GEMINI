#include "tas5805m.h"
#include <Wire.h>
#include <Arduino.h>

TAS5805M::TAS5805M(uint8_t i2cAddress) : _addr(i2cAddress) {}

bool TAS5805M::begin(int sdaPin, int sclPin) {
    Wire.begin(sdaPin, sclPin);
    Wire.setClock(100000); // 100kHz standard I2C speed
    
    // Auto-probe possible TAS5805M addresses (TI Datasheet Table: 0x2C for 4.7k, 0x2D for 15k, 0x2E for 47k, 0x2F for 100k)
    const uint8_t possibleAddrs[] = {
        TAS5805M_I2C_ADDR_4K7,
        TAS5805M_I2C_ADDR_15K,
        TAS5805M_I2C_ADDR_47K,
        TAS5805M_I2C_ADDR_100K
    };
    bool found = false;
    for (uint8_t a : possibleAddrs) {
        Wire.beginTransmission(a);
        if (Wire.endTransmission() == 0) {
            _addr = a;
            found = true;
            Serial.printf("[TAS5805M] Detected device at I2C address 0x%02X\n", a);
            break;
        }
    }
    
    if (!found) {
        Serial.println("[TAS5805M] ERROR: No TAS5805M device responded on I2C (probed 0x2C, 0x2D, 0x2E, 0x2F).");
        Serial.println("[TAS5805M] Check 3.3V DVDD, 12V PVDD, PDN pin (GPIO15), and I2C pull-up resistors.");
        return false;
    }
    
    // Step 1: Initial register configurations
    // Select Book 0, Page 0
    if (!writeBookPage(0x00, 0x00)) {
        Serial.println("[TAS5805M] Init Step Failed: writeBookPage(0x00, 0x00)");
        return false;
    }
    delay(2);
    
    // Transition to Hi-Z (0x02) before configuring
    if (!writeRegister(REG_DEVICE_CTRL_2, 0x02)) {
        Serial.println("[TAS5805M] Init Step Failed: Set Hi-Z (REG_DEVICE_CTRL_2 = 0x02)");
        return false;
    }
    delay(2);
    
    // Set standard I2S format & explicit 16-bit word length (SAP_CTRL1: 0x33 = 0x00)
    if (!writeRegister(0x33, 0x00)) {
        Serial.println("[TAS5805M] Init Step Failed: Set SAP_CTRL1 (0x33 = 0x00)");
        return false;
    }
    if (!writeRegister(REG_SIG_CH_CTRL, 0x00)) {
        Serial.println("[TAS5805M] Init Step Failed: Set REG_SIG_CH_CTRL (0x28 = 0x00)");
        return false;
    }
    
    // Set 0dB unity gain volume for Master, Ch1, and Ch2 (0x30 = 0dB in TAS5805M)
    writeRegister(REG_MASTER_VOL, 0x30); // 0x4C
    writeRegister(0x4D, 0x30);           // CH1 Volume
    writeRegister(0x4E, 0x30);           // CH2 Volume (J2 speaker connector)
    
    // Enable Spread Spectrum for EMI suppression (3~6dB peak reduction)
    enableSpreadSpectrum(true);

    // Clear any previous fault flags (Write 0x80 to 0x78 FAULT_CLEAR)
    writeRegister(0x78, 0x80);
    delay(5);
    
    // Enter Play State (0x03)
    if (!enterPlayState()) {
        Serial.println("[TAS5805M] Init Step Failed: enterPlayState()");
        return false;
    }
    
    Serial.println("[TAS5805M] Initialization completed successfully. Amplifier in PLAY state.");
    return true;
}

uint8_t TAS5805M::getI2CAddress() const {
    return _addr;
}

bool TAS5805M::enterPlayState() {
    if (!writeBookPage(0x00, 0x00)) return false;
    // Clear latched faults before requesting Play mode
    writeRegister(REG_FAULT_CLEAR, 0x80);
    delay(5);
    // REG_DEVICE_CTRL_2 (0x03): 0x03 = PLAY Mode (0x02 = Hi-Z Mode)
    return writeRegister(REG_DEVICE_CTRL_2, 0x03);
}

bool TAS5805M::readRegister(uint8_t reg, uint8_t &val) {
    Wire.beginTransmission(_addr);
    Wire.write(reg);
    if (Wire.endTransmission() != 0) return false;
    if (Wire.requestFrom(_addr, (uint8_t)1) != 1) return false;
    val = Wire.read();
    return true;
}

bool TAS5805M::getDiagnostics(uint8_t &state, uint8_t &chanFault, uint8_t &globalFault1) {
    if (!writeBookPage(0x00, 0x00)) return false;
    state = 0xFF;
    chanFault = 0xFF;
    globalFault1 = 0xFF;
    readRegister(REG_DEVICE_CTRL_2, state);
    readRegister(REG_CHAN_FAULT, chanFault);
    readRegister(REG_GLOBAL_FAULT1, globalFault1);
    return true;
}

bool TAS5805M::enterStandbyState() {
    if (!writeBookPage(0x00, 0x00)) return false;
    // REG_DEVICE_CTRL_2 (0x03): 0x02 = Hi-Z (High Impedance Output / Standby)
    return writeRegister(REG_DEVICE_CTRL_2, 0x02);
}

bool TAS5805M::setVolume(uint8_t volumeReg) {
    if (!writeBookPage(0x00, 0x00)) return false;
    // TAS5805M REG_MASTER_VOL (0x4C): 0x00 = +24dB, 0x30 = 0dB (Unity Gain), 0xFF = Mute
    // Clamping to minimum 0x30 prevents over-amplification beyond 0dB (infant ear protection)
    uint8_t safetyVolume = volumeReg;
    if (safetyVolume < 0x30) {
        safetyVolume = 0x30;
    }
    writeRegister(REG_MASTER_VOL, safetyVolume); // 0x4C
    writeRegister(0x4D, safetyVolume);           // CH1 Volume
    writeRegister(0x4E, safetyVolume);           // CH2 Volume
    return true;
}

bool TAS5805M::enableAGL(bool enable) {
    if (!writeBookPage(0x00, 0x3C)) return false;
    if (enable) {
        if (!writeRegister(REG_AGL_CTRL, 0x01)) return false;
    } else {
        if (!writeRegister(REG_AGL_CTRL, 0x00)) return false;
    }
    return writeBookPage(0x00, 0x00);
}

bool TAS5805M::enableSpreadSpectrum(bool enable) {
    if (!writeBookPage(0x00, 0x00)) return false;
    if (enable) {
        // SS_CTRL0 (0x6B) = 0x03 (Enable Spread Spectrum with triangle mode)
        // SS_CTRL1 (0x6C) = 0x03 (24kHz triangle frequency, 25% spread range)
        writeRegister(REG_SS_CTRL0, 0x03);
        writeRegister(REG_SS_CTRL1, 0x03);
        Serial.println("[TAS5805M] EMI Spread Spectrum Enabled (SS_CTRL0=0x03, SS_CTRL1=0x03)");
    } else {
        writeRegister(REG_SS_CTRL0, 0x00);
        Serial.println("[TAS5805M] EMI Spread Spectrum Disabled");
    }
    return true;
}

// Private helper to write standard I2C register
bool TAS5805M::writeRegister(uint8_t reg, uint8_t value) {
    Wire.beginTransmission(_addr);
    Wire.write(reg);
    Wire.write(value);
    return (Wire.endTransmission() == 0);
}

// Private helper to change Book and Page selection in TAS5805M (TI 3-step sequence)
bool TAS5805M::writeBookPage(uint8_t book, uint8_t page) {
    // 1. Move to Page 0 first so register 0x7F operates as Book Select
    Wire.beginTransmission(_addr);
    Wire.write((uint8_t)0x00);
    Wire.write((uint8_t)0x00);
    if (Wire.endTransmission() != 0) return false;
    
    // 2. Write Book selection (0x7F)
    Wire.beginTransmission(_addr);
    Wire.write((uint8_t)REG_BOOK_SEL);
    Wire.write(book);
    if (Wire.endTransmission() != 0) return false;
    
    // 3. Write target Page selection (0x00)
    Wire.beginTransmission(_addr);
    Wire.write((uint8_t)0x00);
    Wire.write(page);
    return (Wire.endTransmission() == 0);
}
