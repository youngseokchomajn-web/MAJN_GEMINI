# Phase 1: 하드웨어 & 펌웨어 프로토타이핑 구체화 계획

본 문서는 `Future_Action_Plan.md`의 1단계 목표인 **VCA 및 ESP32 기반의 30~65Hz 폐루프(Closed-loop) 진동 제어 시스템**을 실제로 구현하기 위한 구체적인 설계 명세 및 펌웨어 개발 계획입니다.

---

## 1. 시스템 아키텍처 (System Architecture)

*   **메인 컨트롤러 (MCU)**: `ESP32` (듀얼 코어 활용, Wi-Fi/Bluetooth 통신 확장성 고려)
*   **피드백 센서**: `ADXL355` (초저소음 3축 MEMS 가속도 센서, 20-bit 분해능)
*   **액추에이터 (VCA)**: `Dayton Audio TT25-16` (선형 보이스 코일 액추에이터)
*   **증폭기 (Amplifier)**: `Wondom JAB3` (DSP 내장 오디오 앰프)

### 1.1 데이터 흐름 (Data Flow)
1. **Sensory Input**: 매트리스 하단에 부착된 ADXL355가 Z축(수직) 미세 가속도를 측정하여 ESP32로 전송 (SPI 통신).
2. **Processing (PID)**: ESP32가 가속도를 변위(Displacement)로 변환하고, 목표 변위(10~12μm)와의 오차를 계산하여 PID 제어량 산출.
3. **Actuation Output**: ESP32가 제어량이 반영된 30~65Hz 대역의 정현파(Sine wave)를 생성하여 Wondom JAB3 앰프로 전송. 앰프가 VCA를 구동.

---

## 2. 하드웨어 핀 맵핑 (Pin Mapping - ESP32)

| ESP32 핀 | 연결 대상 부품 | 통신 방식 / 기능 | 비고 |
| :--- | :--- | :--- | :--- |
| **GPIO 19** | ADXL355 (MISO) | SPI 통신 | 센서 데이터 수신 |
| **GPIO 23** | ADXL355 (MOSI) | SPI 통신 | 센서 설정 송신 |
| **GPIO 18** | ADXL355 (SCLK) | SPI 통신 | 클럭 신호 |
| **GPIO 5** | ADXL355 (CS) | SPI 통신 | 칩 셀렉트 (Chip Select) |
| **GPIO 25 (DAC1)** | Wondom JAB3 (Audio In) | Analog / I2S | 30~65Hz 정현파 오디오 신호 출력 |
| **GPIO 26** | Wondom JAB3 (Enable) | Digital Out | 앰프 ON/OFF 제어 (소프트 스타트 용도) |

---

## 3. 펌웨어 제어 로직 (Firmware Control Logic)

ESP32의 듀얼 코어(Core 0, Core 1)를 분리하여 데이터 처리 지연을 방지합니다.

*   **Core 0 (통신 및 상태 관리)**: 
    *   상위 시스템(AI 비전, 모바일 앱)과의 Wi-Fi/BLE 통신 담당.
    *   현재 상태(대기, 작동 중, 에러) 관리.
*   **Core 1 (실시간 제어 루프 - RTOS)**:
    *   **1kHz 타이머 인터럽트**: 매 1ms마다 ADXL355 데이터 리드.
    *   **필터링**: 저역통과필터(LPF)를 통해 고주파 기계 노이즈 제거.
    *   **PID 연산**: 계산된 변위를 바탕으로 Sine Wave의 진폭(Amplitude) 재조정.

---

## 4. 단계별 구현 마일스톤 (Milestones)

### Step 1: ADXL355 센서 연동 및 데이터 필터링 (Week 1)
*   ESP32와 ADXL355 간의 고속 SPI 통신 구현.
*   가속도 데이터를 변위(Displacement) 단위(μm)로 이중 적분하는 수치 해석 로직 작성.
*   DC 오프셋 제거 및 디지털 노이즈 필터 적용.

### Step 2: VCA 정현파 구동 및 앰프 제어 (Week 2)
*   ESP32의 DAC 채널을 통해 30Hz ~ 65Hz 사이의 부드러운 Sine Wave 출력 함수 구현.
*   급격한 소음 및 아기 놀람 방지를 위한 **소프트 스타트/스톱(Soft Start/Stop)** 램프(Ramp) 함수 적용 (진폭을 3초에 걸쳐 서서히 증가시킴).

### Step 3: PID 폐루프 제어 통합 (Week 3)
*   Step 1의 변위 피드백 데이터와 Step 2의 출력 기능을 결합하여 PID 컨트롤러 구현.
*   아기의 무게 변화나 움직임(외란)이 발생해도 진동판의 진폭이 10~12μm로 일정하게 유지되도록 Kp, Ki, Kd 게인(Gain) 튜닝.

### Step 4: 시제품 조립 및 FRF (주파수 응답) 테스트 (Week 4)
*   Sorbothane 댐퍼 위에 구성품을 조립.
*   실제 구동 시 목표 주파수(예: 45Hz)에서 기구적 공진이 발생하는지 확인하고, 발생 시 앰프의 DSP 노치 필터(Notch Filter)를 설정하여 공진 대역 회피.

---

### 💻 기초 펌웨어 코드 스켈레톤 (구조)

```cpp
#include <SPI.h>

// 핀 정의
const int CS_PIN = 5;
const int DAC_PIN = 25;

// PID 변수
float target_displacement = 10.0; // 10 μm
float current_displacement = 0.0;
float pwm_amplitude = 127.0; // 기본 출력

void setup() {
  Serial.begin(115200);
  
  // ADXL355 SPI 초기화
  pinMode(CS_PIN, OUTPUT);
  digitalWrite(CS_PIN, HIGH);
  SPI.begin();
  initADXL355();
  
  // 1kHz 타이머 인터럽트 설정 (제어 루프)
  setupTimerInterrupt();
}

void loop() {
  // Core 0: 통신 및 상태 모니터링 로직 (비동기 처리)
  delay(10);
}

// 1ms마다 실행되는 핵심 루프 (Core 1)
void IRAM_ATTR controlLoop() {
  // 1. 센서 읽기 (가속도)
  float accel = readADXL355_Z();
  
  // 2. 가속도 -> 변위 변환 및 필터링
  current_displacement = calculateDisplacement(accel);
  
  // 3. PID 연산
  float error = target_displacement - current_displacement;
  pwm_amplitude = updatePID(error);
  
  // 4. VCA로 Sine Wave 출력
  outputSineWave(pwm_amplitude);
}
```
