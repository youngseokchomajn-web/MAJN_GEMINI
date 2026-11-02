# [MAJN Engineering System] ENG-001 ~ ENG-006 기준선 충돌 해결 및 분석 종합 보고서

- **문서 ID**: `MAJN-ENG-RES-001-006`
- **상태**: Draft for Human & Peer Review
- **기준 브랜치**: `docs/engineering-system-development-plan` (Commit `a5d7b65`)
- **작업 브랜치**: `docs/eng-001-006-baseline-resolution`
- **참조 문서**:
  - `docs/engineering/ENGINEERING_DEVELOPMENT_PLAN_INDEX.md`
  - `docs/engineering/ENGINEERING_RISK_AND_CONFLICT_REGISTER.md`
  - `docs/engineering/ENGINEERING_WORK_PACKAGE_BACKLOG.md`
  - `docs/engineering/WP00_WP01_INTEGRATED_AUDIT_REPORT.md`

---

## 1. 개요 및 목적

본 보고서는 MAJN 스마트 배시넷 엔지니어링 통합 시스템 개발 계획(Week 1)에 따라 식별된 **6대 기준선 충돌 과제(ENG-001 ~ ENG-006 / BASE-01 ~ BASE-08 / RSK-001 ~ RSK-008)**에 대해, 소스 코드, 제조 거버, DRL 드릴 데이터, DMM 계측 CSV, 회로 넷리스트 및 규제 표준을 교차 대조하여 도출한 공식 해결 방안과 기술적 판정을 기록합니다.

본 작업은 기존의 검증되지 않은 설계치를 임의로 덮어쓰지 않고, **실물 시제품 #0005의 물리적 진실(Ground Truth)을 완벽히 재현**하고 차기 양산 설계 간의 경계를 엄격히 통제하는 것을 최우선 원칙으로 합니다.

---

## 2. 6대 기준선 충돌 정밀 분석 및 해결 (ENG-001 ~ ENG-006)

```
┌──────────────────────────────────────────────────────────────────────────────────────────────────┐
│                         [ ENG-001 ~ ENG-006 기준선 충돌 해결 종합 요약표 ]                       │
├─────────┬──────────────────────┬────────────────────────┬─────────────────────────┬──────────────┤
│ 티켓 ID │ 핵심 쟁점 및 충돌    │ 감사 전 표기 / 가설    │ 실체 규명 팩트 (Truth)  │ 최종 공식 판정│
├─────────┼──────────────────────┼────────────────────────┼─────────────────────────┼──────────────┤
│ ENG-001 │ 불일치 상태 체계     │ RESOLVED / OPEN 단순   │ 8대 표준 상태 체계 도입 │ 대장 v2 개편 │
│         │ 관리 미흡            │ 2단계 분류             │ 추적성/소유자/증거 바인딩│ 상태 재분류  │
├─────────┼──────────────────────┼────────────────────────┼─────────────────────────┼──────────────┤
│ ENG-002 │ PCB #0005 층수 및    │ "2-Layer #0005" vs     │ 제조 거버 Inner1/2 존재 │ 실물 #0005는 │
│(BASE-01)│ 세대 식별 혼선       │ "4-Layer Rev-C" 혼동   │ 75,534B/5,530B 내층 확인│ 100% 4층 보드│
├─────────┼──────────────────────┼────────────────────────┼─────────────────────────┼──────────────┤
│ ENG-003 │ 익사이터 저항 측정치 │ 21.6Ω vs 24.8Ω         │ 단품 DCR 10.8Ω×2=21.6Ω  │ 계측 경로차이│
│(BASE-02)│ 21.6Ω / 24.8Ω 차이   │ 상충 데이터 표기       │ 조립 하네스 실측 24.8Ω   │ 8Ω 승계 금지 │
├─────────┼──────────────────────┼────────────────────────┼─────────────────────────┼──────────────┤
│ ENG-004 │ RF 안테나 이득 및    │ IF-RF-001 "VERIFIED"   │ #0005는 PCB 안테나 실장 │ IF-RF-001을  │
│(BASE-03)│ 모듈 규제 승계 상충  │ 3dBi 외장 FPC 장착 주장│ 외장 3dBi는 승계(≤2.33)초과│ BLOCKED 강등 │
├─────────┼──────────────────────┼────────────────────────┼─────────────────────────┼──────────────┤
│ ENG-005 │ PCB 마운팅 홀 누락   │ 기구-전장 조립 가능 판정│ 실물#0005 홀은 0.25mm   │ BLOCKED /    │
│(BASE-04)│ 및 좌표계 불일치     │ 하판에 나사홀 가공 전무│ DXF 하판 홀=0개 (테이프)│ ECO 제정 대기│
├─────────┼──────────────────────┼────────────────────────┼─────────────────────────┼──────────────┤
│ ENG-006 │ 450×250 vs 720×390   │ 720 카트를 레거시 처리 │ 가정용 슬림패드(450) vs │ 2대 제품군   │
│(BASE-05)│ 제품군 경계 모호     │ 또는 단일 BOM 강제 통합│ 조리원 카트(720 IP67)   │ 매니페스트분리│
└─────────┴──────────────────────┴────────────────────────┴─────────────────────────┴──────────────┘
```

