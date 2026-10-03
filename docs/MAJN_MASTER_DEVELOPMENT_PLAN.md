# MAJN Master Development Plan

## 0. 목적

MAJN을 다음 흐름으로 완성한다.

GUI/Simulation → Mac Chrome ↔ ESP32 BLE → BLE 안정성/안전 → PCB BLE → 실제 IMU → 전원/BOOST → TAS5805M → 익사이터 1개 → 익사이터 4개 → 실제 진동 제어 → Calibration/Preset → Safety/Fault/장시간 시험 → 제품 수준 검증

핵심 원칙은 상위 계층을 먼저 완성하고 하위 하드웨어는 검증된 인터페이스 뒤에 순차적으로 붙이는 것이다.

## 1. 최종 완료 정의

### 소프트웨어
- Mac Chrome GUI에서 장치를 검색/연결/해제할 수 있다.
- GUI는 Simulation과 실제 BLE 장치를 동일한 DeviceProvider 인터페이스로 제어한다.
- Command → ACK → State → Telemetry 흐름이 일관된다.
- 잘못된 명령, timeout, disconnect, reboot, fault를 안전하게 처리한다.
- Firmware/Protocol version compatibility를 확인한다.

### 하드웨어
- ESP32 BLE가 안정적으로 동작한다.
- LSM6DSOX 실측 telemetry가 GUI에 표시된다.
- BOOST/PVDD가 명시된 순서와 한계 안에서 동작한다.
- TAS5805M startup/shutdown/fault 처리가 확인된다.
- 익사이터 1개에서 저출력부터 검증한다.
- 4개 동시 구동 시 전원/열/출력 안정성을 확인한다.

### 제어
- frequency/amplitude/volume/preset이 실제 출력과 대응한다.
- ramp-up/ramp-down이 안전하게 동작한다.
- IMU 기반 실제 진동 측정값을 이용해 calibration한다.
- 허용 출력 범위를 firmware에서 강제한다.

### 안전
- ESTOP은 정상 제어보다 항상 우선한다.
- BLE disconnect/heartbeat timeout 시 안전 정지한다.
- IMU/AMP/I2C/전원/열 fault를 감지하고 출력 차단한다.
- watchdog 및 재부팅 후 안전 상태로 시작한다.
- 장시간 시험 후에도 안전 정지 및 재기동이 가능하다.

## 2. Phase 0 — 기준선 및 요구사항 고정

작업:
1. 현재 GUI/BLE/firmware를 동결 기준으로 지정
2. 현재 구현과 Protocol 문서의 차이 제거
3. 기능별 완료 기준 정의
4. 테스트 ID 체계 정의
5. 실제 측정값과 simulation 값을 엄격히 구분

산출물:
- Master Development Plan
- BLE Protocol v1
- GUI state model
- DeviceProvider contract
- Hardware/Firmware interface matrix
- Test matrix

완료 기준: 문서와 코드가 서로 다른 명령/상태/범위를 갖지 않는다.

## 3. Phase 1 — GUI 제품 구조 완성

화면:
- Device: Simulation/ESP32 BLE, Connect/Disconnect, device name, firmware/protocol, connection status
- Control: START, STOP, ESTOP, Frequency, Amplitude, Volume, Preset
- Telemetry: State, Safety lock, IMU X/Y/Z, PVDD, 3.3V, amplifier temperature, actuator status
- Diagnostics: Event log, ACK log, fault, reconnect, timeout

상태:
- DISCONNECTED
- CONNECTING
- READY
- RUNNING
- FAULT
- SAFETY_LOCK

완료 기준: Simulation만으로 모든 정상/오류 UI 흐름을 재현할 수 있다.

## 4. Phase 2 — DeviceProvider 계약 고정

공통 API:
- connect()
- disconnect()
- start(params)
- stop()
- emergencyStop()
- setFrequency(hz)
- setAmplitude(scale)
- setVolume(percent)
- setPreset(name)
- getStatus()
- subscribeTelemetry()
- subscribeEvents()

