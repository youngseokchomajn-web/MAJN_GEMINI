/*
  Majn Smart Bassinet - Vibration Control Firmware (Phase 1)
  Platform: ESP32 (Arduino IDE)
  
  Features:
  - ADXL355 SPI Communication (High-resolution Z-axis reading)
  - 1kHz Hardware Timer Interrupt for deterministic control loop
  - 30~65Hz Sine Wave Generation via DAC (GPIO 25)
  - Soft-start Ramp-up to prevent sudden mechanical shock
  - Phase 2: Double Integration & PID Loop for Amplitude Control
  - Phase 3: FRF Auto-calibration & Resonance Avoidance
  - Phase 4: Edge Actigraphy (Movement Detection in Sleep Mode)
*/

#include <SPI.h>

// --------------------------------------------------------
// [1] PIN MAP & HARDWARE CONSTANTS
// --------------------------------------------------------
#define ADXL355_CS_PIN 5
#define DAC_OUTPUT_PIN 25 // ESP32 DAC1

// ADXL355 Registers (Partial)
#define ADXL355_REG_XDATA3 0x08
#define ADXL355_REG_ZDATA3 0x0E
#define ADXL355_REG_POWER_CTL 0x2D

// --------------------------------------------------------
// [2] VIBRATION CONTROL VARIABLES
// --------------------------------------------------------
// State Machine
enum SystemState {
  STATE_INIT,
  STATE_CALIBRATION,
  STATE_ACTIGRAPHY_SLEEP, // Monitoring infant movement while motor is off
  STATE_RUNNING           // Active vibration soothing
};
volatile SystemState current_state = STATE_INIT;

volatile float current_frequency = 45.0; // Target frequency (30~65Hz)
volatile float phase = 0.0;
volatile float phase_increment = 0.0;
volatile float target_amplitude = 127.0; // Max amplitude offset (0~127 for 8-bit DAC)
volatile float current_amplitude = 0.0;  // For Soft-start

// Soft Start config
const float RAMP_UP_TIME_SEC = 3.0; // 3초에 걸쳐 서서히 진동 세기 증가
const float AMPLITUDE_STEP = 127.0 / (RAMP_UP_TIME_SEC * 1000.0); // 1ms당 증가량 (고정 기준값 127.0 사용)

// Sensor Variables
volatile float current_z_accel = 0.0;
volatile float current_z_vel = 0.0;
volatile float current_z_disp = 0.0; // Calculated displacement (μm)
volatile float measured_amplitude_um = 0.0;
volatile float setpoint_amplitude_um = 50.0; // Target amplitude in um

// PID Control Variables
volatile float pid_kp = 0.05;
volatile float pid_ki = 0.01;
volatile float pid_kd = 0.001;
volatile float pid_integral = 0.0;
volatile float pid_prev_error = 0.0;

// Resonance Calibration Variables
float sweep_data[36]; // Indices 0-35 correspond to 30-65Hz
int resonant_freq = -1; // -1 means no resonance found yet
const int SWEEP_START_FREQ = 30;
const int SWEEP_END_FREQ = 65;
int current_sweep_freq = SWEEP_START_FREQ;

// Actigraphy (Movement Detection) Variables
volatile float actigraphy_variance = 0.0;
const float THRASHING_THRESHOLD_UM = 15.0; // Threshold for waking/thrashing (micrometers of displacement caused by baby)
volatile unsigned long last_movement_time = 0;

hw_timer_t * timer = NULL;
portMUX_TYPE timerMux = portMUX_INITIALIZER_UNLOCKED;

// --------------------------------------------------------
// [3] ADXL355 FUNCTIONS
// --------------------------------------------------------
void initADXL355() {
  pinMode(ADXL355_CS_PIN, OUTPUT);
  digitalWrite(ADXL355_CS_PIN, HIGH);
  SPI.begin();
  
  // SPI Settings: Max 10MHz, MSB First, SPI Mode 0
  SPI.beginTransaction(SPISettings(5000000, MSBFIRST, SPI_MODE0));
  
  // Power up ADXL355 (Standby -> Measure)
  digitalWrite(ADXL355_CS_PIN, LOW);
  SPI.transfer(ADXL355_REG_POWER_CTL << 1); // Write mode
  SPI.transfer(0x00); // 0 = Measurement mode
  digitalWrite(ADXL355_CS_PIN, HIGH);
  
  SPI.endTransaction();
}