---

### 2.1 [ENG-001] 불일치 상태 체계 표준화 (Discrepancy Register v2)

- **배경**: 기존에는 이슈가 해결되었는지 여부를 단순히 `RESOLVED` 또는 `OPEN`으로만 표기하여, "공학적 사실이 규명된 것(Fact Confirmed)"과 "실제 설계 변경이나 부품 발주가 승인된 것(Approved)", 그리고 "시험을 통해 합격한 것(Verified)"이 혼용되는 중대한 관리적 결함이 있었습니다.
- **해결 방안**: 기획 문서(`ENGINEERING_RISK_AND_CONFLICT_REGISTER.md`)에 정의된 **8대 표준 상태 체계**를 도입하여 전수 재분류하였습니다:
  1. `FACT_CONFIRMED`: 코드, 데이터, 거버를 통해 물리적 사실관계가 100% 규명됨.
  2. `DISCREPANCY_IDENTIFIED`: 둘 이상의 소스 간 수치/형상 불일치가 공식 식별됨.
  3. `ENGINEERING_ACTION_OPEN`: 엔지니어링 후속 조치(설계 수정, 도면 작성 등)가 열려 있음.
  4. `VERIFICATION_PENDING`: 가설 수립 및 설계는 되었으나 물리 계측/시험 합격이 잔여함.
  5. `HUMAN_APPROVAL_PENDING`: 안전, 비용, 규제 책임자의 공식 서명이 대기 중임.
  6. `BLOCKED`: 선행 조건 미충족 또는 안전/규제 위험으로 작업 착수 금지.
  7. `CLOSED`: 공식 승인 및 실측 검증이 완료되어 닫힘.
  8. `SUPERSEDED`: 설계 변경에 의해 구버전 사양으로 대체 폐기됨.

---

### 2.2 [ENG-002 / BASE-01] PCB #0005 층수(Layer Stackup) 및 세대 실체 규명

