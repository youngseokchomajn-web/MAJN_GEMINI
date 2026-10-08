# MAJUNG LSM6DSOX Reality Check — 2026-10-08

## 결론

현재 GitHub 레포의 default branch를 실제 코드 검색으로 대조한 결과, **LSM6DSOX가 실제 구현되어 있다는 증거를 찾지 못했다.**

검색 대상:
- LSM6DSOX / lsm6dsox
- LSM6
- IMU
- accel_g
- imu_manager
- imu_manager.cpp

모두 코드 검색 결과가 없었다.

따라서 현재 상태를 다음과 같이 정정한다.

| 항목 | 현재 판정 |
|---|---|
| Master Plan에 LSM6DSOX 계획이 있음 | YES |
| 실제 PCB에 LSM6DSOX 장착 확인 | NO EVIDENCE |
| firmware LSM6DSOX driver 확인 | NO |
| 실제 IMU telemetry 확인 | NO |
| 실제 측정 데이터 확인 | NO |

## 중요한 의미

이전 문서에서 LSM6DSOX를 '현재 PCB에 이미 들어가 있는 센서'처럼 표현한 부분은 설계계획과 실제 구현을 혼동한 것이다.

따라서 LSM6DSOX를 이용한 선행 측정은 현재 단계에서 전제하지 않는다.

## 현재 올바른 측정 경로

실제 physical-output characterization은 외부 reference sensor를 기준으로 시작한다.

MAJUNG prototype
→ mattress/contact surface
→ external accelerometer
→ logger
→ raw CSV
→ Python analysis

병렬로:
MAJUNG controller
→ command/state timestamp

그리고 별도로:
mattress/head-equivalent position
→ microphone
→ acoustic recording

## ADXL355 decision

ADXL355급 센서는 현재 계획대로 **external reference measurement 후보**로 유지한다.

단, 구매 전에 실제 PCB BOM/schematic/assembled board가 별도로 존재하는지 확인할 수 있다면 먼저 그것을 확인한다.

## 다음 Gate

### G-HW-0
현재 실제 PCB/BOM/schematic에서 IMU 존재 여부 확인.

- IMU 없음 → ADXL355 external reference로 바로 진행
- 다른 IMU 존재 → 해당 센서의 측정 가능성 검토
- LSM6DSOX 존재 → firmware/telemetry 구현 여부 별도 확인

### G-MEAS-1
external accelerometer로 prototype contact-surface ON/OFF 측정.

이 결과가 최초의 실제 physical-output evidence가 된다.

## Evidence rule

'계획에 있음'과 '실제 구현됨'을 서로 다른 상태로 기록한다.

앞으로 Master Plan의 Phase 완료 표시는 실제 build/measurement evidence가 있는 경우에만 PASS로 인정한다.
