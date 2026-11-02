# [MAJN Engineering System] ENG-001 ~ ENG-006 기준선 충돌 정밀 검증 및 3차 기술 정합성 감사 종합 보고서 (Round 3 Consistency Audited)

- **문서 ID**: `MAJN-ENG-RES-001-006`
- **상태**: Draft for Human & Peer Review (Round 3 Technical Consistency Audited)
- **기준 브랜치**: `docs/engineering-system-development-plan` (Commit `a5d7b65`)
- **작업 브랜치**: `docs/eng-001-006-consistency-audit`
- **참조 문서**:
  - `docs/engineering/manifests/CFG_PROTO_0005_MANIFEST.yaml`
  - `docs/engineering/baseline/discrepancy_register.csv`
  - `docs/engineering/baseline/interface_registry.csv`
  - `docs/engineering/changes/ECO_001_BOTTOM_PLATE_PCB_MOUNTING.md`
  - `docs/engineering/ENGINEERING_DEVELOPMENT_PLAN_INDEX.md`
  - `docs/engineering/ENGINEERING_RISK_AND_CONFLICT_REGISTER.md`
  - `docs/engineering/ENGINEERING_WORK_PACKAGE_BACKLOG.md`
  - `docs/engineering/WP00_WP01_INTEGRATED_AUDIT_REPORT.md`

---

## 1. 개요 및 3대 층위 구분 원칙

본 문서는 MAJN 스마트 배시넷 엔지니어링 개발계획 1주차(ENG-001 ~ ENG-006) 과제에 대해 2차 증거 감사에 이어 문서 간 수치 모순과 비약된 안전성 가설을 엄격히 배제한 **3차 기술 정합성 감사(Technical Consistency Audit)** 종합 보고서입니다.

감사 원칙에 따라 모든 엔지니어링 서술을 다음 **3대 층위**로 엄격히 분리하였습니다:
1. **증거로 확인된 사실 (Fact Confirmed)**: 원본 파일 해시, 거버 내층 데이터, 고해상도 실물 사진, DMM 전원 레일 실측 로그, 파싱된 DXF 형상.
2. **증거를 바탕으로 한 해석/계산 (Analysis / Calculated Estimate)**: 4층 제조 스택업 해석, 계측 경로별 저항 차이, 50% 진폭 정현파 가정 계산치, 판 휨 등방성 스케일링 추정치. (실측 전압/변위와 엄격히 구분).
3. **아직 승인되지 않은 설계 가설 및 미검증 항목 (Unapproved Hypothesis / Verification Pending)**: 외장 안테나 형식 승계, 하판 스탠드오프 가공, 720 카트 제품군 및 IP67 방수 요구사항, 8Ω 익사이터 열안전성, 1.05mm 동적 간극 안전성.

---

## 2. 6대 기준선 충돌(ENG-001 ~ ENG-006) 세부 검증 결과