Provider:
- SimulationDeviceProvider
- BleDeviceProvider

완료 기준: GUI가 Simulation/BLE 구현 세부사항을 알 필요가 없다.

## 5. Phase 3 — Simulation 검증

정상: connect → READY → START → RUNNING → parameter change → ACK/state update → STOP → READY

오류: ESTOP → FAULT/SAFETY_LOCK, disconnect → DISCONNECTED, timeout → safe state, invalid parameter → rejected, reconnect → READY

완료 기준: 실물 장치 없이 GUI 제품 사용 흐름 전체가 검증된다.

## 6. Phase 4 — BLE Protocol v1 동결

Command:
- PING
- STATUS
- START
- STOP
- ESTOP
- SET_FREQUENCY
- SET_AMPLITUDE
- SET_VOLUME
- SET_PRESET

SET_VIBRATION은 필요하면 compatibility command로 유지하되 GUI 기본 API는 개별 parameter 명령을 사용한다.

Response:
- ACK
- TELEMETRY
- EVENT
- FAULT

필수 규칙:
- 모든 command에 id
- ACK에 command/id/status/state
- 값 범위 firmware 검증
- unknown command → rejected
- malformed JSON → rejected
- protocol mismatch → connection rejected 또는 safe state
- telemetry 미측정 값은 null

완료 기준: GUI와 firmware가 이 문서만 보고 독립적으로 구현 가능하다.

## 7. Phase 5 — ESP32 BLE-only Test Firmware

실제 액추에이터를 사용하지 않는 단계.

부팅 상태:
- BOOST = OFF
- AMP_PDN = LOW
- I2S = OFF
- BLE = ON

검증:
- advertising
- GATT service
- characteristic discovery
- PING/STATUS
- 모든 command ACK
- telemetry notification
- disconnect
- heartbeat timeout
- reboot/reconnect

START가 들어와도 BLE test firmware에서는 실제 BOOST/TAS5805M/익사이터를 켜지 않는다.

완료 기준: ESP32를 BLE 통신 장치로만 사용하여 GUI/BLE 계층을 반복 검증할 수 있다.

## 8. Phase 6 — 실제 Mac Chrome ↔ ESP32

순서:
1. Discovery
2. Connect
3. Service discovery
4. Characteristic subscription
5. PING
6. STATUS
7. START
8. SET_FREQUENCY
9. SET_AMPLITUDE
10. SET_VOLUME
11. SET_PRESET
12. STOP
13. ESTOP
14. Disconnect
15. Reconnect

개발 중 최소 10회 반복 연결 시험을 실시하고 최종 횟수는 별도 시험계획으로 확정한다.

완료 기준: 실제 ESP32를 Chrome에서 반복 연결하고 핵심 command round-trip을 모두 통과한다.

## 9. Phase 7 — BLE 안정성/예외처리

시험:
- GUI 강제 종료
- Chrome 탭 종료
- BLE 신호 저하
- ESP32 reboot
- command timeout
- telemetry timeout
- malformed command
- out-of-range value
- duplicate command
- delayed ACK
- reconnect
- protocol mismatch

원칙: 통신 실패를 정상 RUNNING으로 간주하지 않는다.

완료 기준: 모든 통신 장애가 정의된 safe state로 귀결된다.

## 10. Phase 8 — GUI/BLE Freeze

동결 대상:
- UUID
- command schema
- state
- ACK
- telemetry
- Provider API
- safety behavior
- versioning

이후 하드웨어 개발은 이 인터페이스를 깨지 않는 방향으로 진행한다.

## 11. Phase 9 — PCB BLE 실물 연결

1. USB/ESP32 boot
2. BLE advertising
3. Chrome 연결
4. command/ACK
5. telemetry

아직 BOOST와 익사이터는 사용하지 않는다.

완료 기준: Phase 6~7 BLE 테스트를 실제 PCB에서 통과한다.

## 12. Phase 10 — 실제 IMU

