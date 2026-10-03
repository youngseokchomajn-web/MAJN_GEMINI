# MAJN GUI 개발 계획

## 1. 목표

MAJN GUI를 단순 시뮬레이터가 아니라 실제 ESP32 BLE 장치를 연결하고 제어할 수 있는 제품형 GUI로 완성한다.

우선 개발 범위는 **GUI + BLE 통신**까지다. 실제 PCB의 전원, 앰프, 익사이터 브링업은 GUI/BLE 계층이 검증된 이후 진행한다.

1차 목표 환경은 **Mac + Chrome + Web Bluetooth**다.

## 2. 개발 원칙

- GUI와 하드웨어를 직접 결합하지 않는다.
- GUI는 공통 DeviceProvider 인터페이스를 통해 장치를 제어한다.
- Simulation과 BLE는 같은 인터페이스를 구현한다.
- BLE Protocol을 먼저 명확히 정의하고 GUI와 ESP32가 동일한 계약을 사용한다.
- 실물 하드웨어를 연결하기 전에 PC ↔ ESP32 BLE 통신을 독립적으로 검증한다.
- 측정하지 않은 하드웨어 telemetry는 임의의 숫자로 표시하지 않고 null/미측정 상태로 표현한다.
- 안전 관련 명령(특히 ESTOP, disconnect, timeout)은 일반 제어보다 우선한다.

## 3. 전체 개발 순서

```
현재 코드/상태 고정
        ↓
GUI 기능·상태 정의
        ↓
DeviceProvider 인터페이스
        ↓
Simulation Provider 완성
        ↓
BLE Protocol v1 확정
        ↓
GUI 1차 완성 + Simulation 검증
        ↓
ESP32 BLE 테스트 펌웨어
        ↓
Mac Chrome ↔ ESP32 실제 BLE 연결
        ↓
Command / ACK / Telemetry 검증
        ↓
BLE 예외·안전 처리
        ↓
GUI/BLE 최종 완성
        ↓
[여기까지가 1차 개발 목표]
        ↓
실제 PCB BLE 연결
        ↓
실제 IMU
        ↓
BOOST / 전원
        ↓
TAS5805M
        ↓
익사이터 1개
        ↓
익사이터 4개
        ↓
실제 진동 제어 / Calibration / Preset
        ↓
Safety / 장시간 검증
```

## 4. Phase별 계획

### Phase 0 — 현재 상태 고정

현재 Simulation GUI, BLE Provider, ESP32 BLE 코드, BLE Protocol 문서를 기준점으로 고정한다.

**완료 기준**
- 기존 Simulation 기능이 깨지지 않음
- 현재 코드와 문서의 차이를 파악함
- 이후 변경사항은 기능 단위로 커밋함

### Phase 1 — GUI 기능 및 상태 정의

GUI에서 필요한 기능과 상태를 먼저 확정한다.

**주요 기능**
- 장치 검색/연결/해제
- 연결 상태
- 장치명 / firmware / protocol 정보
- START / STOP / ESTOP
- Frequency
- Amplitude
- Volume
- Preset
- IMU telemetry
- Power telemetry
- Temperature
- Safety 상태
- Fault
- Event log

**상태**
- DISCONNECTED
- CONNECTING
- CONNECTED
- READY
- RUNNING
- FAULT
- SAFETY_LOCK

**완료 기준**
- 각 UI 컨트롤이 어떤 상태에서 활성/비활성인지 정의됨
- 명령과 상태 변화가 명확함

### Phase 2 — DeviceProvider 인터페이스

GUI가 Simulation과 BLE 구현을 구분하지 않도록 공통 인터페이스를 만든다.

예상 API:
- connect()
- disconnect()
- start()
- stop()
- emergencyStop()
- setFrequency()
- setAmplitude()
- setVolume()
- setPreset()
- getStatus()
- telemetry/event callback

**완료 기준**
- GUI 코드가 특정 BLE 구현에 직접 의존하지 않음
- Simulation/BLE가 같은 명령 구조를 사용함

### Phase 3 — Simulation Provider 완성

실제 ESP32 없이 GUI 전체 기능을 검증할 수 있는 상태를 만든다.

**검증**
- START → RUNNING
- STOP → READY
- ESTOP → SAFETY_LOCK/FAULT
- frequency/amplitude/volume 변경
- telemetry 갱신
- IMU 그래프
- fault 표시
- disconnect 상태

**완료 기준**
- BLE 장치가 없어도 GUI의 주요 기능을 모두 테스트할 수 있음

### Phase 4 — BLE Protocol v1 확정

GUI와 ESP32 사이의 통신 계약을 고정한다.

**Command**
- PING
- STATUS
- START
- STOP
- ESTOP
- SET_FREQUENCY
- SET_AMPLITUDE
- SET_VOLUME
- SET_PRESET

**ESP32 → GUI**
- ACK
- TELEMETRY
- EVENT
- FAULT

**필수 정의**
- protocol version
- command schema
- ACK status
- telemetry schema
- state values
- timeout
- 범위/validation
- unsupported command 처리

**완료 기준**
- GUI와 ESP32가 별도 구현되어도 같은 protocol 문서만 보고 구현할 수 있음