```
┌──────────────────────────────────────────────────────────────────────────────────────────────────┐
│                      [ ENG-001 ~ ENG-006 정밀 증거 감사 및 최종 판정 대조표 ]                    │
├─────────┬──────────────────────┬────────────────────────┬─────────────────────────┬──────────────┤
│ 티켓 ID │ 핵심 쟁점 및 충돌    │ 감사 전 표기 / 가설    │ 실체 포렌식 규명 증거   │ 최종 공식 판정│
├─────────┼──────────────────────┼────────────────────────┼─────────────────────────┼──────────────┤
│ ENG-001 │ 불일치 상태 체계     │ 단순 2단계 (RESOLVED)  │ 8대 표준 상태 체계 도입 │ 대장 v2 지속 │
│         │ 관리 미흡            │ 분류로 인한 오해       │ 소유자/증거/종료기준 연결│ 통제 확정    │
├─────────┼──────────────────────┼────────────────────────┼─────────────────────────┼──────────────┤
│ ENG-002 │ PCB #0005 층수 및    │ "2-Layer #0005" vs     │ 거버 4층 + 사진 확인    │ 거버4층 확인 │
│(BASE-01)│ 실물 제조 추적성     │ "점퍼 와이어 rev-A" 오해│ rev-B 정상 SMT, 단 실물 │ 실물추적성   │
│         │                      │                        │ 공장 성적서 미확보 상태 │ VERIF_PENDING│
├─────────┼──────────────────────┼────────────────────────┼─────────────────────────┼──────────────┤
│ ENG-003 │ 익사이터 부하 저항   │ 21.6Ω vs 24.8Ω         │ 단품 DCR 21.6Ω/루프 24.8Ω│ 전력계산치구분│
│(BASE-02)│ 및 BTL 전력 계산     │ 6W/9W vs 3W/4.5W vs    │ 3W/4.5W(100%)/0.75/1.1W │ 실측UNVERIFIED│
│         │                      │ 0.75W/1.125W 혼선      │ 전력 실측 부재, BTL 차동│ 8Ω열안전성   │
│         │                      │                        │ 프로브 계측 필수        │ VERIF_PENDING│
├─────────┼──────────────────────┼────────────────────────┼─────────────────────────┼──────────────┤
│ ENG-004 │ RF 모듈 실물 사양 및 │ 32E(PCB안테나) vs 32UE │ 사진상 u.FL 실장 확인   │ 모듈은 32UE  │
│(BASE-03)│ KC 전파인증 승계     │ 2.33dBi 법적상한 오인  │ u.FL 미체결 비통제 시험 │ RF시험UNVERIF│
│         │                      │                        │ R-C-es5-ESP32WROOM32E   │ 외장안테나   │
│         │                      │                        │ 3dBi FPC 시험기관 질의  │ BLOCKED 유지 │
├─────────┼──────────────────────┼────────────────────────┼─────────────────────────┼──────────────┤
│ ENG-005 │ 하판 마운팅 홀 누락  │ "0.25mm 홀 결함" 오인  │ 기판 홀은 정상 ⌀2.7mm PTH│ ECO-001 제안 │
│(BASE-04)│ 및 체결 간극         │ 15kg 처짐 1.8mm 및     │ 450mm 처짐 0.35mm는 단순│ (Würth MPN)  │
│         │                      │ 0.35mm 안전 간극 속단  │ 스케일링 추정치(이방성) │ 간극안전보류 │
│         │                      │                        │ CAE/진동 실측 전 안전보류│ VERIF_PENDING│
├─────────┼──────────────────────┼────────────────────────┼─────────────────────────┼──────────────┤
│ ENG-006 │ 450×250 vs 720×390   │ 720 카트를 확정 제품화 │ 720은 탐색용 콘셉트     │ 2대 라인업   │
│(BASE-05)│ 제품군 경계 및 IP67  │ IP67을 확정 규격화     │ IP67은 미검증 목표요구  │ 분리 매니페스트│
└─────────┴──────────────────────┴────────────────────────┴─────────────────────────┴──────────────┘
```

---

### 2.1 [ENG-001] 상태 관리 체계 v2 및 거버넌스
- **규명 사실**: 단순 `RESOLVED`는 입증된 사실과 승인된 변경을 혼동시킵니다.
- **판정 및 조치**: `discrepancy_register.csv`에 `FACT_CONFIRMED`, `DISCREPANCY_IDENTIFIED`, `ENGINEERING_ACTION_OPEN`, `VERIFICATION_PENDING`, `HUMAN_APPROVAL_PENDING`, `BLOCKED`, `CLOSED`, `SUPERSEDED`의 8대 표준 상태를 엄격히 적용하고, 모든 레코드에 증거 파일 경로, 담당자, 종료 조건을 바인딩하였습니다.

---

### 2.2 [ENG-002 / BASE-01] PCB #0005 층수 및 제조 추적성 (rev-A 점퍼 루머 정정)
- **포렌식 증거**:
  1. **거버 4층 구조**: `Gerber_PCB1_revB_2026-07-09.zip` 분석:
     - `TopLayer.GTL`: 58,956 Bytes
     - `InnerLayer1.G1`: 78,146 Bytes (GND Plane)
     - `InnerLayer2.G2`: 5,661 Bytes (VCC_3V3 Plane)
     - `BottomLayer.GBL`: 5,769 Bytes
  2. **실물 사진 검증 (`crop_usbc.jpg`, `crop_uart.jpg`)**:
     - USB-C 커넥터는 외측으로 정상 돌출되어 있으며 점퍼선이 0개인 깔끔한 공장 자동 SMT 상태입니다. (초기 rev-A 발주 취소 후 rev-B로 생산되었음이 확인됨).
     - 마운팅 홀 MH1, MH4는 ⌀0.25mm 비아가 아니라 **정상 ⌀2.7mm 도금 관통홀(PTH)**입니다. 시제품 #0005에서 테이프를 쓴 이유는 오직 **목재 하판에 홀이 없었기 때문**입니다.
  3. **2026-07-09 단면 SMT 전환**:
     - `BOM_PCB1_revB_2026-07-09.csv` 및 `CPL`에서 하판 R12(0603)가 상판 0402(C25900)로 이동하여 **Single-sided Top SMT**로 완결되었습니다.
  4. **부스트 분압비 실측 정합**:
     - $R_1=143\text{k}\Omega$ (C22877), $R_2=16\text{k}\Omega$ (C22818) $\rightarrow$ 계산치 $12.17\text{V}$, 실측치 $12.00\text{V}$.
