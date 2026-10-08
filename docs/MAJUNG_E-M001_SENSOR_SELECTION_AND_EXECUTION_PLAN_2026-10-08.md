# MAJUNG E-M001 Sensor Selection & Execution Plan — 2026-10-08

## 1. Decision

현재 병목은 '어떤 연구를 할 것인가'가 아니라 **MAJUNG mattress contact surface에 실제로 어떤 진동이 전달되는지 측정하는 것**이다.

따라서 고가 DAQ를 먼저 구매하지 않고, 저비용 prototype measurement → 정량 measurement 순으로 진행한다.

## 2. Sensor decision

### Quantitative reference: ADXL355

ADXL355는 3-axis digital MEMS accelerometer이며 20-bit ADC, SPI/I2C, programmable digital filtering을 제공한다. ±2/4/8 g range를 지원하고 저잡음 특성이 명시되어 있다. citeturn0search0turn0search1

ADI datasheet의 대표 noise density는 ±2 g에서 22.5 µg/√Hz이며, output data rate/filter 설정을 함께 고려해야 한다. citeturn0search24turn0search7

따라서 MAJUNG의 저진폭 vibration characterization에는 ADXL355급 센서가 적합한 기준 장비 후보로 판단한다.

### Exploratory sensor

ADXL345급 저가 module은 존재 확인/대략적 waveform 탐색용으로 사용할 수 있으나, ADXL355와 동일한 측정 품질로 취급하지 않는다.

## 3. Immediate execution order

### E-M001-A — sensor procurement
1. ADXL355 evaluation/breakout option 확인
2. MCU/USB logging path 확보
3. thin sensor mounting method 준비
4. 기존 multimeter는 전원/배선 확인에만 사용

ADI는 EVAL-ADXL355-PMDZ와 PC/MCU 연결용 evaluation ecosystem을 제공한다. citeturn0search0turn0search2

### E-M001-B — bench validation
센서를 MAJUNG에 연결하기 전에:
- stationary zero recording
- known orientation gravity check
- 10 s OFF
- 60 s ON
- 10 s OFF
- 3 repeats

를 수행한다.

목적은 센서 자체의 offset/noise와 MAJUNG vibration을 분리하는 것이다.

### E-M001-C — contact-surface characterization

첫 시험은 다음 조건만 사용한다.

- mattress configuration: intended prototype
- load: representative distributed dummy/load
- sensor: center P1
- output: current prototype default setting
- duration: 60 s ON
- repeats: ≥3

추가로 P2/P3/P4/P5 위치를 같은 조건에서 측정한다.

### E-M001-D — load/bedding matrix

이후:
- L0 no load
- L1 bedding only
- L2 representative load
- L3 conservative/worst-case distributed load

와 bedding configuration을 교차시켜 load dependence를 확인한다.

## 4. Data to save

각 run마다 다음 metadata를 반드시 저장한다.

run_id
timestamp
hardware_revision
firmware_revision
stimulation_command
stimulation_level
sensor_model
sensor_position
load_condition
bedding_condition
sampling_rate
filter_setting
raw_xyz
derived_acceleration_rms
peak_acceleration
frequency_spectrum
temperature
acoustic_measurement_reference

원본 CSV는 수정하지 않고, 분석 결과는 별도 파일로 생성한다.

## 5. Analysis

1. time waveform
2. FFT/PSD
3. dominant frequency band
4. RMS acceleration
5. peak acceleration
6. ON/OFF detectability
7. run-to-run CV
8. position ratio
9. load ratio

가능한 경우 acceleration에서 displacement를 계산하되, 단일 주파수에 가까운 경우에만 단순 변환을 적용한다. broadband/stochastic output은 frequency-domain 방식 또는 직접 displacement measurement를 별도로 검토한다.

## 6. Decision gates

### E0 — Detectability
ON과 OFF를 측정 데이터만으로 구분할 수 있는가?

### E1 — Repeatability
동일 조건 반복에서 waveform/spectrum/RMS가 재현되는가?

### E2 — Load dependence
load/bedding 변화가 출력에 의미 있는 변화를 만드는가?

### E3 — Spatial distribution
center와 edge/longitudinal/lateral position 사이의 출력 차이를 정량화할 수 있는가?

### E4 — Acoustic coupling
진동 ON이 infant-head-equivalent 위치에서 측정 가능한 acoustic output을 발생시키는가?

### E5 — Configuration freeze
측정 결과를 바탕으로 의료연구자가 검토할 수 있는 stimulation envelope v1.0을 정의할 수 있는가?

## 7. Stop rules

다음 중 하나라도 발생하면 인간 대상 시험으로 넘어가지 않는다.

- vibration output을 신뢰성 있게 측정할 수 없음
- 동일 조건 반복성이 낮음
- load에 따라 출력이 예측 불가능하게 변함
- edge/center variation이 아직 설명되지 않음
- acoustic output이 평가되지 않음
- hardware/firmware revision이 고정되지 않음

## 8. Important boundary

이 문서의 측정값은 의료적 안전 한계가 아니다.

기존 논문에서 보고된 30–60 Hz, 10–21 µm 등의 값을 MAJUNG의 목표값이나 안전값으로 복사하지 않는다.

먼저 MAJUNG의 실제 출력 envelope를 측정하고, 그 결과를 의료연구자에게 전달한 뒤 human study 조건을 결정한다.

## 9. Next action

현재 가장 합리적인 다음 행동은 **센서 구매 후 실제 prototype 측정**이다.

연구질문을 더 늘리거나 문헌을 무한히 확장하는 것보다 E0~E5를 통과시키는 것이 다음 의사결정에 더 큰 정보를 제공한다.
