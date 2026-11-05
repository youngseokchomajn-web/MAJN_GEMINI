#include "majn_power_state_machine.h"
#include <cstdio>

namespace Majn {

PowerStateMachine::PowerStateMachine(IHardwareInterface &hal, const HardwarePinConfig &pins)
    : _hal(hal),
      _pins(pins),
      _currentState(PowerState::BOOT_COLD),
      _activeFaults(static_cast<uint32_t>(FaultSource::NONE)),
      _stateEntryTime(0),
      _recoveryAttempts(0) {
}

bool PowerStateMachine::initialize() {
    _hal.logMessage("[FSM] Initializing Power State Machine (PCB #0006 Architecture)...");

    // Configure GPIO pins to safe default states immediately
    // BOOST_EN = Output LOW
    _hal.setPinMode(_pins.pinBoostEn, 1 /* OUTPUT */);
    _hal.writePin(_pins.pinBoostEn, 0);

    // AMP_PDN = Output LOW (10k pulldown holds line at 0V even in tristate)
    _hal.setPinMode(_pins.pinAmpPdn, 1 /* OUTPUT */);
    _hal.writePin(_pins.pinAmpPdn, 0);

    // AMP_FAULTz = Input (GPI only on GPIO35, external 4.7k pull-up R12)
    _hal.setPinMode(_pins.pinAmpFaultz, 0 /* INPUT */);

    _currentState = PowerState::BOOT_COLD;
    _stateEntryTime = _hal.getMillis();
    _activeFaults = static_cast<uint32_t>(FaultSource::NONE);
    _recoveryAttempts = 0;

    // Begin controlled power-up sequence
    transitionTo(PowerState::POWER_STABILIZING);
    return true;
}

void PowerStateMachine::tick(uint32_t currentMillis) {
    // 1. Continuous Safety Guard: Check hardware fault line on GPIO35 (Active LOW)
    if (_currentState == PowerState::STANDBY_SAFE || _currentState == PowerState::RUNNING_ACTIVE) {
        if (_hal.readPin(_pins.pinAmpFaultz) == 0) {
            _hal.logMessage("[FSM] CRITICAL: TAS5805M Pin 3 FAULTz asserted LOW! Immediate interrupt trip.");
            triggerEmergencyStop(FaultSource::AMP_HARDWARE_FAULT_ISR);
            return;
        }
    }

    // 2. State-specific processing
    switch (_currentState) {
        case PowerState::BOOT_COLD:
            // Remain cold until initialized
            break;

        case PowerState::POWER_STABILIZING:
            // Wait for Boost 12V and charge pump to reach steady state
            if (currentMillis - _stateEntryTime >= BOOST_SETTLE_MS) {
                _hal.logMessage("[FSM] 12V PVDD stabilized. Asserting AMP_PDN HIGH...");
                _hal.writePin(_pins.pinAmpPdn, 1);
                _hal.delayMs(PDN_SETTLE_MS);
                transitionTo(PowerState::STANDBY_SAFE);
            }
            break;

        case PowerState::STANDBY_SAFE:
            // Safe low-power idle state; waiting for requestStart()
            break;

        case PowerState::RUNNING_ACTIVE:
            // Audio output active; guarded by hardware fault line and software supervisor
            break;

        case PowerState::FAULT_LATCHED:
            // Fault condition latched; output muted
            break;

        case PowerState::EMERGENCY_SHUTDOWN:
            // Hard shutdown; hardware held in safe state
            break;
    }
}

bool PowerStateMachine::requestStart() {
    if (_currentState != PowerState::STANDBY_SAFE) {
        _hal.logMessage("[FSM] Warning: Cannot start running from non-standby state.");
        return false;
    }

    _hal.logMessage("[FSM] Transitioning to RUNNING_ACTIVE...");
    transitionTo(PowerState::RUNNING_ACTIVE);
    return true;
}

bool PowerStateMachine::requestStop() {
    if (_currentState == PowerState::RUNNING_ACTIVE) {
        _hal.logMessage("[FSM] Safe Stop requested. Returning to STANDBY_SAFE...");
        transitionTo(PowerState::STANDBY_SAFE);
        return true;
    }
    return false;
}

void PowerStateMachine::triggerEmergencyStop(FaultSource fault) {
    _activeFaults |= static_cast<uint32_t>(fault);
    _hal.logMessage("[FSM] EMERGENCY STOP TRIGGERED!");
    transitionTo(PowerState::EMERGENCY_SHUTDOWN);
}

bool PowerStateMachine::attemptFaultRecovery() {
    if (_currentState != PowerState::FAULT_LATCHED && _currentState != PowerState::EMERGENCY_SHUTDOWN) {
        return false;
    }

    if (_recoveryAttempts >= MAX_RECOVERY_ATTEMPTS) {
        _hal.logMessage("[FSM] Max recovery attempts exceeded. System locked in EMERGENCY_SHUTDOWN.");
        return false;
    }

    _recoveryAttempts++;
    char buf[80];
    std::snprintf(buf, sizeof(buf), "[FSM] Attempting fault recovery (%u/%u)...", _recoveryAttempts, MAX_RECOVERY_ATTEMPTS);
    _hal.logMessage(buf);

    // Power cycle procedure: Kill PDN and Boost, wait, then reinitialize
    _hal.writePin(_pins.pinAmpPdn, 0);
    _hal.writePin(_pins.pinBoostEn, 0);
    _hal.delayMs(50);

    _activeFaults = static_cast<uint32_t>(FaultSource::NONE);
    transitionTo(PowerState::POWER_STABILIZING);
    return true;
}

void PowerStateMachine::transitionTo(PowerState newState) {
    exitState(_currentState);
    _currentState = newState;
    _stateEntryTime = _hal.getMillis();
    enterState(_currentState);
}

void PowerStateMachine::enterState(PowerState state) {
    switch (state) {
        case PowerState::BOOT_COLD:
            _hal.writePin(_pins.pinBoostEn, 0);
            _hal.writePin(_pins.pinAmpPdn, 0);
            break;

        case PowerState::POWER_STABILIZING:
            _hal.logMessage("[FSM] Enter POWER_STABILIZING: Enabling Boost (GPIO4 HIGH)");
            _hal.writePin(_pins.pinBoostEn, 1);
            break;

        case PowerState::STANDBY_SAFE:
            _hal.logMessage("[FSM] Enter STANDBY_SAFE: Amplifier in Hi-Z standby");
            // Set TAS5805M into Hi-Z mode over I2C (Reg 0x03 = 0x02)
            _hal.i2cWriteRegister(0x2C, 0x03, 0x02);
            break;

        case PowerState::RUNNING_ACTIVE:
            _hal.logMessage("[FSM] Enter RUNNING_ACTIVE: Switching TAS5805M to PLAY mode");
            // Set TAS5805M into Play mode over I2C (Reg 0x03 = 0x03)
            _hal.i2cWriteRegister(0x2C, 0x03, 0x03);
            break;

        case PowerState::FAULT_LATCHED:
            _hal.logMessage("[FSM] Enter FAULT_LATCHED: Muting TAS5805M (Reg 0x03 = 0x00)");
            _hal.i2cWriteRegister(0x2C, 0x03, 0x00);
            break;

        case PowerState::EMERGENCY_SHUTDOWN:
            _hal.logMessage("[FSM] Enter EMERGENCY_SHUTDOWN: Clamping AMP_PDN=0 and BOOST_EN=0");
            _hal.writePin(_pins.pinAmpPdn, 0);
            _hal.writePin(_pins.pinBoostEn, 0);
            break;
    }
}

void PowerStateMachine::exitState(PowerState state) {
    (void)state;
}

const char* PowerStateMachine::getStateString() const {
    switch (_currentState) {
        case PowerState::BOOT_COLD:          return "BOOT_COLD";
        case PowerState::POWER_STABILIZING:  return "POWER_STABILIZING";
        case PowerState::STANDBY_SAFE:       return "STANDBY_SAFE";
        case PowerState::RUNNING_ACTIVE:     return "RUNNING_ACTIVE";
        case PowerState::FAULT_LATCHED:      return "FAULT_LATCHED";
        case PowerState::EMERGENCY_SHUTDOWN: return "EMERGENCY_SHUTDOWN";
    }
    return "UNKNOWN";
}

bool PowerStateMachine::isOutputSafe() const {
    return (_currentState == PowerState::BOOT_COLD ||
            _currentState == PowerState::STANDBY_SAFE ||
            _currentState == PowerState::FAULT_LATCHED ||
            _currentState == PowerState::EMERGENCY_SHUTDOWN);
}

} // namespace Majn
