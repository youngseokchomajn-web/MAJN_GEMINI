# MAJUNG Physical-Output Measurement Readiness Audit — 2026-10-08 (corrected)

## 1. Audit result

현재까지 확인된 레포 evidence를 기준으로 보면 **LSM6DSOX는 실제 구현 하드웨어/firmware로 확인되지 않았다.**

Master Development Plan에는 Phase 10의 설계 대상으로 LSM6DSOX가 명시되어 있지만, 이것은 실제 장착/구현/telemetry의 증거가 아니다.

실제 코드 검색에서 다음 키워드의 구현 증거를 확인하지 못했다.

- LSM6DSOX / lsm6dsox
- LSM6
- IMU
- accel_g
- imu_manager
- imu_manager.cpp

따라서 이 문서의 이전 버전에서 LSM6DSOX가 현재 PCB에 존재한다고 전제했던 부분은 폐기한다.

## 2. Current hardware/measurement status

| 항목 | 현재 판정 | 증거 |
|---|---|---|
| Master Plan에 LSM6DSOX 설계가 있음 | YES | Phase 10 |
| 실제 PCB에 LSM6DSOX 장착 | **미확인** | BOM/실물 확인 필요 |
| LSM6DSOX firmware driver | **미확인** | 현재 코드 검색상 없음 |
| LSM6DSOX telemetry | **미확인** | 현재 코드 검색상 없음 |
| 실제 contact-surface vibration 측정 | NO | 아직 prototype measurement 전 |
| independent reference sensor | NO | 미측정 |
| MAJUNG stimulation envelope v1.0 | NO | physical output 미측정 |

## 3. Measurement hierarchy

앞으로 다음 세 가지를 분리한다.

### A. Design intent
Master Plan에 무엇을 넣으려고 했는가.

### B. Implementation evidence
PCB/BOM/firmware에 실제로 구현되어 있는가.

### C. Measurement evidence
실제 장치에서 측정값으로 검증되었는가.

특히 의료연구에 전달하는 physical-output 값은 **C. Measurement evidence**를 기준으로 한다.

## 4. 현재 올바른 측정 경로

현재는 internal IMU를 전제로 하지 않는다.

**MAJUNG prototype**
→ mattress/contact surface
→ external reference accelerometer
→ logger
→ raw CSV
→ analysis

병렬:

**MAJUNG controller**
→ command/state timestamp

별도:

**mattress/head-equivalent position**
→ microphone
→ acoustic recording

실제 PCB에 IMU가 나중에 확인되면 다음 관계를 추가한다.

**internal IMU ↔ external contact-surface reference**

## 5. External reference sensor role

ADXL355급 센서를 quantitative reference 후보로 유지한다.

ADXL345급 센서는 E0/E1 탐색용으로 사용할 수 있지만 최종 reference와 동일한 정밀도로 취급하지 않는다.

센서 선택보다 먼저 다음을 고정한다.

1. contact-surface 위치
2. 센서 고정법
3. MCU/USB logging path
4. sampling rate
5. timestamp 규격
6. raw-data format

## 6. Immediate bench sequence

### M0 — Sensor baseline
- stationary zero/noise
- gravity/orientation check
- ambient vibration
- acoustic baseline

### M1 — ON/OFF detectability
- OFF → ON → steady → OFF
- ≥3 repeats
- current prototype configuration
- contact-surface P1

### M2 — Spatial
- P1 center
- P2/P3 longitudinal ±25%
- P4/P5 lateral ±25%

### M3 — Load/bedding
- L0 no load
- L1 bedding only
- L2 representative distributed load
- L3 conservative/worst-case distributed load

### M4 — Acoustic/thermal
- infant-head-equivalent acoustic position
- ambient vs ON
- spectrum / dBA if calibrated measurement is available
- temperature trend

## 7. E-M001 gates

- **E0 Detectability:** ON/OFF가 실제 센서 데이터에서 구분되는가?
- **E1 Repeatability:** 동일 조건 반복 결과가 재현되는가?
- **E2 Load dependence:** 하중/침구 변화가 출력에 미치는 영향이 정량화되는가?
- **E3 Spatial distribution:** 위치별 출력 편차가 설명되는가?
- **E4 Acoustic coupling:** 진동과 동반되는 음향 출력이 측정되는가?
- **E5 Configuration freeze:** hardware/firmware/mattress/bedding/sensor setup이 재현 가능하게 고정되는가?

E5 이후에만 **MAJUNG Stimulation Envelope v1.0**을 정의한다.

## 8. Safety boundary

이 audit는 의료 안전성 평가가 아니다.

측정값이 낮거나 반복성이 좋다는 사실만으로 인간 대상 시험의 안전성이 확보되는 것은 아니다.

FDA가 실제 therapeutic vibrational mattress pad의 분류에서 별도의 clinical/performance 및 device-specific requirements를 두고 있는 점도 이 구분을 뒷받침한다. Prapela의 FDA De Novo authorization은 일반 영아 수면 제품에 대한 authorization이 아니라 prenatal opioid exposure/NOWS라는 특정 임상 적응증에 한정된다. citeturn0search0turn0search3

## 9. Decision rule

다음 원칙을 고정한다.

> **계획에 있음 ≠ 구현됨 ≠ 측정됨 ≠ 임상적으로 안전함 ≠ 임상적으로 유효함**

각 단계의 evidence를 별도 상태로 기록한다.

## 10. Current next action

문헌 단계는 freeze한다.

다음 병목은 **실제 MAJUNG prototype의 contact-surface physical output 측정**이다.

순서는:

**prototype 확인 → external sensor baseline → E0 → E1 → E2/E3 → E4 → E5 → stimulation envelope → medical researcher review**

LSM6DSOX는 실제 PCB/BOM/firmware에서 존재가 확인될 때만 measurement path에 추가한다.