float readADXL355_Z() {
  // Read Z-axis 20-bit data (Registers 0x0E, 0x0F, 0x10)
  SPI.beginTransaction(SPISettings(5000000, MSBFIRST, SPI_MODE0));
  digitalWrite(ADXL355_CS_PIN, LOW);
  
  SPI.transfer((ADXL355_REG_ZDATA3 << 1) | 1); // Read mode
  uint8_t z3 = SPI.transfer(0x00);
  uint8_t z2 = SPI.transfer(0x00);
  uint8_t z1 = SPI.transfer(0x00);
  
  digitalWrite(ADXL355_CS_PIN, HIGH);
  SPI.endTransaction();
  
  // Convert 20-bit two's complement
  int32_t z_raw = (z3 << 12) | (z2 << 4) | (z1 >> 4);
  if (z_raw & 0x00080000) {
    z_raw |= 0xFFF00000; // Sign extend
  }
  
  // Convert to g (assuming +-2g range = 256000 LSB/g)
  float z_g = (float)z_raw / 256000.0; 
  return z_g;
}

// --------------------------------------------------------
// [4] UTILITY FUNCTIONS
// --------------------------------------------------------
float getSafeFrequency(float requested_freq) {
    if (resonant_freq == -1) return requested_freq; // No resonance found or not calibrated
    
    // If requested frequency is within +/- 2Hz of resonant frequency, avoid it
    if (abs(requested_freq - resonant_freq) <= 2.0) {
        if (requested_freq >= resonant_freq) {
            return resonant_freq + 3.0; // Push above resonance
        } else {
            return resonant_freq - 3.0; // Push below resonance
        }
    }
    return requested_freq;
}

