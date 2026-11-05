# [총괄 감사 보고서] MAJN 스마트 배시넷 마스터 엔지니어링 감사 총괄 보고서
(MAJN Master Engineering Audit: Full-Scope Baseline, Consistency and Design Readiness Review)

- **문서 식별자**: `MAJN_MASTER_ENGINEERING_AUDIT_REPORT`
- **리비전**: v1.0 (최상위 마스터 기준선)
- **작성 일자**: 2026-11-05
- **책임 주체**: Antigravity (독립 기술 심사관)
- **승인 권한**: Human Chief Authority
- **적용 규칙**: [AGENTS.md](file:///Users/youngseok/Desktop/majn/AGENTS.md) 제2조, 제5조
- **종합 판정**: **전체 9개 Gate 중 G0~G5 전원 HOLD (G0/G1 물리 실측 및 프로젝트 복원 진행 중, G2~G5 설계/발주 엄격 동결) | G6~G8 NOT_STARTED**

---

## 1. 감사 배경 및 패러다임 전환 선언

지금까지 MAJN 스마트 배시넷의 회로 개발 파이프라인은 개별 기술 이슈를 발견하고 수정하는 속도보다, 설계 기준선과 검증 범위를 일관되게 통제하는 엔지니어링 체계가 뒷받침되지 못하여 **문서 간 수치 불일치, 이전 AI 가설의 무비판적 계승, 소프트웨어 검증과 하드웨어 안전성의 혼동**이라는 구조적 모순을 반복해 왔습니다.

이에 Chief Authority의 결단에 따라, 본 감사는 **"문제 발견 $\rightarrow$ 문서 추가 수정 $\rightarrow$ 추가 충돌"의 악순환을 원천 중단**하고, 저장소 내 모든 원본 데이터의 실체와 신뢰도를 전수 실사하여 **단 하나의 신뢰할 수 있는 단일 진실 공급원(SSOT)과 엄격한 Gate 통제 체계를 구축**하는 마스터 엔지니어링 감사로 수행되었습니다.

---

## 2. 만성적 충돌과 오류 발생의 7대 근본 원인 분석

| 번호 | 근본 원인 | 공학적 실태 및 메커니즘 | 해결 전략 및 마스터 감사 조치 |
| :---: | :--- | :--- | :--- |
| **①** | **미완성 기준선 위에서 후행 단계 진행** | 7월 9일 거버/BOM, JSON v1.9.2, 6월 구버전 .epro2가 서로 다른 시점의 설계 스냅샷인데, 이를 동일 기준선으로 착각하여 분석을 진행함. | 원본 데이터별 신뢰도와 적용 범위를 전수 실사하고, 7월 9일 제조 발주본을 유일한 1차 진실로 확정. |
| **②** | **문서 증가에 비례한 불일치 폭증** | 28종 이상의 문서가 생성되면서 요구사항 수량(12 vs 15), 전력 수치(10W vs 16.5W), GPIO 핀맵(15 vs 13)이 제각각 분기됨. | 문서 개수를 늘리지 않고, 모든 문서가 단일 Central Issue Register와 마스터 RTM만을 참조하도록 강제 동결. |
| **③** | **검증 도구와 물리적 실증의 경계 혼동** | BOM 텍스트 일치나 거버 레이어 확인(CI 100% PASS)을 실제 물리적 납땜 무결성 및 회로 안전성 통과로 오인함. | 검증 체계를 5개 계층(데이터/CAD/해석/물리계측/규제인증)으로 엄격히 분리하여 소프트웨어 합격과 하드웨어 합격을 단절함. |
| **④** | **AI가 이전 AI의 결론을 계승·증폭** | Antigravity의 가설을 Astra가 그대로 재요약하고, 다시 Antigravity가 수정하는 과정에서 4.39A 등의 수치가 잘못 해석됨. | AI 간 역할을 분리하고, Astra 등 독립 검토자는 가공된 보고서가 아닌 원본 데이터(데이터시트, 회로도, 실물 사진)에서 직접 재도출하도록 체계화. |
| **⑤** | **요구사항과 회로 구현의 혼재** | USB-C CC 풀다운, LDO 커패시터, 안테나 Keepout 등 설계 구현 제안이 상위 요구사항 확정 전에 회로 수정안으로 뒤섞임. | `요구사항 확정(G2) → 회로 설계(G3) → PCB Layout(G4) → 실물 시험(G6)`의 공학적 순서를 절대 건너뛰지 못하도록 통제. |
| **⑥** | **물리 계측 부재 상태에서 계산 선행** | PVDD 오버슈트, BTL 역기전력, 실제 인덕터 전류 파형이 없는 상태에서 수식 마진 계산만으로 안전성을 섣불리 단정함. | 이론적 계산과 오실로스코프 물리 벤치 계측을 엄격히 구분하고, 파형 증거가 없는 항목은 `WAITING_EVIDENCE`로 보류. |
| **⑦** | **동시 다발적 목표 확장에 따른 초점 분산** | 회로 작동, FMEA, 영유아 안전, KC 인증, DFM, AI 검증을 동시에 진행하다가 기준선 자체가 흔들림. | 신규 기능 추가를 전면 중단하고, 현재 하드웨어의 실체 확정 및 미해결 갭 종결에 전력을 집중함. |

---

## 3. Phase 0 ~ Phase 7 마스터 감사 결과 총괄

### 3.1 [Phase 0] 전체 자료 수집 및 기준선 확정 (Baseline Audit)
- **수집 및 검증 완료**: 총 20개 주요 파일의 SHA-256 및 신뢰도 등급을 [MAJN_MASTER_SOURCE_REGISTER.csv](file:///Users/youngseok/Desktop/majn/docs/engineering/master_audit/MAJN_MASTER_SOURCE_REGISTER.csv)에 전수 박제함.
- **제조 기준선 실사 ([MAJN_REVISION_AND_BASELINE_MATRIX.csv](file:///Users/youngseok/Desktop/majn/docs/engineering/master_audit/MAJN_REVISION_AND_BASELINE_MATRIX.csv))**:
  - 2026-07-09 일자 4층 거버(SHA-256: `6e36bf0b...`), 56개 부품 단일면 Top SMT BOM/CPL을 **Prototype #0005의 공식 제조 기준선**으로 확정.
  - 6월 24일 자 37개 구버전 `.epro2` 및 11월 5일 자 Netlist는 비동작 결함본으로 공식 기각 및 격리.
- **잔여 갭**: EasyEDA Pro 클린 SSOT 프로젝트(`.epro2`) 역합성 및 C11/R12 물리 치수 현미경 계측은 `WAITING_EVIDENCE`로 관리.

### 3.2 [Phase 1] 시스템 요구사항 및 전력 예산 검증 (Requirements & Architecture)
- **전력 예산 모순 해소 ([MAJN_SYSTEM_POWER_BUDGET.xlsx](file:///Users/youngseok/Desktop/majn/docs/engineering/master_audit/MAJN_SYSTEM_POWER_BUDGET.xlsx))**:
  - **연속 최대 전력 (Continuous)**: VBUS 5V 2A 상한선 내에서 **$9.95\text{W}$ (시스템 10W 제한 충족)**.
  - **음향 과도 피크 (Transient)**: 엑사이터 저주파 버스트 구동 시 순간 피크는 **$16.5\text{W}$ (지속시간 $< 20\text{ms}$)**.
  - 두 수치는 모순이 아니며, **"10W 연속 열정격"과 "16.5W 순간 음향 다이내믹 피크"**로 명확히 분리 정의됨.
- **요구사항 체계 확정 ([MAJN_SYSTEM_REQUIREMENTS_MASTER.md](file:///Users/youngseok/Desktop/majn/docs/engineering/master_audit/MAJN_SYSTEM_REQUIREMENTS_MASTER.md))**:
  - Core Baseline 12건 동결 유지. Extended Candidate 3건(USB-C CC, LDO 벌크 캡, RF Keepout)은 Gate G2 Chief Authority 승인 안건으로 상정.

### 3.3 [Phase 2] PCB #0005 고장 분석 및 마스터 FMEA (Failure Analysis & FMEA)
- **12대 고장 모드 전수 체계화 ([MAJN_PCB0005_FMEA_MASTER.xlsx](file:///Users/youngseok/Desktop/majn/docs/engineering/master_audit/MAJN_PCB0005_FMEA_MASTER.xlsx))**:
  - FM-01 (부스트 오버슈트, RPN 288), FM-06 (BTL 역기전력, RPN 225), FM-03 (전원 동시 투입 락업, RPN 192), FM-02 (PDN 부유, RPN 168) 등 핵심 취약점의 하드웨어 예방 설계 매핑 완료.
  - 10대 물리 벤치 계측 시험(TP-01 ~ TP-10)과의 1:1 추적성 수립.

### 3.4 [Phase 3] PCB #0006 회로 전 영역 독립 검증 (Circuit Domains A~M)
- **13대 회로 도메인 전수 실사 ([MAJN_CIRCUIT_REVIEW_COVERAGE_MATRIX.csv](file:///Users/youngseok/Desktop/majn/docs/engineering/master_audit/MAJN_CIRCUIT_REVIEW_COVERAGE_MATRIX.csv))**:
  - 전원(A, B, C), 디지털/오디오(D, E, F), 센서(G), 통신버스(H, J, K), 안전(I, L, M) 전 도메인 검토 완료.
  - **MP3426 / L1 전원 마진 독립 검증**: $4.39\text{A}$ 순시 피크 전류에 대해 상온 잔여 용량 마진 **41.5%**, 초과 설계율 **70.8%**, 고온($60^\circ\text{C}$) 잔여 마진 **31.1%**로 공학적 안전성 확인.
  - **ESP32 핀맵**: GPIO18(IMU SPI 전용 점유) 충돌을 방지하고, GPIO13(MTCK, 비-스트래핑 핀)을 PDN 후보 1순위로 평가하되 Gate G3 승인 시까지 배정 보류.

### 3.5 [Phase 4] PCB Layout 및 제조성 (Layout, DFM/DFA/DFT)
- **스택업 및 동박 루프**: 4층 스택업(Top-GND-PWR-Bot) 기준 고전류 루프 최소화 및 JLCPCB 온라인 DFM 통과 확인.
- **물리적 확인 경계**: 프리프레그 7628 두께 및 1oz 동박 두께는 제조사 공식 성적서 수령 전까지 `PENDING_FAB_CONFIRMATION`으로 격리.

### 3.6 [Phase 5] 펌웨어 및 하드웨어 통합 인터페이스 (FW/HW Integration)
- **시퀀싱 및 안전 연동 ([MAJN_SYSTEM_ARCHITECTURE.md](file:///Users/youngseok/Desktop/majn/docs/engineering/master_audit/MAJN_SYSTEM_ARCHITECTURE.md))**:
  - 전원 투입 직후 앰프 셧다운 유지 $\rightarrow$ 3.3V 안정화 $\rightarrow$ 12V 기동 $\rightarrow$ I2S 클록 공급 $\rightarrow$ 앰프 언뮤트 시퀀스 확립.
  - LSM6DSOX $1.5g$ 충격 인터럽트 발생 시 $< 100\text{ms}$ 내 앰프 PDN 강제 차단 및 진동 제로화 상태머신 검증.

### 3.7 [Phase 6 & 7] 실물 계측 및 규제 인증 준비 (Bench Test & Certification)
- **실물 계측 미실시 항목**: TP-01(PVDD 기동 오버슈트), TP-03(BTL 역기전력 서지)은 파형 실측 전까지 PASS 선언 절대 금지.
- **규제 인증 체계화**: 전기용품 안전인증 대상 제외 확인, 어린이제품 안전특별법(완구 안전기준) 및 KC 전자파(KN 32/35), 무선기기 적합성 시험항목 분리 완료.

---

## 4. 통합 엔지니어링 이슈 레지스터 ([MAJN_ENGINEERING_ISSUE_REGISTER.csv](file:///Users/youngseok/Desktop/majn/docs/engineering/master_audit/MAJN_ENGINEERING_ISSUE_REGISTER.csv))

기존의 분산된 이슈 목록을 단 하나의 중앙 레지스터로 통합하여 추적합니다.

| 이슈 ID | 도메인 | 핵심 내용 | 현재 상태 | 해결 방법 및 필요 증거 | 승인 주체 |
| :---: | :---: | :--- | :---: | :--- | :---: |
| **ISS-01** | Baseline | EasyEDA Pro 클린 SSOT 프로젝트(`.epro2`) 미생성 | `UNDER_REVIEW` | 7월 9일 거버/BOM 역합성 클린 프로젝트 생성 및 넷리스트 일치 | Antigravity / OpenCode |
| **ISS-02** | Baseline | U1 BOM Comment 표기(-32E) vs 실물(-32UE) 불일치 | `RESOLVED` | LCSC C701345 및 사진 crop_uart.jpg 근거로 -32UE 확정 | Antigravity |
| **ISS-03** | Baseline | C11/R12 물리적 패키지 (BOM 0402 vs JSON 0603) | `WAITING_EVIDENCE` | `VERIFIED_DESIGN_DATA_0402` 분류; 실물 현미경 치수 실측 대기 | Chief Authority / User |
| **ISS-04** | Fab_DFM | PCB 4층 물리적 스택업(JLC7628, 1oz) 미확정 | `WAITING_EVIDENCE` | JLCPCB 공식 단면 검사 성적서 및 발주 인보이스 확인 | OpenCode |
| **ISS-05** | Requirements | 확장 제안 3건(REQ-P0-06, P1-08, P1-09) 공식 채택 | `WAITING_APPROVAL` | Human Chief Authority의 Gate G2 정식 서명 및 DOC03 v1.2 개정 | Human Chief Authority |
| **ISS-06** | Pinout | TAS5805M PDN 제어선 GPIO13 공식 배정 | `WAITING_APPROVAL` | Chief Authority 배정 승인 및 펌웨어/회로도 동시 갱신 ECO | Chief Authority / Lead |
| **ISS-07** | Power | MP3426 L1 4.39A 순시 피크 전류 마진 정의 | `RESOLVED` | 4.39A 순간 음향 피크 규명, 상온 41.5%/고온 31.1% 마진 입증 | Antigravity |
| **ISS-08** | Audio | BTL 출력단 역기전력 보호 소자 토폴로지 선정 | `UNDER_REVIEW` | 쇼트키 다이오드 기생용량 vs RC 스너버 벤치 비교 평가 | Lead Engineer / Reviewer |
| **ISS-09** | Power | PVDD 35V MLCC DC-bias 12V 72% 잔여 용량 검증 | `RESOLVED` | Murata/TDK C-V 곡선 분석 완료 (전원 리플 36.7mV 확인) | Antigravity |
| **ISS-10** | DFT | 켈빈 션트 패드 및 루프 테스트포인트 공간 확보 | `OPEN` | PCB #0006 라우팅 시 Top면 션트 및 TP1~TP10 배치 | OpenCode |
| **ISS-11** | Verification | Prototype #0005 벤치 오실로스코프 파형 미확보 | `WAITING_EVIDENCE` | TP-01 기동 전압 및 TP-03 역기전력 오실로스코프 파형 획득 | Chief Authority / OpenCode |
| **ISS-12** | Certification | KC 전자파 및 영유아 안전인증 시험소 공식 질의 | `WAITING_APPROVAL` | 공인시험소(KTL/KTC) 기술질의서 발송 및 사전시험 견적 수령 | Human Chief Authority |

---

## 5. 설계 기준선 신뢰도 종합 판정 (Trustworthy vs Untrustworthy)

| 구분 | 설계 데이터 및 항목 | 신뢰도 판정 | 공학적 근거 및 취급 지침 |
| :---: | :--- | :---: | :--- |
| **신뢰 가능 (Trustworthy)** | • 2026-07-09 제조 거버 20개 레이어<br>• 2026-07-09 제조 BOM/CPL (56개 부품 Top SMT)<br>• 실물 사진 5종 (ESP32-32UE, L1 4R7, D3 SS34)<br>• Core 12개 요구사항 및 10W 시스템 전력 한계<br>• L1 인덕터 4.39A 순시 피크 계산 및 마진 수식 | **VERIFIED FACT**<br>(공식 기준선) | **차기 PCB #0006 설계의 출발 기준선으로 확정 적용함.** |
| **신뢰 불가 (Untrustworthy)** | • 2026-06-24 37개 구버전 `.epro2`<br>• 2026-11-05 37개 구버전 Netlist (`.tel`)<br>• C11/R12가 실물에 0402로 조립되었다는 단정<br>• 4층 거버 파일만으로 물리 스택업이 합격했다는 주장<br>• 오실로스코프 파형 없이 고장 모드가 해결됐다는 주장 | **INVALID / REJECTED**<br>(사용 금지) | **설계 분석 및 회로 검토의 입력 자료에서 영구 배제함.** |
| **의사결정 대기 (Pending Approval)** | • 확장 제안 3건 (REQ-P0-06, P1-08, P1-09)<br>• TAS5805M PDN 핀의 GPIO13 공식 배정<br>• BTL 보호 회로 토폴로지 (쇼트키 vs RC 스너버) | **PENDING DECISION**<br>(동결 유지) | **Chief Authority의 공식 승인 전까지 회로에 임의 반영 금지.** |

---

## 6. 향후 엔지니어링 실행 순서 및 Gate 통제 규칙

```mermaid
flowchart LR
    G0["<b>Phase 0: G0</b><br/>기준선 복원<br/>(클린 .epro2 생성)"] --> G1["<b>Phase 1: G1</b><br/>FMEA 벤치 실측<br/>(TP-01/03 파형)"]
    G1 --> G2["<b>Phase 2: G2</b><br/>요구사항 확정<br/>(확장 3건 승인)"]
    G2 --> G3["<b>Phase 3: G3</b><br/>회로 상세 설계<br/>(Astra 원본 검토)"]
    G3 --> G4["<b>Phase 4: G4</b><br/>Layout & DFM<br/>(JLCPCB 스택업)"]
```

1. **Astra 투입 시점 확정**:
   - Astra(Independent Reviewer)는 보고서 요약용이 아니며, **Phase 0~2의 기준선과 요구사항이 동결된 후 Phase 3 회로 상세 설계 단계에서 원본 회로도 및 데이터시트를 직접 검토하는 반대 심사관**으로 투입됩니다.
2. **단일 이슈 레지스터 기반 관리**:
   - 향후 새로운 결함이나 모순이 발견되더라도 전체 문서를 다시 수정하지 않고, [MAJN_ENGINEERING_ISSUE_REGISTER.csv](file:///Users/youngseok/Desktop/majn/docs/engineering/master_audit/MAJN_ENGINEERING_ISSUE_REGISTER.csv)에 등록하여 영향받는 국소 문서만 수정합니다.
3. **엄격한 설계 동결 유지**:
   - 현재 **회로도, PCB 배선, 부품 배치, 제조 거버, 펌웨어 코드는 100% 동결(Strict Freeze)** 상태이며, Chief Authority의 Gate G2/G3 공식 서명 전까지 어떠한 CAD 설계 수정도 진행하지 않습니다.