### Phase 5 — GUI 1차 완성

Simulation Provider를 사용하여 GUI를 실제 제품 사용 흐름처럼 완성한다.

**화면**
- Device
- Control
- Status
- IMU
- Power/System
- Safety
- Event Log

**완료 기준**
- Simulation만으로 정상 사용 시나리오를 처음부터 끝까지 실행 가능
- UI 상태와 실제 command/state가 일관됨

### Phase 6 — ESP32 BLE 테스트 펌웨어

실제 PCB의 AMP/BOOST/IMU 기능에 의존하지 않는 BLE 통신용 상태를 구현한다.

초기 telemetry에서 아직 측정하지 않는 값은 null로 보낸다.

**검증 대상**
- advertising
- GATT service/characteristic
- PING
- STATUS
- START
- STOP
- ESTOP
- 설정 명령
- ACK
- test telemetry

**완료 기준**
- ESP32가 독립적으로 BLE 통신 장치로 동작함

### Phase 7 — Mac Chrome ↔ ESP32 실제 BLE 연결

실제 Web Bluetooth 연결을 검증한다.

**순서**
1. device discovery
2. GATT connection
3. service discovery
4. characteristic discovery
5. PING
6. ACK
7. STATUS
8. START/STOP/ESTOP
9. 설정 명령
10. telemetry notification

**완료 기준**
- 실제 ESP32를 Chrome에서 반복 연결/해제할 수 있음
- 모든 핵심 명령이 왕복 검증됨

### Phase 8 — BLE 안정성 및 안전 처리

정상 동작보다 예외 상황을 집중 검증한다.

**테스트**
- BLE disconnect
- ESP32 reboot
- ACK timeout
- telemetry timeout
- 잘못된 command
- 범위 밖 값
- protocol version mismatch
- firmware mismatch
- reconnect
- ESTOP

**완료 기준**
- 통신이 끊어져도 위험한 RUNNING 상태를 계속 유지하지 않음
- GUI와 ESP32가 모두 명확한 fault/safe 상태를 표시함

### Phase 9 — GUI/BLE 최종 완성

이 단계에서 GUI와 BLE 계층을 동결한다.

**완료 기준**

```
Mac Chrome
  ↓
Web Bluetooth
  ↓
ESP32
  ↓
Command / ACK
  ↓
Telemetry
  ↓
GUI 상태 반영
```

이 전체 흐름이 실제 장치로 반복 검증된다.

이 시점부터 **GUI/BLE 1차 개발 완료**로 정의한다.

## 5. 이후 실제 하드웨어 단계

GUI/BLE가 완료된 후에만 실제 PCB 기능을 붙인다.

### Phase 10 — PCB BLE
- ESP32 boot
- BLE advertising
- GUI 연결
- firmware/protocol 확인

### Phase 11 — 실제 IMU
- LSM6DSOX 초기화
- 실제 acceleration telemetry
- GUI graph 확인

### Phase 12 — Power / AMP
- BOOST_EN
- PVDD
- TAS5805M
- fault/temperature
- 안전한 startup/shutdown

### Phase 13 — Exciter 1개
- 저출력
- 주파수 단계 시험
- IMU 변화 확인
- thermal/current 관찰

### Phase 14 — Exciter 4개
- 4개 동시 출력
- 주파수/진폭별 동작
- 전원/앰프/열 상태 확인

### Phase 15 — 실제 제어 및 Calibration

실제 측정 결과를 바탕으로:
- frequency range
- amplitude limit
- ramp-up/down
- preset
- calibration
- output limit

을 결정한다.

처음부터 임의의 preset 값을 고정하지 않는다.

### Phase 16 — 최종 Safety / 장시간 검증

- BLE disconnect
- ESTOP
- watchdog
- I2C failure
- IMU failure
- amplifier fault
- thermal fault
- power fault
- 장시간 운전

후 안전 상태 복귀를 검증한다.

## 6. GUI/BLE 개발 완료 체크리스트

- [ ] GUI 기능/상태 정의
- [ ] DeviceProvider 인터페이스
- [ ] Simulation Provider
- [ ] BLE Protocol v1
- [ ] GUI 1차 구현
- [ ] ESP32 BLE 테스트 펌웨어
- [ ] Web Bluetooth 연결
- [ ] Command/ACK
- [ ] Telemetry
- [ ] START/STOP/ESTOP
- [ ] Disconnect/timeout
- [ ] Reconnect
- [ ] Version compatibility
- [ ] Event/Fault handling
- [ ] 반복 연결 테스트
- [ ] GUI/BLE 최종 동결

## 7. 현재 우선순위

현재는 **실물 브링업을 진행하지 않는다.**

다음 작업 순서는:

1. 현재 GUI/BLE 코드 점검
2. GUI와 BLE 사이의 DeviceProvider 구조 정리
3. BLE Protocol과 실제 코드의 불일치 제거
4. Simulation 기반 GUI 완성
5. ESP32 BLE 테스트 펌웨어 빌드/검증
6. Mac Chrome에서 실제 ESP32 연결
7. Command/ACK/Telemetry 전체 검증
8. BLE 예외/안전 처리
9. GUI/BLE 완료 선언
10. 그 이후 실제 PCB 브링업

이다.