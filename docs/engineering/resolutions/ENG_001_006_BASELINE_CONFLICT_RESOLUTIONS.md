# [MAJN Engineering System] ENG-001 ~ ENG-006 기준선 충돌 정밀 검증 및 기술 정합성 감사 종합 보고서 (Round 7 Failure Mode Analysis & Test Plan Aligned)

- **문서 ID**: `MAJN-ENG-RES-001-006`
- **개정 차수**: Rev 7 (Round 7 — FMEA 고장 모드 전수 식별, 상하부 시험 분리, 역학 하중 재정리 및 8EA 시편 배분 재설계)
- **상태**: Draft for Human & Peer Review (Round 7 Failure Modes & Test Plan Aligned)
- **기준 브랜치**: `docs/eng-001-006-round6-testplan-alignment` (Commit `0d7c707`)
- **작업 브랜치**: `docs/eng-001-006-round7-failure-mode-testplan`
- **참조 문서**:
  - `docs/engineering/ENGINEERING_DEVELOPMENT_PLAN_INDEX.md`
  - `docs/engineering/ENGINEERING_RISK_AND_CONFLICT_REGISTER.md`
  - `docs/engineering/ENGINEERING_WORK_PACKAGE_BACKLOG.md`
  - `docs/engineering/manifests/CFG_PROTO_0005_MANIFEST.yaml`
  - `docs/engineering/changes/ECO_001_BOTTOM_PLATE_PCB_MOUNTING.md`
  - `docs/engineering/verification/ENG_001_006_ROUND7_FAILURE_MODE_AND_TEST_PLAN.md`
  - `docs/engineering/verification/coupon_test_data_template.csv`
  - `docs/engineering/baseline/discrepancy_register.csv`
  - `docs/engineering/baseline/interface_registry.csv`

---

## 1. 개요 및 3대 층위 구분 원칙

본 문서는 MAJN 스마트 배시넷 엔지니어링 개발계획 1주차(ENG-001 ~ ENG-006) 과제에 대해 7차 정밀 감사를 수행하여, **ECO-001 대안 A의 23대 잠재 고장 모드 전수 식별(FMEA)**, **상부 황동 나사산 전단과 하부 목재 체결부 파손의 독립 분리 시험 설계**, **인발 하중 역학 경로 분석 및 임의 수치 TBD 격하**, **진동 시험 프로토콜 정밀화**, 그리고 **대안 C 시험 제외에 따른 8EA 시편 재배분**을 정립한 종합 기술 감사 보고서입니다.

