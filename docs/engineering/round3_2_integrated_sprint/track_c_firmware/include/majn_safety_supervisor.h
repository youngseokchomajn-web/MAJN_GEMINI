#pragma once

#include <stdint.h>
#include <stdbool.h>
#include "majn_power_state_machine.h"
#include "majn_amplifier_driver.h"

namespace Majn {

/**
 * @brief Safety Supervisor governing infant vibration safety, watchdogs, and bus lockups.
 */
class SafetySupervisor {
public:
    static constexpr float FREQ_MIN_CLAMP_HZ      = 30.0f;  ///< Minimum safe soothing frequency
    static constexpr float FREQ_MAX_CLAMP_HZ      = 120.0f; ///< Maximum allowable acoustic frequency
    static constexpr float AMPLITUDE_MAX_CLAMP    = 0.50f;  ///< Hard safety amplitude ceiling (50% scale)
    static constexpr float SLEW_RATE_PER_TICK     = 0.005f; ///< Soft-start ramp step (20ms tick)
    static constexpr uint32_t KC_AUTO_STOP_LIMIT_MS = 30 * 60 * 1000; ///< 30-minute infant safety limit

    SafetySupervisor(IHardwareInterface &hal, PowerStateMachine &fsm, AmplifierDriver &amp);

    void initialize();
    void tickSupervisor(uint32_t currentMillis, float dt);

    // Vibration setpoints with safety constraints
    void setVibrationTarget(float freqHz, float amplitudeScale);
    float getTargetFrequency() const { return _targetFrequency; }
    float getCurrentAmplitude() const { return _currentAmplitude; }

    // Watchdog and I2C health
    void petWatchdog();
    bool recoverStuckI2cBus(int pinScl, int pinSda);

    // Safety lockout queries
    bool isLockoutActive() const { return _isLockedOut; }
    void resetLockout();

private:
    IHardwareInterface &_hal;
    PowerStateMachine &_fsm;
    AmplifierDriver &_amp;

    float _targetFrequency;
    float _targetAmplitude;
    float _currentAmplitude;

    uint32_t _sessionStartTime;
    uint32_t _lastWatchdogPetTime;
    bool _isLockedOut;
    uint32_t _diagnosticTickCounter;
};

} // namespace Majn
