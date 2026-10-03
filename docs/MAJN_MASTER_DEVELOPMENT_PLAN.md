# MAJN Master Development Plan

> GUI → BLE → PCB → IMU → Power → AMP → Exciter → Calibration → Closed-loop → Safety → Long-duration → Final Acceptance

## 1. 최종 목표
MAJN은 Mac Chrome GUI에서 ESP32 BLE 장치를 연결하고, 실제 IMU telemetry를 확인하며, 안전한 상태머신을 통해 4개 익사이터를 제어하는 시스템으로 완성한다.
최종 완료는 단순 진동 발생이 아니라 Command → Safety validation → Output → IMU feedback → Telemetry → Fault handling → Safe shutdown 전체 흐름의 검증이다.

## 2. 개발 원칙
1. GUI는 하드웨어 구현을 직접 알지 않는다.
2. Simulation과 BLE는 동일한 DeviceProvider 계약을 사용한다.
3. BLE Protocol을 먼저 동결한다.
4. 미측정 telemetry는 숫자를 만들지 않고 null/N/A로 표시한다.
5. 실제 하드웨어는 하나씩 붙인다.
6. ESTOP, disconnect, timeout, fault는 일반 명령보다 우선한다.
7. 모든 Phase에 진입조건과 완료 Gate를 둔다.
8. 실제 측정값은 시험기록으로 남긴다.
9. 기능 단위로 작게 커밋한다.

## 3. 전체 Phase
| Phase | 목표 | 완료 Gate |
|---|---|---|
| 0 | 코드/문서 정합성 | command/state/range 일치 |
| 1 | GUI 구조 | Simulation 정상/오류 흐름 |
| 2 | DeviceProvider | GUI가 구현 세부사항을 모름 |
| 3 | Simulation 검증 | regression 통과 |
| 4 | BLE Protocol v1 | schema/version/range 동결 |
| 5 | BLE-only firmware | ESP32 BLE build/통신 통과 |
| 6 | Mac Chrome ↔ ESP32 | 핵심 command 왕복 통과 |
| 7 | BLE 예외/안전 | disconnect/timeout/reconnect 통과 |
| 8 | GUI/BLE Freeze | 상위계층 동결 |
| 9 | 실제 PCB BLE | 무부하 BLE 통과 |
| 10 | 실제 IMU | 실제 telemetry 통과 |
| 11 | Power/BOOST | PVDD/startup/shutdown 통과 |
| 12 | TAS5805M | I2C/AMP/fault 통과 |
| 13 | Exciter 1 | 저출력/열/전류 범위 확보 |
| 14 | Exciter 4 | 4채널 안정성 확보 |
| 15 | Calibration | command↔physical output 데이터 확보 |
| 16 | Closed-loop | feedback 제어 검증 |
| 17 | Preset | 실제 출력 기반 preset 확정 |
| 18 | Safety/Fault | fault matrix 통과 |
| 19 | Long-duration | 반복/장시간 시험 완료 |
| 20 | Final Acceptance | 전체 lifecycle 통과 |

## 4. Phase 0 — 현재 코드/문서 정합성
### 작업
- GUI/BLE/firmware 현재 구현 전체 점검
- BLE Protocol v1과 실제 command 비교
- SET_VIBRATION과 SET_FREQUENCY/AMPLITUDE의 역할 정리
- state 값과 GUI state mapping 통일
- frequency/amplitude/volume 범위 통일
- protocol/firmware version 필드 통일
- telemetry null/N/A 규칙 통일
- main.cpp의 BLE-only 경로와 실제 hardware 경로 분리
- 문서의 완료 체크 표시와 실제 검증 여부 분리
### 산출물
- Master Plan
- Protocol v1
- DeviceProvider contract
- Hardware/FW contract
- Test Matrix
- Fault Matrix
### Gate 0
문서와 코드가 서로 다른 command/state/range를 사용하지 않는다.