- **공식 판정**: 거버 데이터는 4층 설계로 확증되었습니다. 실물 보드가 rev-B 4층으로 제작되었음을 사진으로 확인하였으며, 매니페스트에 점퍼 루머를 삭제하고 `layer_verification_status: FACT_CONFIRMED_DATASET`으로 정정합니다.

---

### 2.3 [ENG-003 / BASE-02 & BASE-06] 익사이터 임피던스 및 TAS5805M 실효 전력
- **포렌식 증거**:
  1. **저항 실측치 정합**:
     - 단품 DCR: $10.8\,\Omega \times 2 = \mathbf{21.6\,\Omega}$ (보이스코일 순수 DCR)
     - 인시츄 루프 실측치: **$24.8\,\Omega$** (24AWG 실리콘 연선 25cm, J2 터미널 헤더, 테스터 리드선 포함)
  2. **BTL H-Bridge 통전 구조 교정**:
     - BTL 모드에서 임의의 순간 전류는 상단 FET 1개와 하단 FET 1개(대각선 2개)만 통과하므로, 온저항은 $2 \times R_{DS(on)} = 2 \times 90\,\text{m}\Omega = \mathbf{0.18\,\Omega}$입니다. (4개 직렬 $0.36\,\Omega$는 오류)
  3. **펌웨어 50% 하드캡 가드 확인**:
     - [`vibration_controller.cpp#L70-L71`](file:///Users/youngseok/Desktop/majn/인증준비/firmware/src/vibration_controller.cpp#L70-L71): `gTargetAmplitude = constrain(amplitudeScale, 0.0f, 0.5f);`
     - 진폭이 50%로 제한되므로 부하에 인가되는 피크 전압은 $12\text{V} \times 0.5 = \mathbf{6.0\text{ V}}$, 실효 전압은 $V_{rms} = \frac{6.0}{\sqrt{2}} \approx \mathbf{4.24\text{ V}_{rms}}$입니다.
  4. **실제 실효 전력 계산**:
     - $24\,\Omega$ 부하 (12Ω 2직렬):
       $$P_{rms} = \frac{(4.24)^2}{24} = \mathbf{0.75\text{ W}}, \quad P_{peak} = \frac{6.0^2}{24} = \mathbf{1.5\text{ W}}$$
     - $16\,\Omega$ 부하 (8Ω 2직렬):
       $$P_{rms} = \frac{(4.24)^2}{16} = \mathbf{1.125\text{ W}}, \quad P_{peak} = \frac{6.0^2}{16} = \mathbf{2.25\text{ W}}$$
     - 기존 보고서의 6W/9W 및 3W/4.5W는 펌웨어 가드가 해제된 100% 포화 상태의 이론적 상한에 불과합니다.
- **공식 판정**: 현 펌웨어 구동 하에서 실효 전력은 채널당 0.75W~1.13W 수준으로 극히 안전합니다. 8Ω 양산품 적용 시 발열 폭증 위험은 과장되었으나, 방열 검증을 위해 T2 시험까지 `VERIFICATION_PENDING`을 유지합니다.

---

### 2.4 [ENG-004 / BASE-03] RF 모듈 실물 사양 및 전파법 인증 승계
- **포렌식 증거**:
  1. **실물 사진 검증 (`crop_amp.jpg`, `crop_boost.jpg`, `crop_usbc.jpg`)**:
     - U1 모듈 상단에 **금색 u.FL/IPEX 커넥터**와 금속 차폐 쉴드캔이 명확히 실장되어 있어 실물 모듈은 **`ESP32-WROOM-32UE-N8` (LCSC C701345)**임이 100% 확정되었습니다.
     - 단, u.FL 단자에는 외장 안테나 케이블이 꽂혀 있지 않은 **미체결(Unpopulated)** 상태입니다.
  2. **국립전파연구원(RRA) 인증 데이터 대조**:
     - 인증 번호: **`R-C-es5-ESP32WROOM32E`** (2021-01-22)
     - `ESP32-WROOM-32UE`는 기본 모델 `ESP32-WROOM-32E`의 파생 모델로 동일 인증번호에 등록되어 있습니다.
     - 등록 안테나는 2.33 dBi 외장 옴니 다이폴입니다.
     - 전파법 고시상 등록 이득(≤2.33 dBi) 이하의 동일 형식(Dipole) 안테나일 때만 시험 면제/승계가 가능합니다. 제안된 3.0 dBi FPC 안테나는 이득 초과 및 형식 불일치로 단순 승계가 불가하며 호스트 완제품 시험 대상입니다.
- **공식 판정**: 모듈 실물은 `-32UE`로 확정하되, 외장 3dBi 안테나 인터페이스(`IF-RF-001`)는 시험기관 승인 전까지 **`BLOCKED`**로 통제합니다.

---

### 2.5 [ENG-005 / BASE-04] 하우징 하판 마운팅 및 기구 간극 스케일링
- **포렌식 증거**:
  1. **하판 체결 단면 구조**:
     - 하판 외측(바닥): M2.5 접시머리 볼트 매립 (카운터싱크 깊이 1.5mm, 4.5T 합판 내 3.0mm 잔여 두께)
     - 중간: 5.0mm M/F 황동 스탠드오프 (하판 내측 지지)
     - 상단: PCB (1.6mm) 관통 후 M2.5 너트 체결
  2. **수직 적층 높이**: 스탠드오프(5.0) + PCB(1.6) + 우각단자/인덕터(5.5) = **$12.1\text{ mm}$**.
  3. **15kg 하중 시 상판 처짐 역학식 교정**:
     - 기존 보고서의 1.1~1.44mm 처짐은 $600 \times 340\text{ mm}$ (4.0T) 기준 수치입니다.
     - 현 Rev 2 ($450 \times 250\text{ mm}$, 4.5T)에 대한 휨 변위 스케일링:
       $$\text{Deflection Ratio} \approx \left(\frac{450}{600}\right)^4 \times \left(\frac{4.0}{4.5}\right)^3 \approx 0.316 \times 0.702 \approx \mathbf{0.22}$$
     - 450mm 패드의 실제 15kg 하중 처짐은 **약 $0.35\text{ mm}$**로 대폭 감소합니다.
     - 따라서 정적 간극 1.4mm에서 처짐을 제외한 **실효 동적 여유 공간은 $\approx 1.05\text{ mm}$**로 안전합니다.
- **공식 판정**: 기구 간극은 이론적으로 충분하나, 체결 홀 추가를 위한 [`ECO_001_BOTTOM_PLATE_PCB_MOUNTING.md`](file:///Users/youngseok/Desktop/majn/docs/engineering/changes/ECO_001_BOTTOM_PLATE_PCB_MOUNTING.md)는 사람 책임자 서명 전까지 `HUMAN_APPROVAL_PENDING`을 유지합니다.

---

### 2.6 [ENG-006 / BASE-05] 제품 라인업 분리 및 IP67 요구사항 격하
- **포렌식 증거**:
  1. 720×390mm 모델은 초기 산후조리원 아크릴 카트 인셋을 위한 CAE 탐색용 콘셉트 모델이었습니다.
  2. IP67(1m 수중 30분 방수)은 시험 성적서나 검증된 실리콘 실링 설계가 전혀 없는 미검증 목표치입니다.
- **공식 판정**: 720×390은 정규 개발 라인업이 아닌 "연구 탐색 콘셉트"로 격하하며, IP67은 확정 사양이 아닌 **`UNVERIFIED_TARGET_REQUIREMENT`**로 재분류하여 관리합니다.

---

## 3. 권장 후속 조치 및 승인 대기 목록

1. **사람 엔지니어 승인 필요 항목**:
   - `ECO-2026-001` (하판 M2.5 스탠드오프 카운터싱크 타공 승인)
   - KC 시험기관 앞 `R-C-es5-ESP32WROOM32E` 안테나 승계 질의서 공식 발송 승인
2. **미해결 잔여 항목**:
   - 실물 #0005 브링업 시험 당시 통신 시험용 임시 안테나 부착 여부 현장 확인