- **쟁점**: 자산 대장 및 일부 문서에서 실물 보드 PCB #0005를 "2-Layer"로 기재한 반면, 제조 패키지에서는 4층 기판 거버가 발견되어 보드의 물리적 실체에 대한 혼선이 발생함.
- **포렌식 분석 및 증거**:
  1. **실물 발주 증거**: [`인증준비/pcb/260630/MAJN_PCB_발주완료_2026-07-06.md`](file:///Users/youngseok/Desktop/majn/인증준비/pcb/260630/MAJN_PCB_발주완료_2026-07-06.md) 확인 결과, 2026년 7월 6일 JLCPCB에 주문번호 `W2026070611043433`으로 발주(총 $190.13, 5장 제작).
  2. **제조 거버 압축파일 검증**: `Gerber_PCB1_2026-07-05_1oz.zip` (SHA-256: `b0fff25bff8612727e49ff3db24ac40ce4196dfb60c9afc4b401d8f678a251dc`):
     - `Gerber_TopLayer.GTL`: 58,956 Bytes
     - `Gerber_InnerLayer1.G1`: **75,534 Bytes (Inner 1 - GND Plane)**
     - `Gerber_InnerLayer2.G2`: **5,530 Bytes (Inner 2 - VCC_3V3 Plane)**
     - `Gerber_BottomLayer.GBL`: 5,769 Bytes
  3. **"2-layer" 오류 발원지**: [`인증준비/mcp_development/PCB1_Project_Backup.epro2`](file:///Users/youngseok/Desktop/majn/인증준비/mcp_development/PCB1_Project_Backup.epro2)의 초기 백업 파일에서 Inner1/Inner2의 `use` 속성이 `false`로 설정된 구버전 프로젝트 메타데이터를 복사하면서 발생한 문서 오염임.
  4. **부스트 컨버터 피드백 분압 저항 정정**:
     - 선행 보고서에 기재된 $R_1=16\text{k}\Omega, R_2=150\text{k}\Omega$는 Low-side와 High-side가 반전된 오류 수치임 ($V_{out} = 1.225 \times (1 + 16/150) = 1.35\text{V}$가 되어 부스트 불가).
     - 실제 실장 BOM(`C22877`, `C22818`) 및 공정 실측값은 **$R_1=143\text{k}\Omega, R_2=16\text{k}\Omega$ ($V_{out,calc}=12.17\text{V}$, 실측 $12.00\text{V}$)**임.
- **공식 판정**: **실물 보드 PCB #0005는 100% 물리적 4층 기판(4-Layer FR-4)**입니다. `asset_inventory.csv`의 오류 표기를 4층으로 정정합니다.

---

### 2.3 [ENG-003 / BASE-02 & BASE-06] 익사이터 임피던스(21.6Ω vs 24.8Ω) 계측 조건 정합

- **쟁점**: 계측 결과 문서에서 익사이터 부하 저항이 21.6Ω과 24.8Ω으로 다르게 표기되어 모순 여부 확인 필요.
- **포렌식 분석 및 증거**:
  1. **24.8Ω 실측**: [`docs/MAJN_PCB_0005_EXCITER_SUCCESS_MEASUREMENT_RECORD.md#L23`](file:///Users/youngseok/Desktop/majn/docs/MAJN_PCB_0005_EXCITER_SUCCESS_MEASUREMENT_RECORD.md#L23)
     - 2026-10-24 벤치 시험: 24AWG 실리콘 케이블(25cm), J2 터미널 헤더, 테스터 리드봉 저항이 포함된 **인시츄(In-situ) 루프 직류 저항 실측치 = 24.8 Ω**.
  2. **21.6Ω 실측**: `hardware_review/Measurements/Resistance.csv`
     - 시료 단품 보이스코일 순수 DCR($10.8\,\Omega \times 2 = 21.6\,\Omega$)이며, 1kHz 교류 공칭 임피던스는 **24.0 Ω** (단품 12Ω 공칭).
  3. **8Ω 양산 적용 시의 엄중한 경고 (RSK-006)**:
     - 시제품 #0005는 12Ω 공칭 샘플(직렬 24Ω 부하)로 구동되어 피크 전류 0.50A, 피크 전력 6.0W 수준에서 검증됨.
     - 양산 예정 부품인 **Tectonic TEAX14C02-8 (8Ω 공칭, 직렬 16Ω, DCR ≈ 14.4Ω)** 적용 시:
       $$I_{peak} = \frac{12.0\text{V}}{16\Omega} = \mathbf{0.75\text{ A}}, \quad P_{peak} = \frac{12.0^2}{16\Omega} = \mathbf{9.0\text{ W}} \quad (\text{전력 및 발열 50\% 급증})$$
- **공식 판정**: 21.6Ω(단품 DCR)과 24.8Ω(하네스 포함 루프 저항)은 상충이 아니며 계측 경계 조건의 차이임. 단, #0005의 12Ω 계측 결과를 8Ω 양산품에 무단 승계하는 것은 엄격히 금지하며, T2 부하/발열 인증 시험 전까지 8Ω 확정은 `VERIFICATION_PENDING`으로 통제함.

---

### 2.4 [ENG-004 / BASE-03] RF 안테나 규제 승계 상충 (3dBi vs ≤ 2.33dBi)

- **쟁점**: `IF-RF-001` 인터페이스 대장에 "외장 3dBi FPC 안테나"가 `VERIFIED`로 기재되어 있으나, 실물 보드 및 전파법 승계 조건과 충돌함.
- **포렌식 분석 및 증거**:
  1. **실물 #0005 보드 실체**:
     - 실물 보드 #0005의 U1 모듈은 온보드 PCB 역F(MIFA) 안테나가 인쇄된 `ESP32-WROOM-32E`로 실장되어 출고됨.
     - IPEX(u.FL) 외장 커넥터가 장착되지 않았으므로 실물 보드에서 외장 3dBi FPC 안테나를 구동한 적이 없음. 따라서 기존 `VERIFIED` 판정은 허위 기재임.
  2. **전파인증 모듈 승계 한계 ($2.33\,\text{dBi}$)**:
     - 에스프레시프(Espressif)가 KC/FCC에 등록한 ESP32-WROOM-32UE의 공식 사전인증 다이폴 안테나 최대 이득은 **$2.33\,\text{dBi}$**임.
     - 전파법 규정상 등록 안테나 이득($\le 2.33\text{dBi}$) 이하의 동일 형식 안테나를 사용할 때만 모듈 인증이 승계되며, 3.0dBi 안테나를 임의 체결 시 인증이 원천 무효화되어 전면 재시험이 요구됨.
- **공식 판정**: `interface_registry.csv`의 `IF-RF-001` 상태를 `VERIFIED`에서 **`BLOCKED`**로 즉각 강등함. #0005는 "온보드 PCB 안테나"로 분리 기록하고, 차기 외장 안테나는 $\le 2.33\text{dBi}$ 규격품(MPN) 확정 및 시험기관 질의 전까지 설계를 동결함.

---

### 2.5 [ENG-005 / BASE-04] PCB-하우징 좌표 정합 및 마운팅 인터페이스 실체

- **쟁점**: 하우징 하판 Master DXF에 PCB 마운팅 홀이 누락되어 조립 불가.
- **포렌식 분석 및 증거**:
  1. **PCB 마운팅 홀 규격**:
     - Gerber Drill(`Drill_PTH_Through.DRL` Tool T06) 분석:
       가로 간격 $\Delta X = 72.39 - 3.81 = \mathbf{68.58\text{ mm}}$ ($2.70''$)
       세로 간격 $\Delta Y = 58.42 - 3.556 = \mathbf{54.864\text{ mm}}$ ($2.16''$)
  2. **실물 #0005의 치명적 결함 (E-16)**:
     - 7월 5일 제조 Gerber의 DRL 확인 결과, 해당 홀이 `T01C0.249936` 즉 **⌀0.25mm 비아 홀**로 출고됨.
     - 나사가 들어가지 않아 시제품 #0005는 양면 폼 테이프로 기판을 부착하여 시험했음.
  3. **기구 하판 도면 실태**:
     - `majn_housing/build_rev2_dxf.py` 하판에는 외곽 10개 볼트홀만 존재하고 PCB 체결홀은 0개임.
  4. **캐비티 수직 간극 계산**:
     - 캐비티 높이: $13.5\,\text{mm}$
     - 스탠드오프(5.0mm) + PCB(1.6mm) + 인덕터/커넥터(5.5mm) = $12.1\,\text{mm}$
     - 상판 진동판과의 수직 여유 공간: **약 $1.4\,\text{mm}$**로 매우 협소함.
- **공식 판정**: `IF-MEC-001`의 상태를 **`HUMAN_APPROVAL_PENDING`** 및 **`BLOCKED`**로 확정함. M2.5/M3 나사홀 4개소 및 USB-C 포트 접근홀을 하판 DXF에 추가하는 **공식 ECO(`ECO_001_BOTTOM_PLATE_PCB_MOUNTING.md`) 제정 전까지 하판 가공 및 PCB 발주를 전면 동결**함.

---

### 2.6 [ENG-006 / BASE-05] 제품 라인업 경계 분리 (`CFG-HOME-450` vs `CFG-HOSPITAL-720`)

- **쟁점**: 450×250mm 가정용 배시넷 패드와 720×390mm 산후조리원 카트 인셋용 기구가 혼재되어 단일 제품 규격으로 오인됨.
- **포렌식 분석 및 증거**:
  1. **Variant A: `CFG-HOME-450` (가정용 슬림 진동 패드)**:
     - 외형: $450.0 \times 250.0 \times 22.5\,\text{mm}$ (자작합판 4.5T 3단 적층, 캐비티 13.5mm, 10볼트 체결).
     - 방수: 생활방수 (1.2T 실리콘 가스켓).
     - 타겟: 일반 가정용 아기침대 매트리스 하부 안착형. 실물 #0005가 장착되는 대상.
  2. **Variant B: `CFG-HOSPITAL-720` (산후조리원 아크릴 카트 인셋형)**:
     - 외형: $720.0 \times 390.0 \times 45.0\,\text{mm}$.
     - 방수: **IP67 완전 방수** (조리원 감염관리 프로토콜 준수).
     - 구조: $750 \times 420\,\text{mm}$ 투명 아크릴 카트 맞춤형 인셋 하우징.
  3. **코어-보더 하이브리드 아키텍처**:
     - 450×250mm 목재 진동 코어를 중심으로 외곽에 18mm EVA 폼 보더를 결합하여 조리원 카트에 호환 안착하는 방식이 `NUCU_PAD_ULTRA_SLIM_ENGINEERING_REPORT.md`에 정의됨.
- **공식 판정**: 단일 통합 BOM 작성을 금지하고, `CFG-HOME-450`과 `CFG-HOSPITAL-720`의 2대 독립 구성 매니페스트로 요구사항, BOM, 규제 인증을 분리 관리함.

---

## 3. 후속 실행 조치 (Action Items Taken)

1. **시제품 #0005 불변 재현 매니페스트 생성**:
   - [`docs/engineering/manifests/CFG_PROTO_0005_MANIFEST.yaml`](file:///Users/youngseok/Desktop/majn/docs/engineering/manifests/CFG_PROTO_0005_MANIFEST.yaml) 등록 완료.
2. **불일치 대장 v2 (`discrepancy_register.csv`) 개편**:
   - 8대 표준 상태 및 20개 이슈(DISC-001~012, RSK-001~008) 매핑 완료.
3. **인터페이스 대장 (`interface_registry.csv`) 동기화**:
   - `IF-RF-001` $\rightarrow$ `BLOCKED`, `IF-MEC-001` $\rightarrow$ `HUMAN_APPROVAL_PENDING` / `BLOCKED`.
4. **기구 하판 마운팅 홀 추가 ECO 제정**:
   - [`docs/engineering/changes/ECO_001_BOTTOM_PLATE_PCB_MOUNTING.md`](file:///Users/youngseok/Desktop/majn/docs/engineering/changes/ECO_001_BOTTOM_PLATE_PCB_MOUNTING.md) 초안 등록.