// --------------------------------------------------------
// [5] REAL-TIME CONTROL LOOP (1kHz ISR)
// --------------------------------------------------------
void IRAM_ATTR onTimer() {
  portENTER_CRITICAL_ISR(&timerMux);
  
  // 1. Read Sensor
  float z_g = readADXL355_Z();
  
  // 1-1. Double integration to displacement
  // Remove DC offset using EMA filter
  static float accel_dc = 0.0;
  accel_dc = 0.999 * accel_dc + 0.001 * z_g;
  float accel_ac_g = z_g - accel_dc;
  
  // Convert to m/s^2
  current_z_accel = accel_ac_g * 9.80665;
  
  // Leaky integration to velocity (m/s)
  static float vel = 0.0;
  vel = 0.99 * vel + current_z_accel * 0.001;
  current_z_vel = vel;
  
  // Leaky integration to displacement (m)
  static float disp = 0.0;
  disp = 0.99 * disp + vel * 0.001;
  
  current_z_disp = disp * 1000000.0; // Convert to micrometers
  
  // 1-2. Amplitude Envelope Detection (EMA of absolute value * pi/2)
  static float disp_envelope = 0.0;
  disp_envelope = 0.99 * disp_envelope + 0.01 * abs(current_z_disp);
  measured_amplitude_um = disp_envelope * 1.5708; // 1.5708 is roughly pi/2
  
  if (current_state == STATE_RUNNING) {
      // 1-3. PID Control Loop (Only active during normal running state)
      float error = setpoint_amplitude_um - measured_amplitude_um;
      pid_integral += error * 0.001;
      
      // Anti-windup
      if (pid_integral > 500.0) pid_integral = 500.0;
      else if (pid_integral < -500.0) pid_integral = -500.0;
      
      float derivative = (error - pid_prev_error) / 0.001;
      pid_prev_error = error;
      
      float pid_output = (pid_kp * error) + (pid_ki * pid_integral) + (pid_kd * derivative);
      
      // Apply PID to target_amplitude (only if soft-start has mostly finished)
      if (current_amplitude >= 10.0) {
          target_amplitude += pid_output * 0.001; // slow adjustment
          if (target_amplitude > 127.0) target_amplitude = 127.0;
          if (target_amplitude < 10.0) target_amplitude = 10.0;
      }
      
      // 2. Soft-start & Tracking Logic (Ramp up/down amplitude)
      if (current_amplitude < target_amplitude) {
        current_amplitude += AMPLITUDE_STEP;
        if (current_amplitude > target_amplitude) current_amplitude = target_amplitude;
      } else if (current_amplitude > target_amplitude) {
        current_amplitude -= AMPLITUDE_STEP;
        if (current_amplitude < target_amplitude) current_amplitude = target_amplitude;
      }
  } else if (current_state == STATE_CALIBRATION) {
      // During calibration, use a fixed, low target amplitude
      target_amplitude = 30.0; 
      if (current_amplitude < target_amplitude) {
        current_amplitude += AMPLITUDE_STEP * 2.0; // Faster ramp for sweep
      } else if (current_amplitude > target_amplitude) {
        current_amplitude -= AMPLITUDE_STEP * 2.0;
      }
  } else if (current_state == STATE_ACTIGRAPHY_SLEEP) {
      // In sleep mode, motor is off. Monitor sensor for baby movement.
      target_amplitude = 0.0;
      current_amplitude = 0.0;
      
      // Calculate variance (activity level)
      actigraphy_variance = 0.99 * actigraphy_variance + 0.01 * abs(current_z_disp);
      
      if (actigraphy_variance > THRASHING_THRESHOLD_UM) {
          last_movement_time = millis();
      }
  } else {
      // INIT state
      current_amplitude = 0;
  }
  
  // 3. Generate Sine Wave
  // phase_increment = 2 * PI * Frequency * dt (dt = 0.001s for 1kHz)
  phase_increment = TWO_PI * current_frequency * 0.001;
  phase += phase_increment;
  if (phase >= TWO_PI) {
    phase -= TWO_PI;
  }
  
  // 4. Calculate DAC Output (8-bit: 0~255)
  // DC Offset = 128, Amplitude = current_amplitude (0~127)
  int dac_value = 128 + (int)(current_amplitude * sin(phase));
  
  // Constrain bounds
  if (dac_value > 255) dac_value = 255;
  if (dac_value < 0) dac_value = 0;
  
  // 5. Output to VCA Amplifier
  dacWrite(DAC_OUTPUT_PIN, dac_value);
  
  portEXIT_CRITICAL_ISR(&timerMux);
}

// --------------------------------------------------------
// [6] MAIN SETUP & LOOP
// --------------------------------------------------------
void setup() {
  Serial.begin(115200);
  Serial.println("Majn Smart Bassinet - Booting...");

  // Initialize Sensor
  initADXL355();
  Serial.println("ADXL355 Initialized.");
  
  // Initialize Timer Interrupt (Core 1)
  // Timer 0, Prescaler 80 (80MHz/80 = 1MHz -> 1us tick)
  timer = timerBegin(0, 80, true);
  timerAttachInterrupt(timer, &onTimer, true);
  // Alarm every 1000 ticks = 1ms = 1kHz sample rate
  timerAlarmWrite(timer, 1000, true);
  timerAlarmEnable(timer);
  
  Serial.println("1kHz Control Loop Started.");
  
  // Transition to calibration state
  current_state = STATE_CALIBRATION;
  Serial.println("Starting FRF Auto-Calibration...");
}

