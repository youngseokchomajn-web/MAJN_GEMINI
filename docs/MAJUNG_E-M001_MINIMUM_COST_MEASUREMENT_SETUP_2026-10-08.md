# MAJUNG E-M001 최소비용 측정 셋업 및 진행안

작성일: 2026-10-08
상태: E-M001 실행 준비안
목적: MAJUNG의 실제 접촉면 진동을 정량적으로 측정하기 위한 최소비용 셋업을 확정하고, 이후 E-M002/E-M003 및 의료연구 단계의 물리적 자극 정의를 위한 기준 데이터를 확보한다.

## 1. 이번 단계의 결정

현재는 고가 오실로스코프나 전문 DAQ를 먼저 구매하지 않는다.

1차 측정은 디지털 3축 MEMS 가속도센서 + MCU/USB 데이터로거를 중심으로 구성한다.
- 탐색/디버깅 목적: 저가 MEMS 센서 사용 가능
- 최종 물리량 기준화: 가능하면 저잡음 센서/검증된 DAQ로 업그레이드
- 스마트폰 센서는 정량 검증 장비가 아니라 보조적인 존재 확인용으로만 취급
- 멀티미터는 전원/배선 확인용으로 사용

이 결정은 기존 연구가 매트리스 표면의 실제 자극을 직접 측정했다는 점과 맞는다. Bloch-Salisbury 2009는 표면 변위를 직접 측정하고, 30–60 Hz 대역, RMS 변위, 공간 균일도, 침구/하중 영향, 인접 두부 위치의 음향을 별도로 기록했다.

## 2. 최소 측정 체인

MAJUNG
→ mattress/contact surface
→ accelerometer
→ MCU/USB logger
→ Mac
→ CSV
→ Python 분석

동시에

MAJUNG
→ acoustic output
→ microphone
→ audio recording
→ spectrum/dBA 보조 분석

으로 구성한다.

### 필수
- 3축 MEMS accelerometer 1개
- MCU 또는 USB 데이터 수집 장치 1개
- 고정용 얇은 테이프/양면테이프
- Mac
- 시험용 하중
- 현재 보유 멀티미터

### 권장
- 저잡음 accelerometer
- 별도 microphone
- 온도센서
- 기준 하중용 저울

## 3. 센서 선택

### A안: 저비용 탐색용
ADXL345 계열 breakout

장점:
- 3축 디지털 출력
- SPI/I2C
- ±2/4/8/16 g
- bandwidth 설정 가능
- MCU와 직접 연결 가능

단점:
- 저진폭 진동의 정밀 정량에는 한계가 있을 수 있음
- breakout 보드와 고정 방법이 측정에 영향을 줄 수 있음
- 의료연구용 검증장비로 바로 간주하지 않는다.

ADI 공식 자료에서 ADXL345는 3축 디지털 가속도계이며 SPI/I2C와 bandwidth 설정을 제공한다.

### B안: 권장 기준 센서
ADXL355 계열

장점:
- 20-bit ADC
- 저잡음 22.5 µg/√Hz 수준
- ±2/4/8 g
- SPI/I2C
- programmable digital filter
- 최대 약 4 kHz 데이터레이트 지원

따라서 30–60 Hz 수준의 저진폭 진동을 정량화하는 목적에는 ADXL345보다 훨씬 적합하다.

단, 센서 IC 자체의 가격과 주변 회로/DAQ 비용이 올라가므로 최초 탐색부터 반드시 이것을 사용할 필요는 없다.

## 4. 현재 판단

MAJUNG의 목표는 단순히 진동이 있는지 확인하는 것이 아니라 향후 다음 값을 정의하는 것이다.

- dominant frequency / frequency band
- acceleration RMS
- acceleration peak
- displacement estimate
- 위치별 편차
- 하중별 편차
- 침구별 편차
- ON/OFF 응답시간
- 장시간 안정성
- acoustic output

따라서 최종적으로는 저잡음 센서 기반 측정으로 올라가는 것이 맞다.

## 5. 센서 설치

최소 5개 위치를 정의한다.

- P1: actuator 중심
- P2: 종방향 +25%
- P3: 종방향 -25%
- P4: 횡방향 +25%
- P5: 횡방향 -25%

가능하면 이후 grid로 확장한다.

센서는 mattress/contact surface에 최대한 얇고 단단하게 고정한다.

센서 자체의 움직임이나 케이블 흔들림이 측정값에 들어가지 않도록 한다.

## 6. 하중 조건

최초에는 다음으로 시작한다.

- L0: 무하중
- L1: mattress + intended bedding
- L2: 대표 하중
- L3: worst-case distributed load

하중값은 기존 논문의 1–1.5 kg saline bag을 그대로 MAJUNG 기준으로 복사하지 않는다.

그 값은 기존 연구의 실험조건이지 MAJUNG의 실제 사용 하중을 의미하지 않는다.