## 5. Phase 1 — GUI 제품 구조
### Device
- Simulation/BLE 선택
- Connect/Disconnect
- device name
- firmware/protocol
- connection state
### Control
- START / STOP / ESTOP
- Frequency / Amplitude / Volume
- Preset
### Telemetry
- State / Safety Lock
- IMU X/Y/Z
- PVDD / 3.3V / AMP temperature
- actuator status
### Diagnostics
- command log
- ACK log
- event log
- fault
- timeout
- reconnect
### Gate 1
Simulation에서 모든 UI control과 state transition을 재현한다.

## 6. Phase 2 — DeviceProvider
공통 API: connect, disconnect, start, stop, emergencyStop, setFrequency, setAmplitude, setVolume, setPreset, getStatus, onTelemetry, onEvent.
구현: SimulationDeviceProvider / BleDeviceProvider.
GUI 코드에서 BLE characteristic을 직접 호출하지 않는다.
### Gate 2
Provider를 바꿔도 GUI 핵심 로직을 수정하지 않는다.

## 7. Phase 3 — Simulation
### 정상
Connect → READY → parameter change → START → RUNNING → telemetry → STOP → READY.
### 오류
invalid value, ESTOP, disconnect, timeout, reconnect, fault.
### Gate 3
실물 장치 없이 정상/오류 사용 흐름 전체가 PASS한다.

## 8. Phase 4 — BLE Protocol v1
### Command
PING, STATUS, START, STOP, ESTOP, SET_FREQUENCY, SET_AMPLITUDE, SET_VOLUME, SET_PRESET.
SET_VIBRATION은 필요하면 compatibility command로 유지한다.
### ACK
id, cmd, status, state. status는 received/validated/applied/rejected/fault.
### Telemetry
protocol, firmware, uptime, state, safety_lock, frequency_hz, amplitude_scale, accel_g, pvdd_v, vdd_3v3_v, amp_temp_c.
### Validation
malformed JSON, unknown command, out-of-range value, protocol mismatch를 명시적으로 처리한다.
### Gate 4
GUI와 firmware가 Protocol 문서만 보고 동일하게 구현할 수 있다.

## 9. Phase 5 — ESP32 BLE-only Test Firmware
### 목적
실제 BOOST/TAS5805M/I2S/exciter를 전혀 구동하지 않고 BLE만 검증한다.
### Boot
BOOST_EN LOW, AMP_PDN LOW, I2S OFF, BLE ON, advertising ON.
### 명령
PING, STATUS, START, STOP, ESTOP, SET_FREQUENCY, SET_AMPLITUDE, SET_VOLUME, SET_PRESET.
START는 논리 상태 RUNNING만 시험하고 실제 출력은 발생시키지 않는다.
### 시험
advertising, GATT discovery, ACK, telemetry, disconnect, heartbeat timeout, reboot/reconnect.
### Gate 5
PlatformIO build 성공 + BLE-only 동작 확인.

## 10. Phase 6 — 실제 Mac Chrome ↔ ESP32
### 순서
1. BLE-only firmware upload
2. serial log 확인
3. Chrome GUI 실행
4. MAJN-Bassinet discovery
5. Connect
6. service/characteristic discovery
7. telemetry/event subscribe
8. PING/STATUS
9. START
10. SET_FREQUENCY
11. SET_AMPLITUDE
12. SET_VOLUME
13. SET_PRESET
14. STOP
15. ESTOP
16. Disconnect
17. Reconnect
### 반복
개발 중 최소 10회 연결/해제를 반복한다.
### Gate 6
핵심 command → ACK → GUI state 반영이 실제 ESP32에서 반복 성공한다.

## 11. Phase 7 — BLE 안정성/예외
시험: GUI 강제 종료, Chrome 탭 종료, ESP32 reboot, BLE disconnect, heartbeat timeout, telemetry timeout, malformed JSON, unknown command, out-of-range value, duplicate command, delayed ACK, reconnect, protocol mismatch.
기대 결과: 통신 이상 시 RUNNING을 정상상태로 유지하지 않고 safe state로 전환한다.
### Gate 7
각 장애의 Expected State와 Actual State가 일치한다.

