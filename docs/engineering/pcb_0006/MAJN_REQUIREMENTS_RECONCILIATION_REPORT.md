# [요구사항 조정 보고서] MAJN PCB #0006 — 12대 기준선 vs 15대 확장 요구사항 정합성 감사 및 조정 보고서
(MAJN PCB #0006 Requirements Reconciliation & Traceability Alignment Report)

- **문서 식별자**: `MAJN_REQUIREMENTS_RECONCILIATION_REPORT`
- **리비전**: v1.0
- **작성 일자**: 2026-11-05
- **책임 주체**: Antigravity (시스템 엔지니어링 에이전트)
- **감사 대상**: DOC03 원본 요구사항(12종) vs PCB #0006 확장 요구사항(15종)

---

## 1. 개요 및 조정 배경

선행 엔지니어링 명세서(DOC03)는 **12대 필수 요구사항(`REQ-P0-01` ~ `REQ-P0-05`, `REQ-P1-01` ~ `REQ-P1-07`)**을 정의하고 있었다. 그러나 커밋 `a591717`에서 작성된 `PCB_0006_SYSTEM_REQUIREMENTS.md` 및 `PCB_0006_REQUIREMENTS_TRACEABILITY_MATRIX.csv`에는 총 **15개 요구사항**이 기재되어 있었으며, 자동 검증 스크립트는 12개만 검사하여 "12대 완비"로 출력되는 수량적 괴리가 발생했다.

본 문서는 추가된 3개 요구사항의 출처와 근거를 명확히 규명하고, 기존 12개 기준선과의 관계를 체계화하여 요구사항 관리의 단일 진실 공급원(SSOT)을 확립한다.

---

## 2. 12대 핵심 기준선 vs 15대 확장 요구사항 1:1 전수 대조표

| 요구사항 ID | 분류 구분 | 요구사항 요약 | DOC03 원본 상태 | PCB #0006 확장 상태 | 변경 사유 및 승인 필요 여부 |
|:---:|:---:|:---|:---:|:---:|:---|
| **REQ-P0-01** | Core Baseline | TAS5805M PDN 하드웨어 디폴트 LOW | 10k 풀다운 (Pin 12) | 동일 (Free GPIO 분리) | **유지 (확정 기준선)** |
| **REQ-P0-02** | Core Baseline | 부스트-PVDD 분리 점퍼 (`R_ISO1` 2512 0Ω)| 직결 격리 점퍼 | 동일 (5A 정격 점퍼) | **유지 (확정 기준선)** |
| **REQ-P0-03** | Core Baseline | 부스트 무부하 블리더 저항 (`R_BLEED`) | 1.5k 1206 저항 | 동일 (무부하 오버슈트 방어)| **유지 (확정 기준선)** |
| **REQ-P0-04** | Core Baseline | BTL 출력 역기전력 보호 어레이 | BTL 서지 클램프 | 동일 (차동 RC 스너버 표준) | **유지 (확정 기준선)** |
| **REQ-P0-05** | Core Baseline | 전체 시스템 최대 소비전력 10W 제한 | 10W 전력 상한 | 동일 (VBUS 2A 리미터 연계) | **유지 (확정 기준선)** |
| **REQ-P0-06** | **Extended Candidate**| **USB-C 표준 양방향 CC1/CC2 5.1kΩ 풀다운** | **미정의** | **신규 제안 (P0 필수 보호)** | **[신규 1]** C-to-C 케이블 기동 불능 결함(DISC-08) 해소 필수.<br>$\rightarrow$ **Gate G2 승인 대상** |
| **REQ-P1-01** | Core Baseline | VBUS 입력 전류 측정 션트 패드 (50mΩ) | 50mΩ 션트 패드 | 동일 (Kelvin 센싱 적용) | **유지 (확정 기준선)** |
| **REQ-P1-02** | Core Baseline | PVDD 앰프 공급 전류 션트 패드 (20mΩ)| 20mΩ 션트 패드 | 동일 (Kelvin 센싱 적용) | **유지 (확정 기준선)** |
| **REQ-P1-03** | Core Baseline | 진동자 4개 출력 커넥터 규격화 (2.0mm) | 2.0mm 2-pin 커넥터 | 동일 (2S2P 16Ω 결선 확정) | **유지 (확정 기준선)** |
| **REQ-P1-04** | Core Baseline | 주요 신호 전용 테스트 포인트 (DFT) | 루프형 TP 패드 | 동일 (차동 OUT TP 포함) | **유지 (확정 기준선)** |
| **REQ-P1-05** | Core Baseline | PVDD MLCC 정격 35V 이상 승격 (1210) | 35V X7R 승격 | 동일 (DC-bias 72% 유지) | **유지 (확정 기준선)** |
| **REQ-P1-06** | Core Baseline | L1 인덕터 포화전류 $I_{\text{sat}} \ge 7.0\text{A}$ 승격 | $I_{\text{sat}} \ge 7.0\text{A}$ | 동일 (MWPA7070 7.5A 선정) | **유지 (확정 기준선)** |
| **REQ-P1-07** | Core Baseline | I2C 버스 하드웨어 리셋 구조 | 하드웨어 버스 리셋 | 동일 (N-ch FET 스위칭) | **유지 (확정 기준선)** |
| **REQ-P1-08** | **Extended Candidate**| **3.3V LDO 전원 안정도 벌크 MLCC 보강** | **미정의** | **신규 제안 (P1 신뢰성)** | **[신규 2]** ESP32 WiFi 피크 전류 시 드롭아웃 방어.<br>$\rightarrow$ **Gate G2 승인 대상** |
| **REQ-P1-09** | **Extended Candidate**| **RF 외장 안테나 매칭 및 기구 연계** | **미정의** | **신규 제안 (P1 규제/RF)**| **[신규 3]** -32UE u.FL 안테나 미체결 통신 불량 해소.<br>$\rightarrow$ **Gate G2 승인 대상** |

---

## 3. 신규 3개 요구사항의 출처 및 승인 판정

1. **`REQ-P0-06` (USB-C Dual CC 5.1kΩ 독립 풀다운)**:
   - **출처**: Phase 0 감사에서 확인된 결함 `DISC-08` (CC1 Open, CC2 SBU2 오결선으로 인한 표준 Type-C 케이블 기동 불가).
   - **위상**: 기판에 전원이 공급되지 않는 치명적 물리 결함을 해소하는 필수 항목이므로, P0 필수 요구사항으로 배정함이 타당함.
2. **`REQ-P1-08` (3.3V LDO 22µF 벌크 캡 및 IMU 비드 필터)**:
   - **출처**: FMEA `FM-09` (ESP32 WiFi/BLE 피크 송신 시 3.3V 드롭아웃 및 센서 통신 노이즈 방어).
3. **`REQ-P1-09` (외장 2.4GHz FPC 안테나 및 기구 연계)**:
   - **출처**: Phase 0 `DISC-12` 및 FMEA `FM-12` (ESP32-WROOM-32UE u.FL 리셉터클에 외장 안테나 미체결 시 통신 거리 급락 방어).

---

## 4. 자동 검증 스크립트(`requirements_traceability_checker.py`) 개선 결과

스크립트를 v2.0으로 개선하여:
- **Core Baseline (12종)**: 12/12 100% 완비 확인.
- **Extended Proposed (3종)**: 3/3 제안 확인.
- 총 15개 요구사항에 대한 구현/검증 상태와 양방향 추적성을 분리 집계하도록 수정 완료.
- 향후 Gate G2 심사에서 Chief Authority가 신규 3종을 공식 승인하면 15대 요구사항이 차기 단일 기준선으로 통합 확정됨.