LSM6DSOX:
1. SPI initialization
2. WHO_AM_I/초기화 확인
3. X/Y/Z raw
4. g 변환
5. telemetry
6. GUI graph

검증: 정지, 방향 변경, 작은 움직임, 진동 전/후, sampling stability.

IMU fault가 발생하면 출력 가능한 단계에서는 RUNNING을 유지하지 않는다.

완료 기준: GUI IMU가 simulation이 아닌 실제 센서값을 표시한다.

## 13. Phase 11 — BOOST / Power Bring-up

익사이터 연결 전 전원부터 검증한다.

BOOST OFF → enable → PVDD rise → stability 확인 → AMP enable

측정:
- VBUS
- 3.3V
- PVDD
- startup transient
- idle current
- shutdown behavior

산출물: power measurement table, startup/shutdown timing, safe operating limits.

완료 기준: 전원이 설계 범위 안에서 안정적으로 켜지고 꺼진다.

## 14. Phase 12 — TAS5805M

익사이터 없이 앰프 계층부터 검증한다.

작업:
- I2C communication
- device detection
- configuration
- PDN
- standby/play
- volume
- I2S
- fault/status
- thermal monitoring

순서: AMP OFF → initialization → standby → low-level output → stop → standby → shutdown

완료 기준: 앰프가 안전하게 startup/shutdown하고 fault 상태를 firmware가 인식한다.

## 15. Phase 13 — 익사이터 1개

시험 순서:
- 최소 출력
- 낮은 frequency
- frequency sweep
- amplitude 단계
- IMU 측정
- current
- PVDD
- amplifier temperature
- actuator 상태

목적: 명령값과 실제 물리 출력의 관계 측정.

완료 기준: 1개 익사이터의 안전 동작 범위와 calibration 데이터가 확보된다.

## 16. Phase 14 — 4개 익사이터

시험: 1개 → 2개 → 3개 → 4개, 동시 출력, 주파수별, 진폭별.

확인:
- 전원 droop
- PVDD stability
- amplifier temperature
- current
- mechanical balance
- actuator 편차

완료 기준: 4개 동작에서 전원/열/기계 상태가 허용 범위 안에 있다.

## 17. Phase 15 — 실제 진동 제어

현재 코드의 임의 PID 계수와 목표값을 제품값으로 취급하지 않는다.

수집 데이터:
- frequency
- command amplitude
- IMU acceleration
- estimated displacement
- PVDD
- current
- temperature
- time

주파수별 command scale → 실제 amplitude 관계를 측정하고 필요하면 LUT/보정식을 만든다.

완료 기준: GUI amplitude 값이 실제 물리 출력 기준으로 의미를 갖는다.

## 18. Phase 16 — Preset 설계

Preset 구조:
- frequency
- target amplitude
- ramp time
- max runtime
- output limit

물리 검증 이후 실제 출력 파라미터와 연결한다.

완료 기준: 각 preset의 실제 동작 범위와 안전 제한이 명확하다.

## 19. Phase 17 — Safety/Fault 완성

Software: watchdog, BLE timeout, command timeout, state machine, invalid parameter rejection

Sensor: IMU missing, impossible sensor value, sensor communication failure

Amplifier: I2C failure, amplifier fault, thermal fault

Power: PVDD abnormal, 3.3V abnormal, boost failure

User: ESTOP, STOP, disconnect

공통 결과:
Fault detected → output ramp/disable → AMP_PDN LOW → BOOST OFF → FAULT/SAFE → local recovery/reset

## 20. Phase 18 — 장시간/반복 시험

시험군:
- 반복 START/STOP
- 반복 BLE reconnect
- 최대 허용 출력
- 각 preset
- 저주파/고주파
- 1개/4개 actuator
- 장시간 운전

기록:
- 시작/종료 시간
- frequency
- amplitude
- current
- PVDD
- temperature
- fault
- BLE 상태
- IMU 상태

완료 기준: fault 발생 시 안전 정지하고 원인을 추적할 수 있는 로그가 남는다.

## 21. Phase 19 — 최종 제품 수준 검증

