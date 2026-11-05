#pragma once

#include <stdint.h>
#include <stdbool.h>
#include "majn_power_state_machine.h"

namespace Majn {

/**
 * @brief TAS5805M Comprehensive Diagnostic Structure
 */
struct AmplifierDiagnostics {
    uint8_t stateReg;         ///< Reg 0x68: Operational State (0=Deep Sleep, 1=Sleep, 2=HIZ, 3=Play)
    uint8_t channelFaultReg;  ///< Reg 0x70: Overcurrent / DC fault flags for Channel A and B
    uint8_t globalFault1Reg;  ///< Reg 0x71: Clock faults, PVDD UVLO/OVLO, OTP
    uint8_t globalFault2Reg;  ///< Reg 0x72: Thermal warning and PLL lock
    uint8_t warningReg;       ///< Reg 0x73: High impedance or clipping warnings
    bool hasFault;            ///< Evaluated summary: true if any critical fault is present
};

class AmplifierDriver {
public:
    static constexpr uint8_t ADDR_CANDIDATE_1 = 0x2C; ///< 4.7kΩ pull-up on Pin 3 (Standard PCB #0006)
    static constexpr uint8_t ADDR_CANDIDATE_2 = 0x2D; ///< 15kΩ pull-up on Pin 3
    static constexpr uint8_t ADDR_CANDIDATE_3 = 0x2E; ///< 47kΩ pull-up on Pin 3
    static constexpr uint8_t ADDR_CANDIDATE_4 = 0x2F; ///< 100kΩ pull-up on Pin 3

    // Firmware-enforced hardware power limit clamp (-3.5dBFS)
    // TAS5805M DIG_VOL (Reg 0x4C): 0x30 = 0dBFS. Each step is 0.5dB attenuation.
    // 0x30 + 7 steps = 0x37 (-3.5dBFS). Clamp guarantees system stays <= 7.0W audio.
    static constexpr uint8_t VOLUME_REG_MAX_CLAMP = 0x37; ///< -3.5dBFS maximum volume limit
    static constexpr uint8_t VOLUME_REG_MUTE      = 0xFF; ///< Complete mute

    explicit AmplifierDriver(IHardwareInterface &hal);

    // Initialization and Address Detection
    bool probeAndInitialize();
    uint8_t getActiveAddress() const { return _activeAddress; }

    // State commands
    bool setDeviceState(uint8_t state); // 0=Deep Sleep, 1=Sleep, 2=Hi-Z Standby, 3=Play
    bool enterPlay();
    bool enterStandby();
    bool muteOutput();

    // Volume control with firmware-enforced safety clamping
    bool setVolumeClamped(uint8_t percentVolume); // 0~100%, safely clamped

    // Diagnostics and Fault management
    bool reconfigurePin3AsFaultOutput();
    bool clearFaults();
    bool readDiagnostics(AmplifierDiagnostics &diag);

private:
    bool writeBookPage(uint8_t book, uint8_t page);
    bool writeReg(uint8_t reg, uint8_t val);
    bool readReg(uint8_t reg, uint8_t &val);

    IHardwareInterface &_hal;
    uint8_t _activeAddress;
    bool _isInitialized;
};

} // namespace Majn
