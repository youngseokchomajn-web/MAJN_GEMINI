#include "majn_amplifier_driver.h"
#include <cstdio>

namespace Majn {

AmplifierDriver::AmplifierDriver(IHardwareInterface &hal)
    : _hal(hal),
      _activeAddress(0),
      _isInitialized(false) {
}

bool AmplifierDriver::probeAndInitialize() {
    _hal.logMessage("[AmpDriver] Probing TAS5805M I2C slave address...");

    const uint8_t candidateAddresses[] = {
        ADDR_CANDIDATE_1, // 0x2C (Standard)
        ADDR_CANDIDATE_2, // 0x2D
        ADDR_CANDIDATE_3, // 0x2E
        ADDR_CANDIDATE_4  // 0x2F
    };

    _activeAddress = 0;
    for (uint8_t addr : candidateAddresses) {
        uint8_t val = 0;
        if (_hal.i2cReadRegister(addr, 0x00 /* Page Reg */, val)) {
            _activeAddress = addr;
            char msg[64];
            std::snprintf(msg, sizeof(msg), "[AmpDriver] Detected TAS5805M at I2C address 0x%02X", _activeAddress);
            _hal.logMessage(msg);
            break;
        }
    }

    if (_activeAddress == 0) {
        _hal.logMessage("[AmpDriver] ERROR: No TAS5805M responding on any candidate address!");
        _isInitialized = false;
        return false;
    }

    // Step 1: Place device into Deep Sleep / Hi-Z while setting up DSP registers
    writeReg(0x03 /* DEVICE_CTRL_2 */, 0x02 /* Hi-Z mode */);

    // Step 2: Configure Pin 3 as Open-Drain Active-LOW FAULT Output
    if (!reconfigurePin3AsFaultOutput()) {
        _hal.logMessage("[AmpDriver] ERROR: Failed to configure Pin 3 ADR/FAULT mode!");
        return false;
    }

    // Step 3: Clear any initial latched startup faults
    clearFaults();

    // Step 4: Apply conservative initial volume clamp (Mute)
    setVolumeClamped(0);

    _isInitialized = true;
    _hal.logMessage("[AmpDriver] TAS5805M successfully configured into Standby/Safe mode.");
    return true;
}

bool AmplifierDriver::reconfigurePin3AsFaultOutput() {
    _hal.logMessage("[AmpDriver] Programming Register 0x61/0x60: ADR Pin -> FAULTz Output...");

    // 1. Switch to Book 0, Page 0
    if (!writeBookPage(0x00, 0x00)) return false;

    // 2. Set ADR_PIN_CONFIG (Reg 0x61) = 0x0B (FAULTz mode)
    if (!writeReg(0x61, 0x0B)) return false;

    // 3. Set ADR_PIN_CTRL (Reg 0x60) = 0x01 (Output Driver Enable)
    if (!writeReg(0x60, 0x01)) return false;

    _hal.logMessage("[AmpDriver] Pin 3 successfully programmed as Open-Drain FAULTz.");
    return true;
}

bool AmplifierDriver::clearFaults() {
    // Write 0x80 to Reg 0x78 (FAULT_CLEAR)
    if (!writeBookPage(0x00, 0x00)) return false;
    return writeReg(0x78, 0x80);
}

bool AmplifierDriver::setDeviceState(uint8_t state) {
    if (!_isInitialized && _activeAddress == 0) return false;
    // Reg 0x03: Bits [1:0] = CTRL_STATE (0=Deep Sleep, 1=Sleep, 2=HIZ, 3=Play)
    return writeReg(0x03, state & 0x03);
}

bool AmplifierDriver::enterPlay() {
    _hal.logMessage("[AmpDriver] Switching TAS5805M to PLAY (State: 0x03)...");
    clearFaults();
    return setDeviceState(0x03);
}

bool AmplifierDriver::enterStandby() {
    _hal.logMessage("[AmpDriver] Switching TAS5805M to STANDBY (State: 0x02)...");
    return setDeviceState(0x02);
}

bool AmplifierDriver::muteOutput() {
    _hal.logMessage("[AmpDriver] Hardware Muting TAS5805M...");
    return setDeviceState(0x00);
}

bool AmplifierDriver::setVolumeClamped(uint8_t percentVolume) {
    if (!_isInitialized && _activeAddress == 0) return false;

    uint8_t regVal;
    if (percentVolume == 0) {
        regVal = VOLUME_REG_MUTE; // 0xFF
    } else {
        // Linear mapping from 1%~100% to range [0xFE (mute-ish) down to VOLUME_REG_MAX_CLAMP (0x37 = -3.5dBFS)]
        // Notice: In TAS5805M, LOWER register value means HIGHER volume (less attenuation).
        // 0x30 = 0dBFS. We NEVER allow lower than 0x37!
        uint32_t span = 0xFE - VOLUME_REG_MAX_CLAMP; // 254 - 55 = 199 steps
        uint32_t attenuation = ((100 - percentVolume) * span) / 100;
        regVal = static_cast<uint8_t>(VOLUME_REG_MAX_CLAMP + attenuation);

        // Hardware enforcement clamp: Ensure regVal NEVER goes below 0x37
        if (regVal < VOLUME_REG_MAX_CLAMP) {
            regVal = VOLUME_REG_MAX_CLAMP;
        }
    }

    char msg[64];
    std::snprintf(msg, sizeof(msg), "[AmpDriver] Volume Set: %u%% -> Clamped Reg: 0x%02X", percentVolume, regVal);
    _hal.logMessage(msg);

    // Write to Master Volume Register 0x4C
    return writeReg(0x4C, regVal);
}

bool AmplifierDriver::readDiagnostics(AmplifierDiagnostics &diag) {
    diag.hasFault = false;
    if (!_isInitialized && _activeAddress == 0) return false;

    if (!readReg(0x68 /* CHAN_STATE */, diag.stateReg)) return false;
    if (!readReg(0x70 /* CHAN_FAULT */, diag.channelFaultReg)) return false;
    if (!readReg(0x71 /* GLOBAL_FAULT1 */, diag.globalFault1Reg)) return false;
    if (!readReg(0x72 /* GLOBAL_FAULT2 */, diag.globalFault2Reg)) return false;
    if (!readReg(0x73 /* WARNING */, diag.warningReg)) return false;

    // Check for critical fault bits:
    // Reg 0x70 != 0 (Channel OCP/DC fault)
    // Reg 0x71 != 0 (PVDD UVLO/OVLO, Clock fault, OTP)
    if (diag.channelFaultReg != 0 || (diag.globalFault1Reg & 0x7F) != 0) {
        diag.hasFault = true;
    }

    return true;
}

bool AmplifierDriver::writeBookPage(uint8_t book, uint8_t page) {
    if (!_hal.i2cWriteRegister(_activeAddress, 0x7F, book)) return false;
    if (!_hal.i2cWriteRegister(_activeAddress, 0x00, page)) return false;
    return true;
}

bool AmplifierDriver::writeReg(uint8_t reg, uint8_t val) {
    return _hal.i2cWriteRegister(_activeAddress, reg, val);
}

bool AmplifierDriver::readReg(uint8_t reg, uint8_t &val) {
    return _hal.i2cReadRegister(_activeAddress, reg, val);
}

} // namespace Majn
