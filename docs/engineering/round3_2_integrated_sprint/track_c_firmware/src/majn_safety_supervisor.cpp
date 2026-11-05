#include "majn_safety_supervisor.h"
#include <cstdio>
#include <algorithm>

namespace Majn {

SafetySupervisor::SafetySupervisor(IHardwareInterface &hal, PowerStateMachine &fsm, AmplifierDriver &amp)
    : _hal(hal),
      _fsm(fsm),
      _amp(amp),
      _targetFrequency(45.0f),
      _targetAmplitude(0.0f),
      _currentAmplitude(0.0f),
      _sessionStartTime(0),
      _lastWatchdogPetTime(0),
      _isLockedOut(false),
      _diagnosticTickCounter(0) {
}

void SafetySupervisor::initialize() {
    _hal.logMessage("[Supervisor] Initializing Safety & Watchdog Supervisor...");
    _sessionStartTime = 0;
    _lastWatchdogPetTime = _hal.getMillis();
    _isLockedOut = false;
    _targetFrequency = 45.0f;
    _targetAmplitude = 0.0f;
    _currentAmplitude = 0.0f;
    _diagnosticTickCounter = 0;
}

void SafetySupervisor::setVibrationTarget(float freqHz, float amplitudeScale) {
    if (_isLockedOut) {
        _hal.logMessage("[Supervisor] Warning: Target rejected. Safety Lockout is ACTIVE.");
        _targetAmplitude = 0.0f;
        return;
    }

    // Clamp frequency strictly between 30Hz and 120Hz
    _targetFrequency = std::max(FREQ_MIN_CLAMP_HZ, std::min(freqHz, FREQ_MAX_CLAMP_HZ));

    // Clamp amplitude strictly between 0.0 and AMPLITUDE_MAX_CLAMP (0.50f)
    _targetAmplitude = std::max(0.0f, std::min(amplitudeScale, AMPLITUDE_MAX_CLAMP));

    char msg[80];
    std::snprintf(msg, sizeof(msg), "[Supervisor] SetTarget: %.1f Hz, Target Scale: %.3f (Clamped to 0.50f)",
                  _targetFrequency, _targetAmplitude);
    _hal.logMessage(msg);

    // If starting a new active vibration session, record timestamp
    if (_targetAmplitude > 0.0f && _sessionStartTime == 0) {
        _sessionStartTime = _hal.getMillis();
    } else if (_targetAmplitude == 0.0f) {
        _sessionStartTime = 0;
    }
}

void SafetySupervisor::tickSupervisor(uint32_t currentMillis, float dt) {
    (void)dt;

    // 1. Task Watchdog Supervision (5000ms max starvation)
    if (currentMillis - _lastWatchdogPetTime > 5000) {
        _hal.logMessage("[Supervisor] FATAL: FreeRTOS Task Starvation / Watchdog Timeout (>5000ms)!");
        _isLockedOut = true;
        _fsm.triggerEmergencyStop(FaultSource::WATCHDOG_TIMEOUT);
        return;
    }

    // 2. 30-Minute KC Infant Safety Run-Time Cutoff
    if (_sessionStartTime > 0 && (currentMillis - _sessionStartTime >= KC_AUTO_STOP_LIMIT_MS)) {
        _hal.logMessage("[Supervisor] KC Compliance Alert: 30-minute maximum runtime reached. Initiating Soft Stop.");
        _targetAmplitude = 0.0f;
        _sessionStartTime = 0;
        _fsm.requestStop();
    }

    // 3. Smooth Slew-Rate Ramping (Soft Start / Stop)
    if (_currentAmplitude < _targetAmplitude) {
        _currentAmplitude += SLEW_RATE_PER_TICK;
        if (_currentAmplitude > _targetAmplitude) _currentAmplitude = _targetAmplitude;
    } else if (_currentAmplitude > _targetAmplitude) {
        _currentAmplitude -= SLEW_RATE_PER_TICK;
        if (_currentAmplitude < _targetAmplitude) _currentAmplitude = _targetAmplitude;
    }

    // 4. Background I2C Diagnostic Health Supervision (every 100ms = 5 ticks of 20ms)
    if (++_diagnosticTickCounter >= 5) {
        _diagnosticTickCounter = 0;

        if (_fsm.getState() == PowerState::RUNNING_ACTIVE) {
            AmplifierDiagnostics diag{};
            if (!_amp.readDiagnostics(diag)) {
                _hal.logMessage("[Supervisor] ERROR: TAS5805M I2C Communication Lost / Bus Stuck!");
                _fsm.triggerEmergencyStop(FaultSource::AMP_I2C_NACK);
            } else if (diag.hasFault) {
                char fmsg[96];
                std::snprintf(fmsg, sizeof(fmsg),
                              "[Supervisor] HARDWARE FAULT: CF=0x%02X, GF1=0x%02X, GF2=0x%02X. Tripping E-Stop.",
                              diag.channelFaultReg, diag.globalFault1Reg, diag.globalFault2Reg);
                _hal.logMessage(fmsg);
                _isLockedOut = true;
                _fsm.triggerEmergencyStop(FaultSource::AMP_OVER_CURRENT);
            }
        }
    }
}

void SafetySupervisor::petWatchdog() {
    _lastWatchdogPetTime = _hal.getMillis();
}

bool SafetySupervisor::recoverStuckI2cBus(int pinScl, int pinSda) {
    _hal.logMessage("[Supervisor] Initiating 9-Clock I2C Bus Recovery Sequence on SCL/SDA...");

    _hal.setPinMode(pinSda, 0 /* INPUT_PULLUP */);
    _hal.setPinMode(pinScl, 1 /* OUTPUT */);

    // If SDA is stuck LOW by an interrupted slave transaction:
    // Generate up to 9 clock pulses on SCL to allow slave to release SDA
    for (int i = 0; i < 9; i++) {
        _hal.writePin(pinScl, 0);
        _hal.delayMs(1);
        _hal.writePin(pinScl, 1);
        _hal.delayMs(1);

        if (_hal.readPin(pinSda) == 1) {
            _hal.logMessage("[Supervisor] SDA released by slave after clocking.");
            break;
        }
    }

    // Generate standard I2C STOP condition (SCL HIGH, then SDA transition from LOW to HIGH)
    _hal.setPinMode(pinSda, 1 /* OUTPUT */);
    _hal.writePin(pinSda, 0);
    _hal.delayMs(1);
    _hal.writePin(pinScl, 1);
    _hal.delayMs(1);
    _hal.writePin(pinSda, 1);
    _hal.delayMs(1);

    _hal.logMessage("[Supervisor] I2C Bus Recovery Completed. STOP condition sent.");
    return true;
}

void SafetySupervisor::resetLockout() {
    _isLockedOut = false;
    _sessionStartTime = 0;
    _targetAmplitude = 0.0f;
    _currentAmplitude = 0.0f;
    _hal.logMessage("[Supervisor] Safety Lockout cleared by authorized command.");
}

} // namespace Majn