정상 시나리오:
Power ON → Self Test → BLE Ready → GUI Connect → READY → Preset 선택 → START → Ramp-up → Closed-loop control → Telemetry → STOP → Ramp-down → READY

비정상:
Fault / Disconnect / ESTOP → Output OFF → AMP OFF → BOOST OFF → FAULT/SAFE

완료 기준: 전체 시스템을 실제 장치에서 처음부터 끝까지 반복 검증한다.

## 22. 병렬 개발 가능 영역

하드웨어를 기다릴 필요가 없는 작업은 동시에 끝낸다.

A. GUI: UI, state machine, diagnostics, ACK 표시, fault, reconnect UX
B. BLE: schema, validation, ACK, telemetry, timeout, reconnect
C. Firmware: state machine, safety abstraction, hardware abstraction, BLE-only build mode
D. Test: simulation test, protocol test vectors, malformed packet, state transition test
E. Documentation: protocol, hardware/FW contract, test matrix, calibration data format

## 23. 최종 코드 구조 방향

bassinet_simulator/
- app.js
- device_provider.js
- simulation_provider.js
- ble_provider.js
- protocol.js
- state_machine.js
- diagnostics.js

인증준비/firmware/src/
- main.cpp
- ble_manager.*
- ble_protocol.*
- safety_manager.*
- hardware_manager.*
- imu_manager.*
- amplifier_manager.*
- power_manager.*
- vibration_controller.*
- calibration.*
- telemetry.*

main.cpp가 모든 기능을 직접 관리하지 않도록 단계적으로 분리한다.

## 24. 테스트 체계

테스트 ID 예시:
- GUI-001 Simulation connect
- BLE-001 Advertising
- BLE-002 GATT discovery
- BLE-003 PING/ACK
- BLE-004 START/ACK
- BLE-005 Disconnect
- FW-001 Safe boot
- FW-002 ESTOP
- IMU-001 Sensor initialization
- PWR-001 PVDD startup
- AMP-001 TAS5805M init
- ACT-001 Single exciter low output
- ACT-002 Four exciter output
- CTL-001 Frequency calibration
- CTL-002 Amplitude calibration
- SAFE-001 BLE timeout
- SAFE-002 IMU fault
- SAFE-003 AMP fault
- SAFE-004 Thermal fault
- LONG-001 Long-duration test

각 테스트는 Input → Expected → Actual → PASS/FAIL → Evidence → Commit 형태로 기록한다.

## 25. 커밋 전략

큰 기능을 한 커밋에 몰아넣지 않는다. 기능 단위로 커밋하고 가능하면 각 커밋을 빌드 가능한 상태로 유지한다.

예:
- docs(master): 전체 개발계획 확정
- refactor(gui): DeviceProvider contract 정리
- feat(gui): diagnostics state handling
- feat(ble): protocol validation
- feat(fw): BLE-only test mode
- test(ble): command ACK test vectors
- feat(fw): hardware abstraction
- feat(imu): LSM6DSOX manager
- feat(power): boost manager
- feat(amp): TAS5805M manager
- feat(actuator): single exciter control
- feat(control): vibration calibration
- feat(safety): fault manager
- test(system): integration test
- docs(test): final validation report

## 26. 현재 실행 순서

현재는 GUI/BLE 계층을 먼저 완성한다.

1. 전체 코드/Protocol 정합성 정리
2. BLE-only firmware
3. BLE test mode
4. GUI ACK/State/Diagnostics 보강
5. protocol test vectors
6. PlatformIO build
7. 실제 ESP32 BLE 연결
8. 반복 BLE test
9. GUI/BLE freeze
10. PCB BLE
11. IMU
12. Power
13. TAS5805M
14. Exciter 1
15. Exciter 4
16. Calibration
17. Closed-loop
18. Preset
19. Safety
20. Long-duration
21. Final validation

이 문서를 전체 개발 기준선으로 사용하며, 각 단계의 완료 기준을 충족한 뒤 다음 단계로 이동한다.