## 12. Phase 8 — GUI/BLE Freeze
동결 대상: UUID, command schema, state, ACK, telemetry, Provider API, timeout, safety behavior, versioning.
### Gate 8
GUI/BLE integration checklist 전체 PASS.
이후 하드웨어 개발은 이 인터페이스를 깨지 않는다.

## 13. Phase 9 — 실제 PCB BLE
순서: PCB boot → BLE advertising → Chrome connect → command/ACK → telemetry → disconnect/reconnect.
이 단계에서는 BOOST/AMP/exciter를 켜지 않는다.
### Gate 9
실제 PCB에서 Phase 6~7을 통과한다.

## 14. Phase 10 — 실제 IMU
LSM6DSOX SPI init → WHO_AM_I → register configuration → raw X/Y/Z → g conversion → telemetry.
시험: 정지, 방향 변경, 이동, 작은 움직임, sampling stability, sensor fault.
### Gate 10
GUI가 실제 IMU값을 표시하고 sensor fault를 처리한다.

## 15. Phase 11 — Power / BOOST
익사이터 연결 전에 전원만 검증한다.
순서: 3.3V 확인 → BOOST OFF 확인 → BOOST enable → PVDD 상승 → 안정화 → 다음 단계 허용.
측정: VBUS, 3.3V, PVDD, startup time, shutdown time, idle/load current, transient/droop.
### Gate 11
실측값으로 safe operating range와 startup/shutdown sequence를 확정한다.

## 16. Phase 12 — TAS5805M
순서: I2C detect → configuration → standby → I2S → low-level output path → volume → fault/status → shutdown.
시험: normal init, repeated init, standby/play, stop, I2C failure, amplifier fault, thermal status.
### Gate 12
AMP startup/shutdown/fault가 firmware safety state와 연결된다.

## 17. Phase 13 — Exciter 1
순서: 최소 출력 → 제한 frequency → frequency sweep → amplitude sweep → IMU → current → PVDD → temperature → stop.
기록: frequency, command amplitude, measured acceleration, PVDD, current, temperature, time.
### Gate 13
1개 exciter의 safe operating envelope을 확보한다.

## 18. Phase 14 — Exciter 4
순서: 1 → 2 → 3 → 4.
각 단계에서 current, PVDD, temperature, IMU, mechanical balance, actuator 편차를 확인한다.
### Gate 14
4개 동시 출력에서 전원/열/기계 상태가 허용 범위에 있다.

## 19. Phase 15 — Calibration
frequency와 command amplitude별 실제 acceleration을 측정한다.
필요하면 frequency별 LUT 또는 calibration curve를 만든다.
### Gate 15
GUI amplitude가 실제 physical output과 연결된 데이터가 있다.

## 20. Phase 16 — Closed-loop Control
단계: open-loop baseline → sensor feedback → target definition → controller → gain tuning → overshoot/settling 확인 → limits → fault handling.
현재 임의 PID 값은 최종 제품값으로 취급하지 않는다.
### Gate 16
target과 actual output의 오차/응답특성을 측정하고 허용범위를 정의한다.

## 21. Phase 17 — Preset
Preset 필드: frequency, target amplitude, ramp-up, ramp-down, max runtime, output limit.
물리 calibration 결과를 기반으로 만든다.
### Gate 17
모든 preset이 검증된 안전 범위에서 동작한다.

## 22. Phase 18 — Safety/Fault
Fault source: BLE, watchdog, IMU, I2C, TAS5805M, PVDD, 3.3V, temperature, actuator, software state.
공통 경로: Fault → output disable/ramp-down → AMP_PDN LOW → BOOST LOW → SAFE/FAULT → recovery/reset.
### Gate 18
Fault Matrix의 모든 항목을 실제 또는 fault-injection 시험으로 검증한다.

## 23. Phase 19 — Long-duration
시험: 반복 START/STOP, reconnect, 각 preset, frequency 영역, amplitude 영역, 1 actuator, 4 actuators, 장시간 운전.
기록: start/end, command, state, IMU, PVDD, current, temperature, BLE, fault/event.
### Gate 19
모든 fault가 안전 정지하고 원인을 추적할 수 있다.

