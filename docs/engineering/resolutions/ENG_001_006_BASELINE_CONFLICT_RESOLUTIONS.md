# [MAJN Engineering System] ENG-001 ~ ENG-006 기준선 충돌 정밀 검증 및 기술 정합성 감사 종합 보고서 (Round 3 Fully Reconciled)

- **문서 ID**: `MAJN-ENG-RES-001-006`
- **상태**: Draft for Human & Peer Review (Round 3 Technical Consistency Audited)
- **기준 브랜치**: `docs/eng-001-006-evidence-audit` (Commit `9c2a721`)
- **작업 브랜치**: `docs/eng-001-006-consistency-audit`
- **참조 문서**:
  - `docs/engineering/ENGINEERING_DEVELOPMENT_PLAN_INDEX.md`
  - `docs/engineering/ENGINEERING_RISK_AND_CONFLICT_REGISTER.md`
  - `docs/engineering/ENGINEERING_WORK_PACKAGE_BACKLOG.md`
  - `docs/engineering/manifests/CFG_PROTO_0005_MANIFEST.yaml`
  - `docs/engineering/changes/ECO_001_BOTTOM_PLATE_PCB_MOUNTING.md`

---

## 1. 개요 및 3대 층위 구분 원칙

본 문서는 MAJN 스마트 배시넷 엔지니어링 개발계획 1주차(ENG-001 ~ ENG-006) 과제에 대해 3차 기술 정합성 감사를 수행하고 내부 수치 충돌을 전면 제거한 공식 기술 보고서입니다.

