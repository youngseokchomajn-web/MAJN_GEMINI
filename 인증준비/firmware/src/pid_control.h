#ifndef PID_CONTROL_H
#define PID_CONTROL_H

class PIDController {
public:
    PIDController(float kp, float ki, float kd, float target);
    
    // Reset internal integral and derivative values
    void reset();
    
    // Update PID parameters dynamically
    void setTunings(float kp, float ki, float kd);
    
    // Update target setpoint
    void setTarget(float target);
    
    // Compute the control output based on current feedback value and loop time delta
    // Returns control signal clamped between minOut and maxOut
    float compute(float feedback, float dt);
    
    // Set output clamping limits
    void setOutputLimits(float minOut, float maxOut);

private:
    float _kp;
    float _ki;
    float _kd;
    float _target;
    
    float _integral;
    float _prevError;
    
    float _minOut;
    float _maxOut;
};

#endif // PID_CONTROL_H
