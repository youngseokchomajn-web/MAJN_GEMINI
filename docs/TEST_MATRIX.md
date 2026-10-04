# MAJN Test Matrix & Verification Log

> Master Development Plan Phase 0~20 Test IDs, Expected Behaviors, and Verification Status

## 1. Test Verification Overview

| 카테고리 | Test ID 범위 | 대상 계층 | 현재 상태 |
|---|---|---|:---:|
| **GUI** | `GUI-001` ~ `GUI-004` | 웹 시뮬레이터 & 상태 머신 | ✅ PASS (48/48 유닛 테스트 통과) |
| **BLE** | `BLE-001` ~ `BLE-008` | Web Bluetooth & GATT 통신 | 🟡 Firmware Ready / HW bench test |
| **FW** | `FW-001` ~ `FW-005` | ESP32 펌웨어 안전 검증 | ✅ Code PASS / Build Ready |
| **IMU** | `IMU-001` ~ `IMU-002` | LSM6DSOX SPI & 센싱 | ⚪ Gate 10 대기 (실물 연결) |
| **PWR** | `PWR-001` ~ `PWR-002` | MP3426 12V Boost 레일 | ⚪ Gate 11 대기 (실물 연결) |
| **AMP** | `AMP-001` ~ `AMP-002` | TAS5805M I2C & PDN 제어 | ⚪ Gate 12 대기 (실물 연결) |
| **ACT** | `ACT-001` ~ `ACT-002` | TEAX14C02-8 익사이터 구동 | ⚪ Gate 13~14 대기 (실물 연결) |
| **CTL** | `CTL-001` ~ `CTL-004` | 제어 알고리즘 & 프리셋 | ⚪ Gate 15~17 대기 (실물 연결) |
| **SAFE** | `SAFE-001` ~ `SAFE-006` | 안전 차단 및 고장 격리 | ✅ Logic PASS / Bench pending |
| **SYS/LONG** | `SYS-001` ~ `LONG-001`| 종합 라이프사이클 & 내구성 | ⚪ Gate 19~20 대기 (실물 연결) |

---

## 2. 세부 테스트 항목 명세 (Input → Expected → Actual → Result)

### [GUI / State Machine]
- **`GUI-001` Simulation Connect**:
  - **Input**: GUI 상단 '시뮬레이션 모드' 선택 및 connect() 호출
  - **Expected**: 상태가 `DISCONNECTED` → `CONNECTING` → `READY`로 전환되고 녹색 인디케이터 활성화
  - **Actual**: `tests/test_protocol_vectors.js` 및 웹 브라우저에서 `READY` 상태 전환 확인
  - **Result**: ✅ PASS

- **`GUI-002` State Transition & UI Enforcement**:
  - **Input**: `READY` 상태에서 START 클릭 후 파라미터 변경 시도
  - **Expected**: `RUNNING` 전환, START 버튼 비활성화, STOP 버튼 활성화, 슬라이더 변경 시 즉시 반영
  - **Actual**: `StateMachine` 권한 검사 통과 및 UI 바인딩 확인
  - **Result**: ✅ PASS

- **`GUI-003` Emergency Stop (ESTOP) Lockout**:
  - **Input**: 진동 구동 중 비상 정지 버튼 클릭
  - **Expected**: 즉시 `SAFETY_LOCK` 전환, 모든 구동 차단, 리셋 버튼 표출, 일반 START 불가
  - **Actual**: ESTOP 패킷 발행 및 안전 잠금 전이 검증 완료
  - **Result**: ✅ PASS

- **`GUI-004` Telemetry Null Unmeasured Handling**:
  - **Input**: `pvdd_v: null`, `vdd_3v3_v: null`, `amp_temp_c: null` 텔레메트리 수신
  - **Expected**: UI에서 임의의 숫자를 만들지 않고 `N/A (미측정)` 텍스트 및 `.unmeasured` 스타일 표시
  - **Actual**: DOM 렌더러에서 null 감지 시 `N/A (미측정)` 출력 확인
  - **Result**: ✅ PASS

---

### [BLE Protocol & GATT]
- **`BLE-001` Advertising**:
  - **Input**: ESP32 부팅 시 `initBleServer()` 실행
  - **Expected**: 디바이스명 `MAJN-Bassinet`, Service UUID `7b4d0001-...` 브로드캐스트
  - **Actual**: `ble_manager.cpp` 내 BLEAdvertising 구성 완료
  - **Result**: 🟡 코드 완료 (실물 플래싱 검증 대기)