감사 원칙에 따라 모든 엔지니어링 서술을 다음 **3대 층위**로 엄격히 분리하여 관리합니다:
1. **증거로 확인된 사실 (Fact Confirmed)**: 원본 파일 해시, 거버 내층, 고해상도 실물 사진(`crop_*.jpg`), DMM 측정 로그, 파싱된 DXF 형상.
2. **증거를 바탕으로 한 해석/계산 (Analysis / Calculation / Calculated Estimate)**: 4층 제조 스택업 해석, 계측 경로별 저항 차이, 펌웨어 50% 진폭 클램프 가정 계산값, 기구 판 휨 스케일링 추정치.
3. **아직 승인되지 않은 설계 가설 (Unapproved Target / Hypothesis)**: 외장 안테나 형식 승계, 하판 스탠드오프 가공, 720 카트 제품군 및 IP67 방수 요구사항.

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
│ ENG-002 │ PCB #0005 층수 및    │ "2-Layer #0005" vs     │ 거버 4층 + 사진 확인    │ 4층 설계 확인│
│(BASE-01)│ 실물 제조 추적성     │ "점퍼 와이어 rev-A" 오해│ rev-B 정상 SMT, 07-09BOM│ 실물추적 유지│
├─────────┼──────────────────────┼────────────────────────┼─────────────────────────┼──────────────┤
│ ENG-003 │ 익사이터 부하 저항   │ 21.6Ω vs 24.8Ω         │ 단품 DCR 10.8Ω×2=21.6Ω  │ 계측경로 차이│
│(BASE-02)│ 및 BTL 전력 계산     │ 100% 포화 6W/9W 계산   │ 루프 24.8Ω, FW 50% 캡   │ CALCULATED_  │
│         │                      │ 0.75W/1.13W 안전 속단  │ DSP 볼륨 -28.5dB 추가   │ ESTIMATE 표기│
├─────────┼──────────────────────┼────────────────────────┼─────────────────────────┼──────────────┤
│ ENG-004 │ RF 모듈 실물 사양 및 │ 32E(PCB안테나) vs 32UE │ 사진상 u.FL 실장 확인   │ 모듈은 32UE  │
│(BASE-03)│ KC 전파인증 승계     │ 2.33dBi 법적상한 오인  │ R-C-es5-ESP32WROOM32E   │ 외장안테나   │
│         │                      │                        │ u.FL 미체결(BLOCKED)    │ BLOCKED 유지 │
├─────────┼──────────────────────┼────────────────────────┼─────────────────────────┼──────────────┤
│ ENG-005 │ 하판 마운팅 홀 누락  │ "0.25mm 홀 결함" 오인  │ 기판 홀은 정상 ⌀2.7mm   │ ECO-001 제안 │
│(BASE-04)│ 및 체결 간극         │ 15kg 처짐 1.8mm 오인   │ 450mm 처짐 0.35mm 추정  │ Würth 970050154│
│         │                      │ 1.05mm 안전 간극 속단  │ 동적 안전성 계측 대기   │ HUMAN_APPROV │
├─────────┼──────────────────────┼────────────────────────┼─────────────────────────┼──────────────┤
│ ENG-006 │ 450×250 vs 720×390   │ 720 카트를 확정 제품화 │ 720은 탐색용 콘셉트     │ 2대 라인업   │
│(BASE-05)│ 제품군 경계 및 IP67  │ IP67 확정 요구사항 서술│ 방수 시험 근거 전무     │ 목표사양 격하│
└─────────┴──────────────────────┴────────────────────────┴─────────────────────────┴──────────────┘
```

---

### 2.1 [ENG-001] 상태 관리 체계 v2 및 거버넌스
- **규명 사실**: 단순 `RESOLVED`는 입증된 사실과 승인된 변경을 혼동시킵니다.
- **판정 및 조치**: `discrepancy_register.csv`에 `FACT_CONFIRMED`, `DISCREPANCY_IDENTIFIED`, `ENGINEERING_ACTION_OPEN`, `VERIFICATION_PENDING`, `HUMAN_APPROVAL_PENDING`, `BLOCKED`, `CLOSED`, `SUPERSEDED`의 8대 표준 상태를 엄격히 적용하고, 모든 레코드에 증거 파일 경로, 담당자, 종료 조건을 바인딩하였습니다.

---

### 2.2 [ENG-002 / BASE-01] PCB #0005 층수 및 제조 추적성 (rev-A 점퍼 루머 정정)
- **포렌식 증거**:
  1. **거버 4층 구조**: `Gerber_PCB1_revB_2026-07-09.zip` (최종 단면 SMT 릴리즈) 전수 검증:
     - `Gerber_TopLayer.GTL`: **63,216 Bytes**
     - `Gerber_InnerLayer1.G1`: **78,094 Bytes (Inner 1 - GND Plane)**
     - `Gerber_InnerLayer2.G2`: **5,609 Bytes (Inner 2 - VCC_3V3 Plane)**
     - `Gerber_BottomLayer.GBL`: **5,884 Bytes**
  2. **실물 사진 검증 (`crop_usbc.jpg`, `crop_uart.jpg`)**:
     - USB-C 커넥터는 외측으로 정상 돌출되어 있으며 점퍼선이 0개인 깔끔한 공장 자동 SMT 상태입니다. (초기 rev-A 발주 취소 후 rev-B로 생산되었음이 확인됨).
     - 마운팅 홀 MH1, MH4는 ⌀0.25mm 비아가 아니라 **정상 ⌀2.7mm 도금 관통홀(PTH)**입니다. 시제품 #0005에서 테이프를 쓴 이유는 오직 **목재 하판에 홀이 없었기 때문**입니다.
  3. **2026-07-09 단면 SMT 전환**:
     - `BOM_PCB1_revB_2026-07-09.csv` 및 `CPL`에서 하판 R12(0603)가 상판 0402(C25900)로 이동하여 **Single-sided Top SMT**로 완결되었습니다.
  4. **부스트 분압비 실측 정합**:
     - $R_1=143\text{k}\Omega$ (C22877), $R_2=16\text{k}\Omega$ (C22818) $\rightarrow$ 계산치 $12.17\text{V}$, 실측치 $12.00\text{V}$.
- **공식 판정**: 거버 데이터셋의 4층 설계는 `FACT_CONFIRMED`이나, 실물 #0005 기판의 공장 출하 성적서 및 주문 영수증과의 1:1 바인딩 추적성은 **`VERIFICATION_PENDING`**으로 유지합니다.

---

### 2.3 [ENG-003 / BASE-02 & BASE-06] 익사이터 임피던스 및 TAS5805M BTL 전력 모델
- **포렌식 증거**:
  1. **저항 실측치 정합**:
     - 단품 DCR: $10.8\,\Omega \times 2 = \mathbf{21.6\,\Omega}$ (보이스코일 순수 직류 저항)
     - 인시츄 루프 실측치: **$24.8\,\Omega$** (24AWG 실리콘 연선 25cm, J2 터미널 헤더, 테스터 리드선 포함 DCR)
  2. **BTL H-Bridge 통전 구조**:
     - BTL 모드에서 임의의 순간 전류는 상단 FET 1개와 하단 FET 1개(대각선 2개)만 통과하므로 온저항은 $2 \times R_{DS(on)} = 2 \times 90\,\text{m}\Omega = \mathbf{0.18\,\Omega}$입니다.
  3. **펌웨어 다중 감쇄 체계 확인**:
     - **진폭 제한**: [`vibration_controller.cpp#L70-L71`](file:///Users/youngseok/Desktop/majn/인증준비/firmware/src/vibration_controller.cpp#L70-L71)에서 `gTargetAmplitude = constrain(amplitudeScale, 0.0f, 0.5f);` ($-6.02\,\text{dBFS}$).
     - **디지털 볼륨 감쇄**: [`amplifier_manager.cpp#L8, L99-L100`](file:///Users/youngseok/Desktop/majn/인증준비/firmware/src/amplifier_manager.cpp#L8-L100)에서 `gCurrentVolume = 72`로 설정되어 마스터 볼륨 레지스터 `0x4C`에 `0x69` 기록 ($-28.5\,\text{dB}$ 감쇄).
     - **합산 디지털 감쇄**: 앰프 입력단에서 이미 **$-34.5\,\text{dB}$** 감쇄가 인가됩니다.
  4. **이론 계산치와 실측 전력의 엄격한 분리**:
     - **100% 구형파 이론 상한치 (무제한 포화)**: $P_{peak} = \frac{12^2}{24} = \mathbf{6.0\text{ W}}$ ($24\,\Omega$) / $\mathbf{9.0\text{ W}}$ ($16\,\Omega$) $\rightarrow$ `CALCULATED_ESTIMATE (theoretical peak)`.
     - **100% 정현파 이론 상한치 (무제한)**: $P_{rms} = \frac{(12/\sqrt{2})^2}{24} = \mathbf{3.0\text{ W}}$ ($24\,\Omega$) / $\mathbf{4.5\text{ W}}$ ($16\,\Omega$) $\rightarrow$ `CALCULATED_ESTIMATE (theoretical RMS)`.
     - **50% 진폭 클램프 정현파 가정치**: 피크 6.0V, 실효 4.24V 가정 시 $P_{rms} = \mathbf{0.75\text{ W}}$ ($24\,\Omega$) / $\mathbf{1.125\text{ W}}$ ($16\,\Omega$) $\rightarrow$ `CALCULATED_ESTIMATE (sine assumption)`.
     - **실제 부하 소모 전력**: 주파수별 부하 임피던스 $Z(f)$ 및 역기전력(Back-EMF), DSP 감쇄가 반영된 실제 전력은 **`UNVERIFIED (실측 자료 부재)`** 상태입니다.
- **공식 판정**:
  - Manifest, Discrepancy Register, Interface Registry의 수치를 `CALCULATED_ESTIMATE`로 일원화하고, 실제 출력전압 및 전력은 `UNVERIFIED`로 명시합니다.
  - 오실로스코프 고전압 차동 프로브 및 전류 프로브를 통한 BTL 전압 파형 계측 전까지, 8Ω 익사이터의 열안전성은 **`VERIFICATION_PENDING`**으로 유지하며 승인을 엄격히 유보합니다.

---

### 2.4 [ENG-004 / BASE-03] RF 모듈 실물 사양 및 전파법 인증 승계
- **포렌식 증거**:
  1. **실물 사진 검증 (`crop_amp.jpg`, `crop_boost.jpg`, `crop_usbc.jpg`)**:
     - U1 모듈 상단에 **금색 u.FL/IPEX 커넥터**와 금속 차폐 쉴드캔이 명확히 실장되어 있어 실물 모듈은 **`ESP32-WROOM-32UE-N8` (LCSC C701345)**임이 100% 확정되었습니다.
     - 단, u.FL 단자에는 외장 안테나 케이블이 꽂혀 있지 않은 **미체결(Unpopulated)** 상태입니다. 10월 24일 통신 성공은 안테나 없는 근거리 누설파 시험이었으므로 정규 RF 통신 시험으로 인정할 수 없습니다.
  2. **국립전파연구원(RRA) 인증 데이터 대조**:
     - 인증 번호: **`R-C-es5-ESP32WROOM32E`** (2021-01-22).
     - `ESP32-WROOM-32UE`는 기본 모델 `ESP32-WROOM-32E`의 파생 모델로 동일 인증번호에 등록되어 있습니다.
     - 등록 안테나는 2.33 dBi 외장 옴니 다이폴입니다.
     - 전파법 고시상 등록 이득(≤2.33 dBi) 이하의 동일 형식(Dipole) 안테나일 때만 시험 면제/승계가 가능합니다. 제안된 3.0 dBi FPC 안테나는 이득 초과(+0.67 dBi) 및 형식 불일치로 단순 승계가 불가하며 호스트 완제품 시험 대상입니다.
- **공식 판정**: 모듈 실물은 `-32UE`로 확정하되, 외장 3dBi 안테나 인터페이스(`IF-RF-001`)는 시험기관 승인 전까지 **`BLOCKED`**로 통제합니다.

---

### 2.5 [ENG-005 / BASE-04] 하우징 하판 마운팅 및 기구 간극 스케일링
- **포렌식 증거**:
  1. **상용 스탠드오프 정규 MPN 확정 (Würth Elektronik)**:
     - 구버전 문서의 `971050244`(M2 수-암) 및 RAF `2059-256-AL`(인치 규격) 오류를 전면 기각합니다.
     - 공식 정규 MPN: **Würth Elektronik `970050154`** (시리즈: WA-SBRII, 황동 니켈도금, M2.5 암-암, 전장 $L=5.0\,\text{mm}$, 대변 거리 $AF=5.0\,\text{mm}$). (스틸 대체품: `970050151` / WA-SSTII).
  2. **체결 단면 5요소 및 나사산 결합 구조**:
     - 하판 외측: M2.5 × 6mm 접시머리 볼트 (ISO 10642, 90° 카운터싱크 깊이 1.5mm 매립, 잔여 합판 3.0mm, 하부 암나사 맞물림 깊이 $3.0\,\text{mm}$).
     - 지지부: Würth `970050154` (L=5.0mm, 하판 내측 지지, 기판 하면 ⌀5.0mm GND 패드와 섀시 접지 형성).
     - 기판부: PCB rev-B (두께 1.6mm, ⌀2.7mm PTH 관통).
     - 절연부: M2.5 나일론 와셔 (두께 0.5mm, 외경 ⌀5.0mm, PA66, 볼트 회전 마찰에 의한 솔더마스크 박리 방지).
     - 상단 체결: M2.5 × 5mm 팬헤드 볼트 (ISO 7045, 상부 암나사 맞물림 깊이 $2.9\,\text{mm}$).
  3. **PCB 마운팅 홀 중심 편심 (X축 +1.27mm Offset)**:
     - PCB 외곽 중심은 $(39.37, 31.115)\,\text{mm}$이나, 홀 기하 중심은 $(38.10, 30.988)\,\text{mm}$로 **X축 $+1.27\,\text{mm}$의 편심**이 존재합니다.
     - 하판 중심 $(225.0, 125.0)$ 대칭 타공 시 PCB 외곽은 $X=184.36\,\text{mm} \sim 268.18\,\text{mm}$로 안착되어 좌우 여유 간격 편차($164.36\,\text{mm}$ vs $161.82\,\text{mm}$)가 발생함을 도면에 명시해야 합니다.
  4. **상판 처짐 스케일링 추정치 및 동적 간극 검증 보류**:
     - $600 \times 340\,\text{mm}$ (4.0T) 데이터 기반 스케일링치($\approx 0.35\,\text{mm}$)는 직교이방성($E_L \approx 10\,\text{GPa}, E_T \approx 4.5\,\text{GPa}$) 및 10볼트 경계조건이 미반영된 **`ROUGH_SCALING_ESTIMATE`**입니다.
     - 따라서 정적 간극 1.4mm에서 0.35mm를 차감한 $1.05\,\text{mm}$를 "안전한 동적 간극"으로 선언하는 것을 철회하고, **`VERIFICATION_PENDING`**으로 전환합니다.
- **공식 판정**:
  - 실제 CAE 구조해석 및 시제품 30~65Hz 가진 하중 시험에서 최소 동적 간극 $\ge 0.5\,\text{mm}$가 확인될 때까지 기구 간극의 안전성 판정을 유보합니다.
  - [`ECO_001_BOTTOM_PLATE_PCB_MOUNTING.md`](file:///Users/youngseok/Desktop/majn/docs/engineering/changes/ECO_001_BOTTOM_PLATE_PCB_MOUNTING.md)는 사람 책임자 서명 전까지 `HUMAN_APPROVAL_PENDING` 상태를 유지합니다.

---

### 2.6 [ENG-006 / BASE-05] 제품 라인업 분리 및 IP67 요구사항 격하
- **포렌식 증거**:
  1. 720×390mm 모델은 초기 산후조리원 아크릴 카트 인셋을 위한 CAE 탐색용 콘셉트 모델(`CFG-HOSPITAL-720-CONCEPT`)입니다.
  2. IP67(1m 수중 30분 방수)은 시험 성적서나 검증된 실리콘 실링 설계가 전혀 없는 미검증 목표치입니다.
- **공식 판정**: 720×390은 정규 개발 라인업이 아닌 "연구 탐색 콘셉트"로 격하하며, IP67은 확정 사양이 아닌 **`UNVERIFIED_TARGET_REQUIREMENT`**로 재분류하여 관리합니다.

---

## 3. 권장 후속 조치 및 승인 대기 목록

1. **사람 엔지니어 승인 필요 항목**:
   - `ECO-2026-001` Rev 3 (하판 M2.5 스탠드오프 Würth `970050154` 기반 카운터싱크 타공 승인)
   - KC 시험기관 앞 `R-C-es5-ESP32WROOM32E` 안테나 승계 질의서 공식 발송 승인
   - 8Ω 양산 익사이터 T2 부하·발열 실측 시험 프로토콜 승인
2. **미해결 잔여 항목**:
   - TAS5805M BTL 차동 전압 파형 및 주파수별 실효 전력 실측 데이터 부재 (오실로스코프 차동 프로브 계측 대기)
   - 450×250mm 4.5T 자작합판의 15kg 하중 시 실제 휨 변위 및 30~65Hz 진동 중 PCB 간극 실측 부재 (CAE 및 다이얼 게이지 계측 대기)
