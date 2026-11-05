# [자동화 커버리지 보고서] MAJN PCB #0006 — 자동 검증 파이프라인 커버리지 및 한계 보고서
(MAJN PCB #0006 Automated Validation Tool Suite Coverage & Scope Limitations Report)

- **문서 식별자**: `MAJN_AUTOMATED_VALIDATION_COVERAGE_REPORT`
- **리비전**: v1.0
- **작성 일자**: 2026-11-05
- **책임 주체**: Antigravity (시스템 엔지니어링 에이전트)
- **감사 대상**: 하드웨어 및 펌웨어 자동 검증 도구 5종

---

## 1. 개요 및 검증 원칙

자동화 검증 스크립트는 수작업 대조에서 발생하는 휴먼 에러를 방지하는 강력한 도구이지만, **"소프트웨어 스크립트 통과가 물리적 하드웨어의 안전성을 보장하지 않는다"**는 한계를 지닌다. 본 문서는 현재 운용 중인 5대 자동 검증 도구의 **검사 범위, 미검사 항목(한계점), 실패 조건, 그리고 하드웨어 실측과의 경계**를 명확히 정의한다.

---

## 2. 5대 자동 검증 도구별 정밀 커버리지 및 한계 명세

### 2.1 [TOOL-01] BOM vs CPL vs JSON 비교기 (`bom_cpl_comparator.py` v2.0)
* **검사 목적**: 제조 발주 BOM, SMT 배치 CPL, CAD 설계 JSON 간의 3자 형상 무결성 검증.
* **입력 파일**: `BOM_PCB1_revB_2026-07-09.csv`, `CPL_PCB1_revB_2026-07-09.csv`, `A_mcp_design_flow_v1.9.2_2026-07-08.json`.
* **검사 항목**:
  1. 56개 Designator 집합 완전 일치 여부 ($\Delta = 0$).
  2. SMT 실장 레이어 (단일면 Top 100% 여부).
  3. LCSC Part # 불일치 전수 탐지 (C11, R12 불일치 보고).
  4. 물리적 패키지 충돌 탐지 (0402 vs 0603).
  5. CPL vs JSON SMT 배치 좌표 이동량($>0.05\text{mm}$) 전수 탐지.
* **검사하지 않는 항목 (한계)**:
  - 실제 LCSC 물류 창고의 실시간 재고 여부.
  - SMT 스텐실 솔더 페이스트 개구율 및 젖음성.
* **실패 조건**: 부품 누락/초과, Bottom 면 부품 실장 감지 시 즉각 FAIL.

### 2.2 [TOOL-02] 거버 패키지 무결성 검사기 (`gerber_integrity_checker.py` v2.0)
* **검사 목적**: 압축 거버 아카이브 내 레이어 파일 무결성 및 4층 구조 확인.
* **입력 파일**: `Gerber_PCB1_revB_2026-07-09.zip`.
* **검사 항목**:
  1. 20개 레이어 파일 존재 여부 (Top, Bottom, G1-GND, G2-VCC, 실크, 마스크, 페이스트, 드릴 3종).
  2. 아카이브 SHA-256 암호화 해시 검증.
* **검사하지 않는 항목 (한계)**:
  - 물리적 기판 두께($1.6\text{mm}$), 프리프레그 유전율($\epsilon_r$), 동박 두께($1\text{oz}$) 실측치 $\rightarrow$ JLCPCB 인보이스 및 물리적 단면 검사 필요 (`PENDING_FAB_CONFIRMATION`).
  - DRC 트랙 간 클리어런스 위반 (EasyEDA 내장 DRC 필요).
* **실패 조건**: 20개 필수 거버 파일 중 1개라도 누락 시 즉각 FAIL.

### 2.3 [TOOL-03] 요구사항 추적성 검사기 (`requirements_traceability_checker.py` v2.0)
* **검사 목적**: RTM CSV의 양방향 추적성 및 필수 요구사항 ID 무결성 검증.
* **입력 파일**: `PCB_0006_REQUIREMENTS_TRACEABILITY_MATRIX.csv`.
* **검사 항목**:
  1. 12대 Core Baseline 요구사항(`REQ-P0-01~05`, `REQ-P1-01~07`) 100% 완비 여부.
  2. 3대 Extended Candidate 요구사항(`REQ-P0-06`, `REQ-P1-08`, `REQ-P1-09`) 존재 여부.
  3. 요구사항별 Schematic Net 및 Test Case ID 매핑 결측치 검사.
* **검사하지 않는 항목 (한계)**:
  - 실제 회로도 넷리스트 상의 물리적 라우팅 연결 여부 (Phase 3 넷리스트 비교기 필요).
* **실패 조건**: 12대 핵심 요구사항 중 1개라도 누락 시 즉각 FAIL.

### 2.4 [TOOL-04] 프로토콜 벡터 테스트 (`test_protocol_vectors.js`)
* **검사 목적**: 스마트 배시넷 제어 명령 패킷의 경계값 필터링 및 상태 머신 전이 검증.
* **실행 내역**: 48개 벡터 전수 실행 $\rightarrow$ **48 PASSED / 0 FAILED**.
* **검사 항목**: 주파수 한계(30~65Hz), 볼륨 상한(0.5f), ESTOP 전이, 안전 잠금(Safety Lock) 중 명령 거부.
* **검사하지 않는 항목 (한계)**:
  - 실제 ESP32 실리콘 칩 및 BLE 라디오 RF 송수신.
  - 호스트 PC의 Node.js 가상 환경에서 C++ 로직의 JS 포팅 버전을 실행한 소프트웨어적 검증임.

### 2.5 [TOOL-05] 펌웨어 보안/안전 감사 스위트 (`test_command_parser.py`)
* **검사 목적**: 펌웨어 C++ 소스 코드 정적 규칙 감사 및 명령어 파서 동적 검증.
* **실행 내역**: 92개 테스트 전수 실행 $\rightarrow$ **92 PASSED / 0 FAILED**.
* **검사 항목**: JSON 파싱 예외 처리, 100ms 감시 루프의 서멀 디레이팅(135°C), 하드웨어 셧다운 콜백 존재 여부, NVS 인증 토큰 노출 방어.
* **검사하지 않는 항목 (한계)**:
  - 실제 타깃 MCU 하드웨어의 클록, 전원 전압 강하, 발열 실측치.

---

## 3. 종합 요약표

| 도구 식별자 | 실행 환경 | 대상 레벨 | 테스트 수 | 통과율 | 물리적 검증 대체 가능 여부 |
|:---|:---:|:---:|:---:|:---:|:---:|
| `bom_cpl_comparator.py` | Python 3 | 제조 CAD 데이터 | 56개 부품 | **100%** | **불가** (실물 계측 별도 필요) |
| `gerber_integrity_checker.py` | Python 3 | 거버 파일셋 | 20개 레이어 | **100%** | **불가** (제조사 스택업 별도 확인) |
| `requirements_checker.py` | Python 3 | 요구사항 매트릭스 | 15개 요구사항 | **100%** | **불가** (설계권자 Gate 승인 필요) |
| `test_protocol_vectors.js` | Node.js | 프로토콜 계층 | 48개 벡터 | **100%** | **불가** (무선 RF 실측 별도 필요) |
| `test_command_parser.py` | Python 3 | 펌웨어 소스/파서 | 92개 테스트 | **100%** | **불가** (실기판 런타임 별도 필요) |
