#include "pid_control.h"

PIDController::PIDController(float kp, float ki, float kd, float target) 
    : _kp(kp), _ki(ki), _kd(kd), _target(target), _integral(0.0f), _prevError(0.0f), _minOut(0.0f), _maxOut(255.0f) {}

void PIDController::reset() {
    _integral = 0.0f;
    _prevError = 0.0f;
}

void PIDController::setTunings(float kp, float ki, float kd) {
    _kp = kp;
    _ki = ki;
    _kd = kd;
}

void PIDController::setTarget(float target) {
    _target = target;
}

void PIDController::setOutputLimits(float minOut, float maxOut) {
    _minOut = minOut;
    _maxOut = maxOut;
}

float PIDController::compute(float feedback, float dt) {
    if (dt <= 0.0f) return 0.0f;
    
    // Calculate error
    float error = _target - feedback;
    
    // Proportional term
    float pOut = _kp * error;
    
    // Integral term (with Anti-windup clamping check)
    _integral += error * dt;
    float iOut = _ki * _integral;
    
    // Clamping integral term to prevent saturation
    if (iOut > _maxOut) {
        iOut = _maxOut;
        _integral = _maxOut / _ki;
    } else if (iOut < _minOut) {
        iOut = _minOut;
        _integral = _minOut / _ki;
    }
    
    // Derivative term
    float derivative = (error - _prevError) / dt;
    float dOut = _kd * derivative;
    
    // Remember error for next calculation
    _prevError = error;
    
    // Calculate total output
    float totalOutput = pOut + iOut + dOut;
    
    // Clamp total output to specified limits
    if (totalOutput > _maxOut) {
        totalOutput = _maxOut;
    } else if (totalOutput < _minOut) {
        totalOutput = _minOut;
    }
    
    return totalOutput;
}
