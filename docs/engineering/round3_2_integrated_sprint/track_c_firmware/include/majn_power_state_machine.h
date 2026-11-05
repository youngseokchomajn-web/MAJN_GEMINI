#pragma once

#include <stdint.h>
#include <stdbool.h>

namespace Majn {

/**
 * @brief Formal Operational States of the MAJN Power & Amplifier Subsystem.
 */
enum class PowerState : uint8_t {
    BOOT_COLD = 0,         ///< Initial hardware state upon reset; all power rails and drivers off
    POWER_STABILIZING = 1, ///< Boost enabled, waiting for 12V PVDD and I2S clocks to settle
    STANDBY_SAFE = 2,      ///< Clocks and PVDD ready; TAS5805M PDN asserted, Hi-Z audio output
    RUNNING_ACTIVE = 3,    ///< TAS5805M in Play state; closed-loop vibration synthesis running
    FAULT_LATCHED = 4,     ///< Hardware or communication fault detected; outputs muted immediately
    EMERGENCY_SHUTDOWN = 5 ///< Unrecoverable failure or supervisor trip; Boost and Amp killed
};

/**
 * @brief Subsystem Fault Flags
 */
enum class FaultSource : uint32_t {
    NONE                  = 0x00000000,
    AMP_HARDWARE_FAULT_ISR= 0x00000001, ///< Pin 3 FAULTz asserted LOW
    AMP_I2C_NACK          = 0x00000002, ///< TAS5805M communication timeout or NACK
    AMP_OVER_CURRENT      = 0x00000004, ///< TAS5805M Channel Fault (OCP)
    AMP_OVER_TEMP         = 0x00000008, ///< TAS5805M Over-temperature shutdown (OTE)
    BOOST_POWER_SAG       = 0x00000010, ///< PVDD or VBUS voltage dropped below threshold
    WATCHDOG_TIMEOUT      = 0x00000020, ///< FreeRTOS task starvation or hang
    SAFETY_LOCKOUT        = 0x00000040  ///< 30-minute KC limit or manual emergency stop
};

/**
 * @brief Hardware Pin Mapping for PCB #0006 Baseline
 */
struct HardwarePinConfig {
    int pinBoostEn;      ///< GPIO4: Active-HIGH Boost Converter Enable
    int pinAmpPdn;       ///< GPIO13: Active-HIGH TAS5805M Power Down (10k pulldown to GND)
    int pinAmpFaultz;    ///< GPIO35: Active-LOW Open-Drain Fault Interrupt from Pin 3
    int pinI2cSda;       ///< GPIO21: I2C Data
    int pinI2cScl;       ///< GPIO27: I2C Clock
    int pinI2sBclk;      ///< GPIO26: I2S Bit Clock
    int pinI2sLrclk;     ///< GPIO25: I2S Word Select / Frame Clock
    int pinI2sDout;      ///< GPIO22: I2S Serial Audio Data
};

/**
 * @brief Low-level Hardware Abstraction Interface for Testing & Platform Portability
 */
class IHardwareInterface {
public:
    virtual ~IHardwareInterface() = default;
    virtual void setPinMode(int pin, int mode) = 0;
    virtual void writePin(int pin, int value) = 0;
    virtual int readPin(int pin) = 0;
    virtual void delayMs(uint32_t ms) = 0;
    virtual uint32_t getMillis() = 0;
    virtual bool i2cWriteRegister(uint8_t addr, uint8_t reg, uint8_t val) = 0;
    virtual bool i2cReadRegister(uint8_t addr, uint8_t reg, uint8_t &val) = 0;
    virtual void logMessage(const char *msg) = 0;
};

/**
 * @brief State Machine Controller governing the Power and Amplifier sequencing.
 */
class PowerStateMachine {
public:
    explicit PowerStateMachine(IHardwareInterface &hal, const HardwarePinConfig &pins);

    // Initialization and state ticks
    bool initialize();
    void tick(uint32_t currentMillis);

    // High-level operational requests
    bool requestStart();
    bool requestStop();
    void triggerEmergencyStop(FaultSource fault);
    bool attemptFaultRecovery();

    // Status queries
    PowerState getState() const { return _currentState; }
    uint32_t getFaultMask() const { return _activeFaults; }
    const char* getStateString() const;
    bool isOutputSafe() const;

private:
    void transitionTo(PowerState newState);
    void enterState(PowerState state);
    void exitState(PowerState state);

    IHardwareInterface &_hal;
    HardwarePinConfig _pins;
    PowerState _currentState;
    uint32_t _activeFaults;
    uint32_t _stateEntryTime;
    uint8_t _recoveryAttempts;

    static constexpr uint32_t BOOST_SETTLE_MS = 20;
    static constexpr uint32_t PDN_SETTLE_MS = 30;
    static constexpr uint8_t MAX_RECOVERY_ATTEMPTS = 3;
};

} // namespace Majn