void runCalibrationSweep() {
    float max_amp = 0;
    int max_freq_index = 0;
    
    for (int freq = SWEEP_START_FREQ; freq <= SWEEP_END_FREQ; freq++) {
        current_frequency = (float)freq;
        delay(500); // 0.5초 대기하며 안정화 및 데이터 수집
        
        int index = freq - SWEEP_START_FREQ;
        // ISR에서 계산되는 measured_amplitude_um을 가져옴
        sweep_data[index] = measured_amplitude_um; 
        
        Serial.print("Sweep [");
        Serial.print(freq);
        Serial.print("Hz] Amp: ");
        Serial.println(sweep_data[index]);
        
        if (sweep_data[index] > max_amp) {
            max_amp = sweep_data[index];
            max_freq_index = index;
        }
    }
    
    // 단순 최대값을 공진 주파수로 설정 (개선 가능: 평균 대비 임계치 초과 여부 확인 등)
    resonant_freq = max_freq_index + SWEEP_START_FREQ;
    
    // 평균 대비 피크가 유의미한지 확인 (예: 평균의 1.5배 이상인가?)
    float sum = 0;
    for(int i=0; i<36; i++) sum += sweep_data[i];
    float avg = sum / 36.0;
    
    if (max_amp > avg * 1.5) {
        Serial.print(">> RESONANCE DETECTED at ");
        Serial.print(resonant_freq);
        Serial.print("Hz (Amp: ");
        Serial.print(max_amp);
        Serial.println(" um) <<");
    } else {
        Serial.println(">> No significant resonance detected. <<");
        resonant_freq = -1; // 무시할 수준
    }
    
    // 캘리브레이션 종료 후 절전/모니터링 상태로 전환
    current_frequency = getSafeFrequency(45.0); // 45Hz 기본값 설정
    current_state = STATE_ACTIGRAPHY_SLEEP;
    Serial.println("Calibration Complete. Entering ACTIGRAPHY_SLEEP mode (Motor OFF, Sensor ON).");
}

void loop() {
  if (current_state == STATE_CALIBRATION) {
      runCalibrationSweep();
  } else if (current_state == STATE_ACTIGRAPHY_SLEEP) {
      // Monitor actigraphy state
      if (millis() - last_movement_time < 1000 && last_movement_time != 0) {
          // Movement detected recently! Transition to RUNNING state for soothing.
          Serial.println(">> INFANT THRASHING DETECTED! Starting preemptive soothing vibration. <<");
          setpoint_amplitude_um = 20.0; // Start with gentle soothing
          current_frequency = getSafeFrequency(40.0);
          current_state = STATE_RUNNING;
          last_movement_time = 0; // Reset
      }
      
      Serial.print("[SLEEP MODE] Actigraphy Variance: ");
      Serial.println(actigraphy_variance);
      delay(1000);
      
  } else if (current_state == STATE_RUNNING) {
      // Core 0: Handle high-level tasks, AI serial commands, or Wi-Fi here.
      // The control loop runs independently in the background via ISR.
      
      // 시리얼 명령이 있을 경우 처리 (예: "F45.0 A50.0\n", "STOP\n")
      if (Serial.available() > 0) {
          String cmd = Serial.readStringUntil('\n');
          cmd.trim();
          
          if (cmd == "STOP") {
              Serial.println("Received STOP command. Entering ACTIGRAPHY_SLEEP mode.");
              current_state = STATE_ACTIGRAPHY_SLEEP;
          } else if (cmd.startsWith("F")) {
              int a_index = cmd.indexOf('A');
              if (a_index > 0) {
                  float req_freq = cmd.substring(1, a_index).toFloat();
                  float req_amp = cmd.substring(a_index + 1).toFloat();
                  
                  // 공진 주파수를 회피하여 설정
                  current_frequency = getSafeFrequency(req_freq);
                  setpoint_amplitude_um = req_amp;
                  
                  Serial.print("Command applied -> Freq: ");
                  Serial.print(current_frequency);
                  Serial.print(", Setpoint: ");
                  Serial.println(setpoint_amplitude_um);
              }
          }
      }
      
      Serial.print("[RUNNING] Freq: ");
      Serial.print(current_frequency);
      Serial.print(" Hz | Target Amp: ");
      Serial.print(target_amplitude);
      Serial.print(" | Meas Amp: ");
      Serial.print(measured_amplitude_um);
      Serial.print(" | Setpoint: ");
      Serial.println(setpoint_amplitude_um);
      
      delay(1000); // 1초마다 상태 출력
  }
}