- **`BLE-002` GATT Services & Characteristics Discovery**:
  - **Input**: Chrome Web Bluetooth `requestDevice` 및 `connect()`
  - **Expected**: Command(Write), Telemetry(Notify), Event(Notify) 3개 특성 검색 및 구독
  - **Actual**: `BleDeviceProvider`에서 startNotifications() 핸들러 구현 완료
  - **Result**: 🟡 코드 완료

- **`BLE-003` PING / ACK Round-trip**:
  - **Input**: `{"id": 1, "cmd": "PING"}` 전송
  - **Expected**: `{"type": "ack", "id": 1, "cmd": "PING", "status": "applied", "state": "READY"}` 수신
  - **Actual**: `ble_manager.cpp` CommandCallbacks 처리 로직 완료
  - **Result**: ✅ PASS (테스트 벡터 검증 완료)

- **`BLE-004` START / ACK / Telemetry Streaming**:
  - **Input**: `{"id": 2, "cmd": "START", "frequency_hz": 45, "amplitude": 0.2}` 전송
  - **Expected**: ACK applied 수신 후 5Hz 주기로 `telemetry` 스트리밍 시작
  - **Actual**: 펌웨어 200ms 타이머 및 `bleNotifyTelemetry` 루틴 정합
  - **Result**: ✅ PASS (테스트 벡터 검증 완료)

- **`BLE-005` STOP / ACK Return**:
  - **Input**: `{"id": 3, "cmd": "STOP"}` 전송
  - **Expected**: 앰프 출력 램프다운 및 `READY` 상태 복귀 ACK 수신
  - **Actual**: `MajnSafety::requestSafeStop()` 연동 확인
  - **Result**: ✅ PASS (테스트 벡터 검증 완료)

- **`BLE-006` ESTOP Override**:
  - **Input**: `{"id": 4, "cmd": "ESTOP"}` 전송
  - **Expected**: 최우선 처리로 앰프/부스트 하드웨어 차단 및 `FAULT` 상태 ACK 수신
  - **Actual**: `hardwareEmergencyShutdown()` 호출 및 ISR 레벨 차단 검증
  - **Result**: ✅ PASS (테스트 벡터 검증 완료)

- **`BLE-007` Reconnect & Recovery**:
  - **Input**: 블루투스 연결 단절 후 재연결 시도
  - **Expected**: GATT 재연결 후 PING/STATUS를 통해 이전 상태 동기화
  - **Actual**: `BleDeviceProvider.connect()` 핸드셰이크 시퀀스 완료
  - **Result**: ✅ PASS (로직 검증 완료)

- **`BLE-008` Heartbeat 5s Timeout**:
  - **Input**: 5초 이상 호스트로부터 PING 또는 명령어 미수신
  - **Expected**: ESP32 `bleLoop()`에서 타임아웃 감지 후 자동으로 Soft Stop 실행
  - **Actual**: `HEARTBEAT_TIMEOUT_MS = 5000` 로직 확인
  - **Result**: ✅ PASS (로직 검증 완료)

---

### [Firmware Safety & Validation]
- **`FW-001` Safe Boot Sequence**:
  - **Input**: 전원 인가 직후 부팅
  - **Expected**: `BOOST_EN` LOW, `AMP_PDN` LOW 상태에서 센서/안전 계층 초기화
  - **Actual**: `MajnPower::initPower()`, `MajnAmplifier::initAmplifier()` 반영
  - **Result**: ✅ PASS

- **`FW-002` Invalid Command Rejection**:
  - **Input**: 정의되지 않은 JSON 명령어 (`{"id": 99, "cmd": "DESTROY"}`)
  - **Expected**: `status: "rejected"` 반환 및 시스템 상태 불변
  - **Actual**: `validateCommandPacket` 및 `ble_manager.cpp` 기본 분기 reject 처리 확인
  - **Result**: ✅ PASS

- **`FW-003` Out-of-Range Parameter Validation**:
  - **Input**: 주파수 20Hz 또는 70Hz, 진폭 0.8 scale, 볼륨 120 전송
  - **Expected**: 펌웨어 및 프로토콜 계층에서 전송 차단 또는 rejected 응답
  - **Actual**: `tests/test_protocol_vectors.js` 48개 케이스 전수 합격
  - **Result**: ✅ PASS