## 24. Phase 20 — Final Acceptance
정상 lifecycle: Power ON → Self Test → BLE Ready → GUI Connect → READY → Preset → START → Ramp-up → Closed-loop → Telemetry → STOP → Ramp-down → READY.
비정상 lifecycle: Fault/Disconnect/ESTOP → output OFF → AMP OFF → BOOST OFF → SAFE/FAULT.
### Final Gate
GUI, BLE, state machine, IMU, power, amplifier, 4 exciters, calibration, closed-loop, preset, safety, long-duration 전체 acceptance PASS.

## 25. 병렬 개발
지금부터 하드웨어와 무관하게 GUI state/diagnostics/ACK/reconnect, BLE schema/validation/timeout/version, firmware state/safety/hardware abstraction, protocol/state tests, 문서/test matrix/fault matrix를 병렬로 진행한다.

## 26. 최종 코드 구조
GUI: app.js, device_provider.js, simulation_provider.js, ble_provider.js, protocol.js, state_machine.js, diagnostics.js.
Firmware: main.cpp, ble_manager.*, ble_protocol.*, safety_manager.*, hardware_manager.*, imu_manager.*, power_manager.*, amplifier_manager.*, vibration_controller.*, calibration.*, telemetry.*.
main.cpp는 orchestration 중심으로 줄이고 기능별 manager로 분리한다.

## 27. Test ID
GUI-001 Simulation connect / GUI-002 state transition / BLE-001 advertising / BLE-002 GATT / BLE-003 PING-ACK / BLE-004 START-ACK / BLE-005 STOP-ACK / BLE-006 ESTOP / BLE-007 reconnect / BLE-008 timeout.
FW-001 safe boot / FW-002 invalid command / FW-003 range validation / FW-004 watchdog / FW-005 safety state.
IMU-001 initialization / IMU-002 telemetry / PWR-001 boost startup / PWR-002 PVDD stability / AMP-001 I2C / AMP-002 startup-shutdown / ACT-001 single exciter / ACT-002 four exciters.
CTL-001 frequency calibration / CTL-002 amplitude calibration / CTL-003 closed-loop / CTL-004 preset.
SAFE-001 BLE timeout / SAFE-002 IMU fault / SAFE-003 AMP fault / SAFE-004 thermal fault / SAFE-005 power fault / SAFE-006 ESTOP.
SYS-001 normal lifecycle / SYS-002 fault lifecycle / LONG-001 long-duration.
각 테스트는 Input → Expected → Actual → PASS/FAIL → Evidence → Commit으로 기록한다.

## 28. 커밋 전략
기능 단위로 작게 커밋하고 가능하면 각 커밋을 build 가능한 상태로 유지한다.
예: docs(master), refactor(gui), feat(ble), feat(fw), test(ble), feat(imu), feat(power), feat(amp), feat(actuator), feat(control), feat(safety), test(system), docs(test).

## 29. 지금부터 실행할 순서
1. Phase 0 정합성 검사
2. Protocol/GUI/firmware 불일치 수정
3. BLE-only build environment
4. BOOST/AMP/I2S 완전 비활성 BLE test path
5. GUI ACK/State/Diagnostics 정리
6. protocol test vectors
7. PlatformIO build
8. ESP32 flash
9. Mac Chrome 연결
10. 핵심 command round-trip
11. disconnect/timeout/reconnect
12. GUI/BLE freeze
13. 실제 PCB BLE
14. 실제 IMU
15. Power
16. TAS5805M
17. Exciter 1
18. Exciter 4
19. Calibration
20. Closed-loop
21. Preset
22. Safety/Fault
23. Long-duration
24. Final Acceptance

## 30. 현재 위치
현재 GUI/BLE 코드는 상당 부분 구현되어 있지만, 문서상 완료 표시와 실제 하드웨어 검증 결과는 구분한다.
현재 최우선은 Phase 0~8이다. 특히 실제 ESP32 BLE 반복 검증, BLE-only firmware 분리, Protocol/GUI/firmware 정합성, BLE exception test, GUI/BLE freeze가 남은 핵심 게이트다.
물리적인 BOOST/AMP/exciter bring-up은 GUI/BLE freeze 이후에 시작한다.