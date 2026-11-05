# [통제 매트릭스] MAJN 차기 제어기 (PCB #0006) 9대 승인 Gate (G0~G8) 준비도 평가표
(MAJN PCB #0006 Gate G0~G8 Engineering Readiness & Sign-off Matrix)

- **문서 식별자**: `MAJN_GATE_G0_G8_READINESS_MATRIX`
- **리비전**: v1.0
- **작성 일자**: 2026-11-05
- **책임 주체**: Antigravity (독립 기술 심사 에이전트)
- **최종 판정**: **G0/G1: HOLD (조건부 진행 중, 최종 통과 미승인) | G2~G5: HOLD (설계 착수 및 거버 생성 동결) | G6~G8: NOT_STARTED**
- **적용 규칙**: [AGENTS.md](file:///Users/youngseok/Desktop/majn/AGENTS.md) 제2조, 제5조 (독립 검토 및 Human Chief Authority 최종 승인 원칙)

---

## 1. 개요 및 Gate 통제 체계 철학

본 문서는 MAJN 차기 제어 보드(PCB #0006) 개발 파이프라인에서 **"문서 작성 완료나 소프트웨어 CI 통과를 실제 하드웨어의 물리적 안전성 승인으로 오인하는 위험"을 원천 차단**하기 위해 수립된 최상위 Gate 승인 통제 매트릭스이다.

### 4대 통제 원칙
1. **소프트웨어 CI와 하드웨어 승인의 엄격한 분리**: 자동화 스크립트(100% PASS)는 텍스트·데이터 무결성 검증 도구일 뿐이며, 실제 물리적 회로 안전성, 기구 적합성, 전기적 동작 승인은 물리적 시험 및 서명(Sign-off)을 통해서만 통과된다.
2. **선행 Gate 미통과 시 후행 Gate 착수 금지 (No Bypassing)**: 선행 Gate가 공식 승인되지 않은 상태에서 회로도 수정, PCB 배선, 거버 생성을 절대 진행하지 않는다.
3. **독립 기술 검토와 최종 승인권자의 분리**:
   - **OpenCode (Lead Engineer)**: 설계 분석, 수정안 설계, DFM/DFT 계획 수립.
   - **Antigravity (Independent Reviewer)**: 기술적 반론, 정량 계산 재검증, 체크리스트 실사, 판정 권고.
   - **Human Chief Authority (최종 승인권자)**: 설계 기준선 확정, 부품 변경 승인, 거버 릴리스 및 발주 승인.
4. **증거 기반 판정 (Fact-Based Verdict)**: 모든 Gate 판정은 데이터시트, 오실로스코프 파형, 공인 시험성적서 등 물리적 증거에 근거한다.

---

## 2. 9대 승인 Gate (G0 ~ G8) 준비도 종합 요약표

| Gate | 명칭 (Stage Name) | 진입 기준 (Entry Criteria) | 요구 물리·공학적 증거 (Required Evidence) | 현재 상태 (Current Status) | 승인 권한 (Sign-off Authority) | 잔여 갭 및 액션 아이템 |
| :---: | :--- | :--- | :--- | :---: | :---: | :--- |
| **G0** | **PCB #0005 제조 기준선 복원** | 7월 제조 발주 파일 및 실물 증거 확보 | • 4층 거버 20개 파일 일치<br>• BOM/CPL 56개 단일면 SMT 100% 일치<br>• 실물 사진(ESP32-32UE, L1 4R7 등) 대조<br>• 37개 구버전 격리 | **HOLD**<br>(조건부 진행 중) | Antigravity (검증)<br>User (최종 승인) | • EasyEDA Pro 클린 SSOT 프로젝트(`.epro2`) 역합성 및 C11/R12 실물 치수 실측 필요 |
| **G1** | **고장 분석 및 FMEA 확정** | 선행 시제품 고장 이력 수집 | • 12대 고장 모드(FM-01~12) 메커니즘 규명<br>• FMEA RPN 우선순위 평가 완료<br>• 고장 재현 계측 계획 수립 | **HOLD**<br>(조건부 진행 중) | OpenCode (분석)<br>Antigravity (검증)<br>User (승인) | • 물리적 벤치 재현 계측(TP-01~04 오실로스코프 파형 획득) 완료 필요 |
| **G2** | **PCB #0006 요구사항 및 아키텍처 확정** | G0, G1 조건부 통과 및 DOC03 최신화 | • 12개 Core 요구사항 동결<br>• 3개 Extended 요구사항 승인 여부 결정<br>• RTM CSV 100% 양방향 매핑<br>• 시스템 전원/인터페이스 블록도 확정 | **HOLD**<br>(의사결정 대기) | Human Chief Authority (최종 확정) | • 확장 3개 항목(REQ-P0-06, P1-08, P1-09) 채택 여부 최종 서명 필요 |
| **G3** | **회로 상세 설계 및 부품 승인** | G2 공식 승인 및 부품 선정 완료 | • 회로도 수정안 및 넷리스트<br>• ERC 0 Error / 0 Warning<br>• GPIO13 PDN 배정 및 FW 연동 승인<br>• L1(7.5A), C6-C9(35V) 부품 승인<br>• BTL 보호 토폴로지 승인 | **HOLD**<br>(설계 수정 미착수) | Lead Engineer<br>Antigravity<br>User (승인) | • Read-Only 규칙 유지 중<br>• G2 확정 후 회로도 수정 및 부품 ECO 결재 |
| **G4** | **PCB Layout 및 DFM/DFT 검토** | G3 공식 승인 | • 4층 PCB 스택업(JLCPCB 7628 확인)<br>• 파워 루프 최소화 및 동박 Rebuild<br>• DRC 0 Error (Clearance/Crossing)<br>• 션트 패드 및 TP1~TP10 배치<br>• 기구 하우징 3D 간섭 검토 | **HOLD**<br>(선행 단계 대기) | Lead Engineer<br>Antigravity | • G3 승인 후 배선 착수<br>• JLCPCB DFM 온라인 검사기 검증 |
| **G5** | **제조 데이터 Release & 발주 동결** | G4 공식 승인 및 DRC 완전 통과 | • 최종 Gerber_Output.zip (SHA-256)<br>• BOM/CPL 100% 매칭 검증<br>• 발주 매니페스트 동결 | **HOLD**<br>(발주 금지) | Human Chief Authority (단독 서명) | • 모든 선행 Gate 종결 후 최종 서명 및 거버 생성 |
| **G6** | **하드웨어 Bring-up 및 계측 검증** | 실물 PCB #0006 제작 및 수령 | • DMM 임피던스 쇼트 검사<br>• 전원 시퀀싱(VBUS→3.3V→12V→AMP) 실측<br>• 과전압/오버슈트(<13.2V) 오실로스코프 파형<br>• 10W 연속 부하 열화상(<55°C) 계측 | **NOT_STARTED** | Lead Hardware Engineer<br>User | • 물리 보드 제작 완료 후 진행 |
| **G7** | **전기 안전 및 규제 인증 적합성** | G6 하드웨어 정상 동작 확인 | • KC 전자파(KN 32/35) 사전 시험성적서<br>• 영유아 안전기준(음압 <75dB, 온도 <60°C)<br>• 모터 구속/단락 시 안전 차단(<100ms) 입증 | **NOT_STARTED** | 공인시험소<br>User | • 공인 인증 기관 사전 시험 의뢰 |
| **G8** | **최종 양산 Release 확정** | G0~G7 전원 합격 및 잔여 이슈 제로 | • 양산 금형/조립 공정 매뉴얼(SOP)<br>• 최종 제조 거버/BOM/CPL 형상 동결<br>• KC/FCC 정식 인증서 수령 | **NOT_STARTED** | Human Chief Authority | • 양산 승인 및 이력 최종 아카이빙 |

---

## 3. Gate별 상세 평가 및 잔여 갭 분석

### 3.1 Gate G0: PCB #0005 기준선 복원 (Current: HOLD / CONDITIONAL_IN_PROGRESS)
- **달성된 사실 (Verified Fact)**:
  - 2026년 7월 9일 자 거버 파일(`Gerber_PCB1_revB_2026-07-09.zip`) 20개 레이어 구조 완비 확인.
  - 제조 발주 BOM/CPL 56개 부품 단일면 Top SMT 실장 100% 일치 확인.
  - 실물 사진 5종을 통해 ESP32-WROOM-32UE(u.FL), Sunlord L1 4R7, D3 SS34, FB1~FB4 실장 완벽 교차 검증.
  - 6월 24일 자 37개 구버전 결함 파일 격리 및 기각 완료.
- **잔여 갭 (Blocking Gap)**:
  - EasyEDA Pro 원본 `.epro2` 파일이 6월 구버전만 존재하므로, 7월 거버/BOM/CPL 기반의 정식 클린 프로젝트(`MAJN_PCB_0005_SSOT_RESTORED`) 역합성 작업이 남아 있음.
- **G0 최종 통과 조건**:
  - 역합성된 클린 프로젝트의 Netlist와 7월 BOM의 1:1 대조 확인 후 최종 서명.

---

### 3.2 Gate G1: 고장 분석 및 FMEA 확정 (Current: HOLD / CONDITIONAL_IN_PROGRESS)
- **달성된 사실 (Verified Fact)**:
  - 12대 고장 모드(`PCB_0005_FAILURE_ANALYSIS_REPORT.md`) 분석 완료.
  - FMEA 위험 우선순위 평가(`PCB_0005_FMEA.md`) 완료: FM-01(부스트 스파이크 RPN 240), FM-03(앰프 동시전원 RPN 216), FM-02(PDN 부유 RPN 210) 등 핵심 취약점 식별.
  - 계측 및 재현 계획(`PCB_0005_MEASUREMENT_AND_REPRODUCTION_PLAN.md`) 수립 완료.
- **잔여 갭 (Blocking Gap)**:
  - 문서 및 수식 기반 메커니즘 규명은 완료되었으나, 실물 보드 벤치에서 오실로스코프로 실측한 파형 데이터 첨부는 실물 접근 시까지 유예됨.
- **G1 최종 통과 조건**:
  - 분석 보고서 및 FMEA RPN 결과에 대한 Human Chief Authority의 승인.

---

### 3.3 Gate G2: PCB #0006 요구사항 및 아키텍처 확정 (Current: HOLD)
- **현재 상황 (Status Context)**:
  - DOC03 요구사항 12개와 신규 도출 3개 항목 간의 불일치를 해소하는 화해 보고서(`MAJN_REQUIREMENTS_RECONCILIATION_REPORT.md`) 작성 완료.
  - 15개 항목 전체에 대한 양방향 추적성 매트릭스(`PCB_0006_REQUIREMENTS_TRACEABILITY_MATRIX.csv`) 및 자동 검증 스크립트 v2.0 개발 완료.
- **보류 사유 (Hold Reason)**:
  - 확장 제안 3개 항목(REQ-P0-06 USB-C CC 풀다운, REQ-P1-08 3.3V LDO 벌크 캡, REQ-P1-09 외장 FPC 안테나)의 정식 채택 여부는 **Human Chief Authority의 설계 변경 승인(ECO 승인)**이 필수적임.
- **G2 통과 조치 (Action to Unblock)**:
  - Chief Authority가 확장 3개 항목을 공식 요구사항으로 승인하고, DOC03 리비전을 v1.2로 확정 서명.

---

### 3.4 Gate G3: 회로 상세 설계 및 부품 승인 (Current: HOLD)
- **현재 상황 (Status Context)**:
  - 부품 선정 매트릭스(`PCB_0006_COMPONENT_SELECTION_MATRIX.csv`) 및 전원 무결성 계산 감사(`MAJN_POWER_INTEGRITY_CALCULATION_AUDIT.md`) 완료.
  - ESP32 38핀 핀맵 분석(`MAJN_HW_FW_PIN_AND_INTERFACE_AUDIT.md`)을 통해 GPIO13을 PDN 후보로 도출하고 스트래핑 핀 위험이 없음을 입증함.
- **보류 사유 (Hold Reason)**:
  - 회로도 원본 수정은 Gate G2 통과 및 사용자 승인 전까지 엄격히 금지됨(Read-Only 원칙).
  - GPIO13 배정 시 펌웨어 매크로(`PIN_AMP_PDN 15` → `13`) 및 회로도 변경의 동시 승인이 필요함.
  - BTL 출력 보호 소자(쇼트키 다이오드 어레이 vs TVS/RC 스너버)의 최종 스펙 확정 필요.
- **G3 통과 조치 (Action to Unblock)**:
  - Gate G2 통과 후, 승인된 회로 수정 지시서(ECO)에 따라 회로도를 수정하고 ERC 무결성 확보.

---

### 3.5 Gate G4: PCB Layout, DFM/DFT 및 스택업 검토 (Current: HOLD)
- **현재 상황 (Status Context)**:
  - DFM/DFA/DFT 보고서 및 레이아웃 체크리스트 수립 완료.
  - 거버 레이어 검증기(`gerber_integrity_checker.py` v2.0)에서 물리적 스택업 파라미터는 `PENDING_FAB_CONFIRMATION`으로 엄격히 분리 관리.
- **보류 사유 (Hold Reason)**:
  - 회로도(G3) 미완성으로 PCB 아트워크 작업 미착수.
  - JLCPCB 4층 스택업(JLC7628 / 1.6mm / 1oz 외층/내층) 발주 옵션 확인 필요.
- **G4 통과 조치 (Action to Unblock)**:
  - 회로 넷리스트 동기화 후 PCB 배선 완료, 내장 DRC 0 Error 달성, 동박 Rebuild(`Shift+B`), JLCPCB 온라인 DFM 통과.

---

### 3.6 Gate G5: 제조 데이터 Release 및 발주 승인 (Current: HOLD)
- **통제 규칙**:
  - G0~G4 승인 없이 신규 거버 파일, 발주용 BOM/CPL 생성 절대 금지.
  - 최종 릴리스 패키지는 SHA-256 해시를 생성하여 매니페스트에 박제하고 Human Chief Authority의 정식 서명 하에서만 JLCPCB 발주 진행.

---

### 3.7 Gate G6 ~ G8: 하드웨어 제작, 안전 인증 및 양산 (Current: NOT_STARTED)
- 물리적 시제품 제작 및 입고 후 순차적으로 진입하며, 각 단계별 계측 성적서와 공인 인증 시험 결과를 바탕으로 엄격히 심사함.

---

## 4. 최종 결론 및 권고

1. **현재 단계는 "G0/G1 조건부 통과 및 G2 승인 대기(HOLD)" 상태**입니다.
2. 소프트웨어 CI 검증 도구가 100% PASS 되었다고 하여 PCB #0006의 회로가 검증된 것이 아니며, **Gate G2에 대한 Human Chief Authority의 최종 의사결정이 파이프라인 진행의 다음 열쇠**입니다.
3. OpenCode와 Antigravity는 Chief Authority의 승인 신호가 전달되기 전까지 회로도 및 레이아웃 수정에 착수하지 않는 엄격한 가드레일을 준수합니다.