감사 원칙에 따라 모든 엔지니어링 서술을 다음 **3대 층위**로 엄격히 분리하여 관리합니다:
1. **증거로 확인된 사실 (Fact Confirmed)**: 원본 파일 해시, 거버 내층, 고해상도 실물 사진(`crop_*.jpg`), DMM 측정 로그, 파싱된 DXF 형상, 펌웨어 소스 코드 실체, 제조사 공식 카탈로그 사양.
2. **증거를 바탕으로 한 해석/계산 (Analysis / Calculation / Calculated Estimate)**: 4층 제조 스택업 해석, 계측 경로별 저항 차이, 특정 전압 인가 가정 하의 계산 예시, 기구 판 휨 스케일링 추정치. (실측치와 엄격히 구분).
3. **아직 승인되지 않은 설계 가설 및 제안 (Unapproved Target / Hypothesis / Proposed Draft)**: 외장 안테나 형식 승계, ECO-001 하판 체결 대안, 720 카트 제품군 및 IP67 방수 요구사항.

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
│ ENG-003 │ 익사이터 부하 저항   │ 21.6Ω vs 24.8Ω         │ 단품 DCR 10.8Ω×2=21.6Ω  │ 전력모델 정정│
│(BASE-02)│ 및 BTL 전력 계산     │ 구형파 피크전력 오표기 │ 루프 24.8Ω, 부팅 0x30(0dB)│ 실측전력     │
│         │                      │ 감쇄(-34.5dB) 모순     │ PCM 50% 캡과 아날로그 분리│ UNVERIFIED   │
├─────────┼──────────────────────┼────────────────────────┼─────────────────────────┼──────────────┤
│ ENG-004 │ RF 모듈 실물 사양 및 │ 32E(PCB안테나) vs 32UE │ 사진상 u.FL 실장 확인   │ 모듈은 32UE  │
│(BASE-03)│ KC 전파인증 승계     │ 법적 승계 불가 속단    │ R-C-es5-ESP32WROOM32E   │ 시험기관 질의│
│         │                      │                        │ u.FL 미체결(BLOCKED)    │ BLOCKED 유지 │
├─────────┼──────────────────────┼────────────────────────┼─────────────────────────┼──────────────┤
│ ENG-005 │ 하판 마운팅 홀 누락  │ "0.25mm 홀 결함" 오인  │ 기판 홀은 정상 ⌀2.7mm   │ ECO-001 Rev7 │
│(BASE-04)│ 및 체결 실현가능성   │ 하부 맞물림 3.0mm 오계산│ 대안A: 23대 FMEA 도출   │ 대안A상하분리│
│         │                      │ 임의의 0.1Ω GND 검사   │ 대안B: 14.1mm 캐비티충돌│ 8EA시편재배분│
│         │                      │ 섀시 접지 오표기       │ 대안C: 부품부재 시험제외│ GND저항 분리 │
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
     - USB-C 커넥터는 외측으로 정상 돌출되어 있으며 점퍼선이 0개인 깔끔한 공장 자동 SMT 상태입니다.
     - 마운팅 홀 MH1~MH4는 ⌀0.25mm 비아가 아니라 **정상 ⌀2.7mm 도금 관통홀(PTH)**입니다. 시제품 #0005에서 테이프를 쓴 이유는 오직 **목재 하판에 홀이 없었기 때문**입니다.
  3. **2026-07-09 단면 SMT 전환**:
     - `BOM_PCB1_revB_2026-07-09.csv` 및 `CPL`에서 하판 R12(0603)가 상판 0402(C25900)로 이동하여 **Single-sided Top SMT**로 완결되었습니다.
  4. **부스트 분압비 실측 정합**:
     - $R_1=143\text{k}\Omega$ (C22877), $R_2=16\text{k}\Omega$ (C22818) $\rightarrow$ 이론 계산치 $12.17\text{V}$, 실측치 $12.00\text{V}$.
- **공식 판정**: 거버 데이터셋의 4층 설계는 `FACT_CONFIRMED`이나, 실물 #0005 기판의 공장 출하 성적서 및 주문 영수증과의 1:1 바인딩 추적성은 **`VERIFICATION_PENDING`**으로 유지합니다.

---

### 2.3 [ENG-003 / BASE-02 & BASE-06] 익사이터 임피던스 및 TAS5805M BTL 전력 모델 정밀 재감사

