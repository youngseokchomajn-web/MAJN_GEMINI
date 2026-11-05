# [통합 시험 계획서] MAJN PCB #0006 — 펌웨어 및 하드웨어 통합 검증 계획서
(MAJN PCB #0006 Firmware & Hardware Integration Test Plan)

- **문서 식별자**: `PCB_0006_INTEGRATION_TEST_PLAN`
- **리비전**: v1.0
- **작성 일자**: 2026-11-05
- **책임 주체**: Antigravity (시스템 엔지니어링 에이전트)
- **적용 대상**: ESP32 펌웨어 및 PCB #0006 하드웨어 통합 시험

---

## 1. 개요 및 시험 원칙

본 문서는 하드웨어 변경(Free GPIO PDN 배정, MP3426 보호망, 2.0mm 커넥터)이 적용된 PCB #0006과 ESP32 펌웨어 간의 **기능적 동작 무결성, 통신 신뢰성, 비상 차단 응답성 및 장시간 안정성**을 체계적으로 검증하기 위한 통합 시험 절차를 수립한다.

> [!IMPORTANT]
> **하드웨어 실측과 소프트웨어 시뮬레이션의 분리 원칙**
> 테스트 스크립트(JS/Python) 통과 결과는 통신 프로토콜 정합성만을 증명하며, **실제 보드에서 오실로스코프로 전압/전류/파형을 계측하기 전까지는 하드웨어 검증을 완료(PASS)로 처리하지 않습니다.**

---

## 2. 5대 통합 시험 영역 및 테스트 케이스 매트릭스

| 시험 그룹 | 테스트 ID | 시험 항목 및 목적 | 입력 조건 및 절차 | 합격 판정 기준 (Pass Criteria) |
|:---|:---:|:---|:---|:---|
| **1. BLE 프로토콜** | **TC-INT-01** | 92개 프로토콜 벡터 검증 | `tests/test_protocol_vectors.js` 구동 | 92/92 벡터 100% PASS, 파라미터 경계값 거부 정상 |
| | **TC-INT-02** | BLE 무선 재연결 복구 | BLE 강제 단절 후 10초 내 재연결 | 진동 즉시 Safe-stop 감쇄 후 대기, 재연결 후 PING 응답 |
| **2. 전원/오디오 시퀀싱**| **TC-INT-03** | 앰프 기동 팝(Pop) 노이즈 | 전원 투입 및 START 명령 시 스코프 관측 | 기동 과도 전압 스파이크 $\le 0.5\text{V}$, 청감 팝 노이즈 전무 |
| | **TC-INT-04** | Free GPIO PDN 제어 검증 | GPIO13 HIGH/LOW 토글 시 PDN 응답 | $V_{\text{IL}} \le 0.4\text{V}$ (Low), $V_{\text{IH}} \ge 2.8\text{V}$ (High) 완전 정합 |
| **3. 능동 안전 루프** | **TC-INT-05** | 100ms Active Supervisor | I2C 라인 임의 단락/단선 발생 | 100ms 이내 `hardwareEmergencyShutdown()` 트리거, PVDD 0V |
| | **TC-INT-06** | 1.5g 비상 충격 차단 | 센서에 1.5g 이상 기계적 충격 인가 | GPIO34 ISR 즉시 발생, **$0.1\text{ms}$ 이내 부스트/앰프 차단** |
| **4. 폐루프 진동 제어** | **TC-INT-07** | 진동 세기 단조성(Monotonicity) | 볼륨 0.1부터 0.5까지 단계별 상승 | 가속도 센서 피크치(G)가 역전 없이 선형/단조 증가 |
| **5. 연속 운전 내구** | **TC-INT-08** | 30분 타이머 자동 정지 | 진동 지속 구동 후 경과 시간 측정 | 정확히 30분($1800\text{초} \pm 1\text{초}$) 도달 시 자동 램프다운 정지 |

---

## 3. 통합 시험 자동화 실행 절차

```bash
# 1. 프로토콜 검증 벡터 전수 실행 (92개 테스트)
node tests/test_protocol_vectors.js

# 2. 커맨드 파서 단위 테스트 실행
python3 tools/test_command_parser.py

# 3. 브링업 하드웨어 시리얼 로그 캡처
python3 tools/capture_boot.py
```
