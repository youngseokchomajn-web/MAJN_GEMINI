# MAJN Fault Matrix & Safety Isolation Specification

> Comprehensive Failure Mode, Detection, Protective Action, and Recovery Rules

## 1. Fault Matrix Summary

| 고장 분류 | 원인 (Root Cause) | 감지 방법 (Detection) | 즉각 조치 (Firmware Action) | GUI 상태 및 표시 | 복구 절차 (Recovery) |
|---|---|---|---|---|---|
| **BLE 단절** | 무선 통신 두절 / 브라우저 닫힘 | `gattserverdisconnected` 이벤트 | `requestSafeStop()` (램프다운) | `DISCONNECTED` 표시 | 재연결 후 PING 동기화 |
| **하트비트 타임아웃** | 호스트 프로세스 정지 (5초 무응답) | `millis() - gLastClientActivity > 5000` | 즉시 소프트 스톱 진동 정지 | `TIMEOUT` 경고 로그 출력 | 호스트 PING 수신 시 해제 |
| **비상 정지 (ESTOP)** | 사용자 수동 비상정지 조작 | 호스트 ESTOP 패킷 수신 | 즉시 부스트(12V) OFF, 앰프 PDN LOW | `SAFETY_LOCK` / 빨간색 경고 | 명시적 비상해제(리셋) 명령 |
| **하드웨어 충격 감지** | 영유아/외력에 의한 1.5g 초과 충격 | LSM6DSOX INT1 핀 RISING 인터럽트 | `safetyLockISR()` 즉각 전원 차단 | `FAULT` / 경고음 및 알림 | 전원 재인가 또는 물리 리셋 |
| **I2C 버스 결함** | TAS5805M 통신 두절 / ACK 미수신 | I2C 트랜잭션 에러 반환 | 앰프 PDN LOW, 안전 정지 | `AMP_FAULT` 알림 | 시스템 재부팅 |
| **과열 (Thermal)** | 앰프 칩셋 온도 한계 초과 | TAS5805M Fault 레지스터 | 앰프 Mute 및 부스트 OFF | `OVERHEAT` 경고 | 온도 하강 확인 후 재가동 |
| **연속 운전 시간 초과** | 영유아 진동 노출 기준 (30분 초과) | `millis() - activeStateStartTime > 30분` | 안전 스톱 (램프다운 후 대기) | `READY` 복귀 및 안내 | 사용자가 재시작 명령 시 인가 |
| **비정상 명령 수신** | 파라미터 범위 이탈 (예: 70Hz, scale 0.8) | 프로토콜 검증기 입력 필터링 | 패킷 거부 (`status: rejected`) | 에러 로그 표출 | 규격 내 파라미터 재전송 |

---

## 2. 하드웨어 긴급 차단(Hardware Shutdown) 계통도

```
[비상 사태 감지: ESTOP / 1.5g 충격 / 과열]
                     │
                     ▼
             safetyLockISR()
                     │
         ┌───────────┴───────────┐
         ▼                       ▼
    BOOST_EN = LOW          AMP_PDN = LOW
(MP3426 12V PVDD 즉각 차단) (TAS5805M 하드웨어 Mute)
         │                       │
         └───────────┬───────────┘
                     ▼
           [익사이터 출력 즉각 0W]
```

## 3. 안전 우선순위 (Precedence)
1. **ESTOP / 하드웨어 ISR**: 모든 작업과 태스크를 무시하고 즉각적인 전원 차단 수행.
2. **센서 이상 및 통신 타임아웃**: 안전 스톱(Soft Stop)을 통해 진동 서서히 차단.
3. **일반 제어 명령 (START, STOP, 설정)**: 안전 잠금 상태에서는 수락되지 않고 거부(`rejected`/`fault`) 처리됨.