- **펌웨어 소스 코드 포렌식 검증 (`amplifier_manager.cpp`, `tas5805m.cpp`, `vibration_controller.cpp`)**:
  1. **TAS5805M 부팅 시 실제 볼륨 레지스터 기록치**:
     - [`tas5805m.cpp#L61-L67`](file:///Users/youngseok/Desktop/majn/인증준비/firmware/src/tas5805m.cpp#L61-L67) 확인 결과, `begin()` 초기화 시 `REG_MASTER_VOL (0x4C)`, `0x4D`, `0x4E` 레지스터에 기록되는 실제 하드웨어 값은 **`0x30` ($0\text{ dB}$, Unity Gain)**입니다.
     - [`amplifier_manager.cpp#L8`](file:///Users/youngseok/Desktop/majn/인증준비/firmware/src/amplifier_manager.cpp#L8)의 `uint8_t gCurrentVolume = 72;`는 익명 네임스페이스 변수 선언일 뿐이며, `initAmplifier()` 내부에서 `setVolume()`을 호출하지 않습니다. `setVolume()`은 BLE 명령 수신 시에만 호출됩니다([`ble_manager.cpp#L262`](file:///Users/youngseok/Desktop/majn/인증준비/firmware/src/ble_manager.cpp#L262)).
  2. **PCM 진폭 제한과 아날로그 전압의 관계**:
     - [`vibration_controller.cpp#L70-L71`](file:///Users/youngseok/Desktop/majn/인증준비/firmware/src/vibration_controller.cpp#L70-L71)의 `gTargetAmplitude = constrain(amplitudeScale, 0.0f, 0.5f);`는 16-bit 사인파 Look-Up Table 샘플을 스케일하여 I2S 디지털 PCM 버퍼로 송출하는 **소프트웨어 디지털 스케일러 ($-6.02\text{ dBFS}$)**입니다.
     - 디지털 PCM 데이터의 절반 감쇄가 아날로그 BTL 출력 차동전압이 PVDD(12V)의 정확히 50%(6V peak)가 됨을 물리적으로 보장하지 않습니다. 아날로그 차동전압은 TAS5805M의 내부 DSP 신호 흐름, PWM 변조율 한계, 데드타임, $R_{DS(on)}$ 전압 강하, PVDD 레일 리플에 의해 변동합니다.
  3. **전력 모델 용어 및 계산식 정밀 재정의**:
     - **이상적 양극성 구형파 부하 평균 전력 이론 상한치 (Ideal Square-Wave Average Load Power Ceiling)**:
       - $V_{rms} = V_{peak} = 12.0\text{ V}$ 가정: $P_{avg, square} = \frac{12^2}{R}$
       - $24\,\Omega$ 부하 시: **$6.0\text{ W}$** / $16\,\Omega$ 부하 시: **$9.0\text{ W}$**
     - **이상적 풀스케일 정현파 부하 평균 전력 이론치 (Ideal Full-Scale Sine Average Power)**:
       - $V_{peak} = 12.0\text{ V}$, $V_{rms} = 8.485\text{ V}$ 가정: $P_{avg, sine} = \frac{(12/\sqrt{2})^2}{R} = \frac{72}{R}$
       - $24\,\Omega$ 부하 시: **$3.0\text{ W}$** / $16\,\Omega$ 부하 시: **$4.5\text{ W}$**
     - **가설적 6.0V peak 정현파 인가 가정 계산 예시 (Hypothetical Clamped Sine Calculation Example)**:
       - $V_{peak} = 6.0\text{ V}$, $V_{rms} = 4.243\text{ V}$ 가정: $P_{avg} = \frac{(6/\sqrt{2})^2}{R} = \frac{18}{R}$
       - $24\,\Omega$ 부하 시: **$0.75\text{ W}$** / $16\,\Omega$ 부하 시: **$1.125\text{ W}$**
     - **실제 부하 소모 전력 (Actual Delivered Power)**:
       - 주파수별(30~65Hz) 복소 임피던스 $Z(f)$, 역기전력, 실제 BTL 차동 전압 파형이 반영된 실제 전력은 **`UNVERIFIED (미확정 / 계측 전)`**입니다.
- **공식 판정**: 오실로스코프 고전압 차동 프로브 및 전류 프로브를 통한 BTL 전압/전류 파형 및 RMS 실측 전까지, 8Ω 익사이터의 열안전성은 **`VERIFICATION_PENDING`**으로 유지합니다.

---

### 2.4 [ENG-004 / BASE-03] RF 모듈 실물 사양 및 전파법 인증 승계 한계 구분

- **포렌식 증거 및 사실 관계 (Fact Confirmed)**:
  1. **실물 모듈 식별**: U1 모듈은 금도금 u.FL 리셉터클과 금속 쉴드캔을 구비한 **`ESP32-WROOM-32UE-N8` (LCSC C701345)**임이 확인되었습니다.
  2. **시제품 #0005 안테나 미체결 사실**: 실물 사진상 u.FL 단자에 외장 안테나가 체결되지 않은 **미체결(Unpopulated)** 상태였습니다. 10월 24일 통신 성공은 안테나 없는 근거리 누설파 시험이었으므로 정규 RF 통신 시험으로 인정할 수 없습니다 (`UNVERIFIED_CONTROLLED_CONDITIONS`).
  3. **국립전파연구원(RRA) 인증 데이터 대조**:
     - 적합인증 번호: **`R-C-es5-ESP32WROOM32E`** (2021-01-22).
     - 등록 안테나 조건: $2.33\text{ dBi}$ 외장 옴니 다이폴 안테나.
- **규제 해석의 엄격한 분리 (Regulatory Interpretation vs Legal Ruling)**:
  - 제안된 3.0 dBi FPC 안테나는 기등록 안테나 규격(2.33 dBi 다이폴) 대비 이득 초과(+0.67 dBi) 및 안테나 형식 변경이 수반됩니다.
  - 단순 변경신고 대상인지 신규 적합성평가 대상인지는 공인 시험기관의 유권해석 사안이므로, **공인 시험기관(KTL/DT&C 등)의 서면 회신 전까지 승계 여부 판정을 보류(`BLOCKED / REGULATORY_INQUIRY_PENDING`)**합니다.

---

### 2.5 [ENG-005 / BASE-04] 하우징 하판 마운팅 구조 및 체결 실현 가능성 재검증 (Round 7 정밀 감사)

- **P0-1: 대안 A 23대 잠재 고장 모드 전수 식별 (Design FMEA 수립)**:
  - 하부 목재 체결부(10개), 상부 황동 스탠드오프(7개), PCB 및 기구 인터페이스(6개) 등 총 23개 잠재 고장 모드를 체계적으로 식별하였습니다.
  - 심각도(S), 발생도(O), 검출도(D)의 평가 척도를 정의하고, 물리 시험 데이터가 없는 발생도 및 RPN은 임의 배점 없이 **전수 `TBD (미검증)`**로 분류하였습니다.
  - FMEA를 수립했다고 실제 고장 안전성이 입증된 것이 아님을 명시하였습니다.

- **P0-2: 상부 나사산 시험과 하부 목재 체결부 시험의 물리적 완전 분리**:
  - 혼합 시험 절차를 폐기하고, 목재 영향을 배제한 강체 소켓 지그 기반 **상부 황동 암나사산 파손 시험(`T0-CP-TOP-01`)**과, 황동 전단을 배제한 고강도 스틸 더미 너트 기반 **하부 목재 압착/인발 시험(`T0-CP-BOT-01`)**으로 완전 분리하였습니다.

- **P0-3: 75N 인발 요구사항 근거 재검토 및 하중 경로 분석**:
  - 25N 케이블 외력은 커넥터 규격서(J1/J2 발거력 2~5N, Type-C 8~20N)에 없는 미검증 추정치임을 규명하였습니다.
  - 외측 케이블 인장력의 90% 이상이 측판 실리콘 그로밋 마찰력으로 흡수되므로 PCB 체결부 직접 전달 가정이 불성립함을 밝혔습니다.
  - $75\,\text{N}$ 인발 요구사항을 **`PROVISIONAL_CALCULATED_ESTIMATE / TBD`**로 격하하고, "실측 시스템 외력 $\times$ 안전율 $\le$ 시편 파손 하중" 체계로 합격 논리를 재수립하였습니다.

- **P0-4: 진동 시험 프로토콜 정밀화 (`T0-VIB-01`)**:
  - 제어점(`ACC-1`, $2.0\,\text{G}$ 일정), 하판 응답(`ACC-2`), PCB 응답(`ACC-3`)을 분리하고, 센서 자체 질량을 $\le 1.0\,\text{g}$로 제한하여 동특성 왜곡을 차단하였습니다.
  - AL6061 지그 4변 클램핑, 30~65Hz 로그 스위프(53회 왕복), 공진 체류(30분), 인덱스 각도 마킹 계측을 정의하였습니다. 잔류 풀림 토크를 실제 체결 축력과 동일시하지 않도록 주의를 명시하였습니다.

- **P0-5: 대안 C 부품 실체 조사 및 시험 제외**:
  - RAMPA(M4부터), E-Z LOK(M3부터), Kerb-Konus(Ensat 6.0mm 관통) 조사 결과 4.5T 합판용 M2.5 상용 부품이 부재함을 확인하였습니다.
  - 대안 C를 시험 대상에서 공식 제외하고 **`CONCEPT_ONLY`**로 동결하였으며, 해당 3개 시편을 대안 A 독립 시험에 재배분하였습니다.

- **P1: 접지(GND) 경로 물리적 분리 및 합격 기준선**:
  - 스탠드오프 외면 $\leftrightarrow$ USB-C 셸 간 **전체 경로 저항($R_{path,total}$)**과 스탠드오프 상면 $\leftrightarrow$ PCB 하면 패드 간 **계면 접촉 저항($R_{contact,interface}$)**을 물리적으로 엄격히 분리하였습니다.
  - 임의의 $15\,\text{m}\Omega$ 기준을 철회하고 시편 실측 후 확정(`TBD`)으로 관리합니다.

- **P1: 시편 수량 배분 및 N=3 의미 한계 명시**:
  - $N=3$은 통계적 유의성이나 신뢰성 입증이 아닌 **"초기 조기 결함 스크리닝(Early Engineering Screening)"** 목적으로만 한정하여 해석합니다.
  - G-1 하부 파괴(3EA), G-2 진동/상부 파괴(3EA), G-3 참조(2EA)의 **총 8EA 권장 배분안**을 수립하고 파괴 시험의 후순위 원칙을 명시하였습니다.

---

### 2.6 [ENG-006 / BASE-05] 제품 라인업 분리 및 IP67 요구사항 격하
- **포렌식 증거**:
  1. 720×390mm 모델은 초기 산후조리원 아크릴 카트 인셋을 위한 CAE 탐색용 콘셉트 모델(`CFG-HOSPITAL-720-CONCEPT`)입니다.
  2. IP67(1m 수중 30분 방수)은 시험 성적서나 실리콘 실링 설계가 전혀 없는 미검증 목표치입니다.
- **공식 판정**: 720×390은 정규 개발 라인업이 아닌 "연구 탐색 콘셉트"로 격하하며, IP67은 확정 사양이 아닌 **`UNVERIFIED_TARGET_REQUIREMENT`**로 재분류하여 관리합니다.

---

## 3. 권장 후속 조치 및 승인 대기 목록

1. **사람 엔지니어 승인 및 결정 필요 항목**:
   - `ECO-2026-001` Rev 7 및 `ENG_001_006_ROUND7_FAILURE_MODE_AND_TEST_PLAN.md` 시험 계획 승인 (`CONDITIONALLY_READY_WITH_OPEN_ITEMS`).
   - 대안 A 시험 결과에 따른 채택/기각 방침 확정 (시험 불합격 시 대안 A 즉각 기각).
   - 메인 결정 로그(Decision 10, 6볼트) vs Rev 2 DXF(10볼트) 충돌 공식 해소 결정.
   - KC 시험기관 앞 `R-C-es5-ESP32WROOM32E` 안테나 승계 질의서 공식 발송 승인.
   - 8Ω 양산 익사이터 T2 부하·발열 실측 시험 프로토콜 승인.
2. **미해결 잔여 실측 항목 (Verification Pending)**:
   - 합판 시편 CP-BOT-01~03 목재 압착 항복 토크 및 축방향 인발 파손 하중 실측.
   - 합판 시편 CP-VIB-01~03 진동 후 상부 나사산 잔류 풀림각 및 파손 토크 실측.
   - TAS5805M BTL 차동 전압 파형 및 주파수별 실효 전력 실측 데이터 부재 (오실로스코프 고전압 차동 프로브 계측 대기).
   - 450×250mm 4.5T 자작합판의 15kg 하중 시 실제 휨 변위 및 30~65Hz 진동 중 PCB 간극 실측 부재 (CAE 및 다이얼 게이지 계측 대기).