## 7. 최초 측정 시퀀스

각 조건마다 다음 순서로 기록한다.

1. sensor zero 확인
2. ambient vibration 기록
3. MAJUNG OFF 10 s
4. command ON
5. vibration onset 기록
6. steady state 60 s
7. command OFF
8. decay/end 기록
9. 최소 3회 반복
10. 조건 변경
11. 동일 절차 반복

가능하면 장기 안정성 확인을 위해 핵심 조건에서 10분 연속 운전도 수행한다.

## 8. 동기화 이벤트

향후 임상연구와 연결할 수 있도록 최초부터 공통 timestamp를 사용한다.

- T0 recording start
- T1 command ON
- T2 measured vibration onset
- T3 stable vibration
- T4 command OFF
- T5 measured vibration decay/end

후속 인간 연구에서는 여기에

- T6 fuss onset
- T7 settling
- T8 caregiver intervention

을 추가할 수 있다.

## 9. 분석

### 진동
- time waveform
- FFT/PSD
- dominant frequency
- RMS acceleration
- peak acceleration
- position-to-position ratio
- load-to-load ratio
- repeatability CV

### 변위
단순 단일 주파수에 가까운 신호에서는

x_RMS = a_RMS / (2πf)^2

관계를 사용할 수 있다.

다만 stochastic/broadband 신호에서는 단일 주파수 식을 그대로 적용하지 않고 frequency-domain 변환 또는 직접 변위센서를 사용한다.

따라서 논문에서 보고된 'μm displacement'와 MAJUNG의 측정값을 비교할 때 계산방법을 명시한다.

### 음향
- ambient level
- ON level
- spectrum
- 가능하면 dBA

단순 스마트폰 dB 앱 값은 calibrated acoustic measurement로 취급하지 않는다.

## 10. E-M001 판정 게이트

E0 — Detectability
- ON/OFF가 측정 데이터에서 명확히 구분되는가?

E1 — Repeatability
- 동일 조건 반복 측정값이 안정적인가?

E2 — Load characterization
- 하중에 따른 출력 변화가 정량화되는가?

E3 — Spatial characterization
- 위치별 출력 편차가 확인되는가?

E4 — Acoustic characterization
- 진동과 함께 발생하는 음향을 별도로 측정할 수 있는가?

E5 — Configuration freeze
- prototype hardware / firmware / mattress / bedding / sensor setup이 재현 가능하게 기록되는가?

E0~E5를 통과한 뒤 E-M004에서 'MAJUNG Stimulation Envelope v1.0'을 정의한다.

## 11. 기존 근거와의 연결

Bloch-Salisbury 2009는 실제 mattress surface에서 30–60 Hz 자극과 0.021 mm RMS displacement를 확인했고, 표면 공간 균일도와 bedding/load 영향, 두부 인접 위치의 acoustic level까지 측정했다. 이는 MAJUNG E-M001/E-M002의 직접적인 측정 설계 precedent로 사용한다.

단, 2009년의 ±2% spatial uniformity나 0.021 mm RMS를 MAJUNG의 안전 기준 또는 목표값으로 복사하지 않는다.

Prapela/FDA 자료 역시 vibration displacement/frequency, patient-weight effect, stimulation uniformity, auditory sound level 등을 bench verification 항목으로 다룬다. 따라서 MAJUNG도 software command만 기록하지 않고 실제 전달된 physical output을 측정하는 방향으로 유지한다.

## 12. 비용 최소화 원칙

지금 단계에서 우선순위는:

1. accelerometer + logger
2. 센서 고정/재현성
3. 시험 하중
4. microphone
5. temperature
6. 고급 DAQ/전문 교정장비

순서다.

오실로스코프는 현재 반드시 필요한 장비가 아니다.

전기적인 PWM/구동파형 자체를 확인하는 단계가 필요해지면 그때 추가한다.

## 13. 절대 하지 않을 것

- 스마트폰 센서만으로 의료 수준의 진동값을 확정하지 않는다.
- 논문의 30–60 Hz를 MAJUNG의 안전범위로 선언하지 않는다.
- 논문의 10–21 μm 수준을 MAJUNG 목표 출력으로 그대로 복사하지 않는다.
- command level을 actual delivered vibration으로 간주하지 않는다.
- 진동 측정 결과를 곧바로 '진정 효과'로 해석하지 않는다.
- 공학적 반복성 결과를 임상적 안전성으로 확대하지 않는다.

## 14. 다음 단계

E-M001 측정 셋업 확정
→ 실제 prototype 측정
→ raw CSV 저장
→ Python 분석
→ E-M002 조건 매트릭스
→ E-M003 worst-case/surrogate
→ MAJUNG Stimulation Envelope v1.0
→ 의료연구자에게 제공할 연구 패키지 작성

이 문서는 장비 구매보다 먼저 측정 목적과 데이터 구조를 고정하기 위한 문서다.
