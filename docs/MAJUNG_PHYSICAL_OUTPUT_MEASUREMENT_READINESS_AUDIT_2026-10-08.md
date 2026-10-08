# MAJUNG Physical-Output Measurement Readiness Audit — 2026-10-08

## 1. Audit result

현재 MAJN_GEMINI의 Master Development Plan을 실제 engineering plan과 대조했다.

기존 system architecture에는 **LSM6DSOX IMU telemetry**가 이미 Phase 10에 포함되어 있고, 이후 Phase 15에서 command amplitude ↔ physical acceleration calibration을 하도록 되어 있다.

그러나 이것만으로 E-M001을 완료했다고 볼 수 없다.

### 핵심 이유

**PCB/내부 IMU의 가속도 ≠ infant contact surface에서 전달되는 vibration**

센서 위치, PCB mounting, mechanical path, mattress compliance, load, bedding에 따라 실제 contact-surface output이 달라질 수 있기 때문이다.

따라서 기존 LSM6DSOX는 다음 용도로 유지한다.

- device internal telemetry
- actuator/control feedback 후보
- system fault/diagnostic signal
- repeatability monitoring

반면 E-M001의 reference measurement는 **mattress contact surface에 별도 external accelerometer를 직접 부착**하는 방식으로 분리한다.

## 2. Current architecture implication

기존 system flow:
Exciter → IMU → Calibration → Closed-loop

연구용 physical-output validation에서는 다음처럼 확장한다.

Exciter → mechanical path → mattress/contact surface → external reference accelerometer

그리고 병렬로:
PCB/LSM6DSOX → internal telemetry

두 데이터를 동시에 저장한다.

목적은 나중에:
internal IMU signal ↔ contact-surface reference
관계를 정량적으로 비교하는 것이다.

## 3. Sensor roles

| Sensor | 위치 | 역할 | E-M001 reference 여부 |
|---|---|---|---|
| LSM6DSOX | MAJN PCB | 내부 telemetry / feedback | NO |
| ADXL355급 | mattress contact surface | reference vibration measurement | YES |
| microphone | infant-head-equivalent position | acoustic output | YES |
| temperature sensor | device/mattress vicinity | thermal trend | YES |

LSM6DSOX를 버리는 것이 아니라 **measurement hierarchy를 분리**한다.

## 4. Immediate bench test

### Test M0 — system baseline

- MAJN power OFF
- external accelerometer zero/noise recording
- LSM6DSOX telemetry 상태 기록
- ambient acoustic recording
- 30–60 s baseline

### Test M1 — ON/OFF detectability

- prototype default output
- external accelerometer P1
- LSM6DSOX simultaneously recorded
- OFF → ON → steady → OFF
- ≥3 repeats

판정:
- external sensor에서 ON/OFF가 명확히 구분되는가?
- LSM6DSOX에서도 동일 event가 검출되는가?
- 두 sensor의 timestamp alignment가 가능한가?

### Test M2 — spatial measurement

동일 조건에서:
- P1 center
- P2/P3 longitudinal ±25%
- P4/P5 lateral ±25%

를 측정한다.

### Test M3 — load/bedding

- no load
- bedding only
- representative distributed load
- conservative/worst-case load

를 비교한다.

## 5. Data architecture

기존 firmware telemetry와 external measurement를 같은 run ID로 묶는다.

Minimum schema:

run_id
timestamp
firmware_revision
hardware_revision
command_state
command_frequency
command_amplitude
internal_imu_x/y/z
external_accel_x/y/z
sampling_rate
sensor_position
load_condition
bedding_condition
acoustic_level
temperature

원본 raw data는 보존한다.

Derived data는 별도 파일로 만든다.

## 6. Calibration relationship

M1~M3가 완료되면 다음 관계를 계산할 수 있다.

command amplitude → external contact-surface acceleration

그리고:

internal LSM6DSOX acceleration → external reference acceleration

이 관계가 충분히 안정적이면 이후 Phase 15 Calibration에서 internal IMU를 feedback sensor로 활용할 근거가 생긴다.

반대로 두 센서 사이 관계가 불안정하면 closed-loop 전에 mechanical/sensor placement를 다시 검토한다.

## 7. Important correction to previous plan

기존 계획에서 'ADXL355 + MCU/USB logger'를 바로 구매하는 것보다 먼저 해야 할 것은 **현재 PCB/firmware에서 LSM6DSOX telemetry가 실제로 얼마나 잘 기록되는지 확인하는 것**이다.

따라서 비용을 최소화하기 위해:

1. 기존 LSM6DSOX telemetry 확인
2. internal IMU raw/sample-rate/format 검증
3. 실제 actuator ON/OFF waveform 확인
4. external reference sensor 필요성 확인
5. 그 후 ADXL355급 sensor 구매

순서로 한다.

단, LSM6DSOX가 이미 PCB에 장착되어 있어도 E-M001의 최종 reference sensor를 대체하는 것으로 간주하지 않는다.

## 8. Decision gate

### G-IMU-0
LSM6DSOX raw telemetry가 안정적으로 수집되는가?

NO → firmware/telemetry 먼저 수정.

YES → G-IMU-1.

### G-IMU-1
LSM6DSOX에서 actuator ON/OFF와 dominant vibration component가 검출되는가?

NO → external sensor 측정으로 즉시 이동.

YES → external reference measurement와 cross-check.

### G-IMU-2
internal IMU와 contact-surface reference 사이 관계가 반복적으로 재현되는가?

YES → closed-loop 후보 sensor로 평가.

NO → external sensor를 reference로 유지하고 mechanical path를 추가 분석.

## 9. Safety boundary

이 audit는 의료 안전성 평가가 아니다.

측정값이 좋다고 해서 인간 대상 시험이 승인되는 것도 아니며, vibration output이 낮다고 해서 자동으로 안전하다고 판단하지 않는다.

이 단계의 목적은 오직:

**'우리가 실제로 영아에게 전달될 물리 자극을 정확히 알고 있는가?'**

를 확인하는 것이다.

## 10. Current next action

가장 먼저 **현재 LSM6DSOX telemetry 구현과 실제 firmware data path를 검증**한다.

그 결과를 확인한 뒤 external reference sensor를 붙이는 것이 가장 효율적이다.

이렇게 하면 이미 PCB에 들어가 있는 센서를 활용하면서도 의료연구에 필요한 independent physical-output measurement의 원칙을 유지할 수 있다.
