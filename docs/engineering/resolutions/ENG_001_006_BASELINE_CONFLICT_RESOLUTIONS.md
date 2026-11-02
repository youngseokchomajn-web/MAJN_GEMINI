# [MAJN Engineering System] ENG-001 ~ ENG-006 기준선 충돌 정밀 검증 및 기술 정합성 감사 종합 보고서 (Round 4 P0 Calculation & Fastener Verification Audited)

- **문서 ID**: `MAJN-ENG-RES-001-006`
- **개정 차수**: Rev 4 (Round 4 P0 오류 전면 정정 및 체결 구조·전력 모델 재감사)
- **상태**: Draft for Human & Peer Review (P0 Errors Fully Corrected)
- **기준 브랜치**: `docs/eng-001-006-consistency-audit` (Commit `f18fa95`)
- **작업 브랜치**: `docs/eng-001-006-p0-fastener-audit`
- **참조 문서**:
  - `docs/engineering/ENGINEERING_DEVELOPMENT_PLAN_INDEX.md`
  - `docs/engineering/ENGINEERING_RISK_AND_CONFLICT_REGISTER.md`
  - `docs/engineering/ENGINEERING_WORK_PACKAGE_BACKLOG.md`
  - `docs/engineering/manifests/CFG_PROTO_0005_MANIFEST.yaml`
  - `docs/engineering/changes/ECO_001_BOTTOM_PLATE_PCB_MOUNTING.md`
  - `docs/engineering/baseline/discrepancy_register.csv`
  - `docs/engineering/baseline/interface_registry.csv`

---

## 1. 개요 및 3대 층위 구분 원칙

본 문서는 MAJN 스마트 배시넷 엔지니어링 개발계획 1주차(ENG-001 ~ ENG-006) 과제에 대해 4차 정밀 감사를 수행하여, 이전 차수에서 발견된 **BTL 전력 모델의 내부 수치 모순(P0-1)**, **ECO-001 하부 볼트 나사산 맞물림 깊이 계산 오류(P0-2)**, **목재 하우징 내 섀시 접지 오표기(P0-3)** 및 **기준선 경계조건 불일치(P1)**를 전면 정정한 기술 감사 보고서입니다.

감사 원칙에 따라 모든 엔지니어링 서술을 다음 **3대 층위**로 엄격히 분리하여 관리합니다:
1. **증거로 확인된 사실 (Fact Confirmed)**: 원본 파일 해시, 거버 내층, 고해상도 실물 사진(`crop_*.jpg`), DMM 측정 로그, 파싱된 DXF 형상, 펌웨어 소스 코드 실체.
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
│ ENG-005 │ 하판 마운팅 홀 누락  │ "0.25mm 홀 결함" 오인  │ 기판 홀은 정상 ⌀2.7mm   │ ECO-001 M2.5x6│
│(BASE-04)│ 및 체결 간극         │ 하부 맞물림 3.0mm 오계산│ 실제 맞물림 1.5mm 미달  │ 기각/재설계대기│
│         │                      │ 섀시 접지 오표기       │ 목재로 섀시접지 부재    │ 0.5mm 잠정목표│
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

### 2.3 [ENG-003 / BASE-02 & BASE-06] 익사이터 임피던스 및 TAS5805M BTL 전력 모델 정밀 재감사 (P0-1 해결)

- **펌웨어 소스 코드 포렌식 검증 (`amplifier_manager.cpp`, `tas5805m.cpp`, `vibration_controller.cpp`)**:
  1. **TAS5805M 부팅 시 실제 볼륨 레지스터 기록치**:
     - [`tas5805m.cpp#L61-L67`](file:///Users/youngseok/Desktop/majn/인증준비/firmware/src/tas5805m.cpp#L61-L67) 확인 결과, `begin()` 초기화 시 `REG_MASTER_VOL (0x4C)`, `0x4D`, `0x4E` 레지스터에 기록되는 실제 하드웨어 값은 **`0x30` ($0\text{ dB}$, Unity Gain)**입니다.
     - [`amplifier_manager.cpp#L8`](file:///Users/youngseok/Desktop/majn/인증준비/firmware/src/amplifier_manager.cpp#L8)의 `uint8_t gCurrentVolume = 72;`는 익명 네임스페이스 내부 변수 초기값일 뿐이며, `initAmplifier()` 내부에서 `setVolume()`을 호출하지 않습니다. `setVolume()`은 BLE 명령 수신 시에만 호출됩니다([`ble_manager.cpp#L262`](file:///Users/youngseok/Desktop/majn/인증준비/firmware/src/ble_manager.cpp#L262)).
     - **오류 정정**: 이전 보고서에서 주장했던 "부팅 시 마스터 볼륨 -28.5dB가 하드웨어에 상시 인가되어 -34.5dB 합산 감쇄가 적용된다"는 서술은 **실제 펌웨어 코드와 정면 배치되는 허위 서술로 판명되어 전면 삭제**합니다.
  2. **PCM 진폭 제한과 아날로그 전압의 관계**:
     - [`vibration_controller.cpp#L70-L71`](file:///Users/youngseok/Desktop/majn/인증준비/firmware/src/vibration_controller.cpp#L70-L71)의 `gTargetAmplitude = constrain(amplitudeScale, 0.0f, 0.5f);`는 16-bit 사인파 Look-Up Table 샘플을 스케일하여 I2S 디지털 PCM 버퍼로 송출하는 **소프트웨어 디지털 스케일러 ($-6.02\text{ dBFS}$)**입니다.
     - 디지털 PCM 데이터의 절반 감쇄가 아날로그 BTL 출력 차동전압이 PVDD(12V)의 정확히 50%(6V peak)가 됨을 물리적으로 보장하지 않습니다. 아날로그 차동전압은 TAS5805M의 내부 DSP 신호 흐름, PWM 변조율 한계(최대 듀티비 통상 95~97%), 데드타임, $R_{DS(on)}$ 전압 강하, PVDD 레일 리플에 의해 변동합니다.
  3. **내부 수치 모순의 완전한 해소**:
     - 만약 $-34.5\text{ dB}$ 감쇄가 실제 적용된다면, $12\text{V} \times 10^{-34.5/20} \approx 0.226\text{V}_{peak}$ ($V_{rms} \approx 0.160\text{V}$)이 되어 전력은 $0.0011\text{W}$ ($24\,\Omega$) / $0.0016\text{W}$ ($16\,\Omega$)에 불과합니다.
     - 이전 보고서가 "-34.5dB 감쇄가 적용된다"고 주장하면서 동시에 "출력 전력이 0.75W / 1.125W"라고 기재한 것은 **양립 불가능한 수학적 모순**이었습니다.
     - **$0.75\text{ W}$ ($24\,\Omega$) 및 $1.125\text{ W}$ ($16\,\Omega$)는 펌웨어 감쇄나 실측 전력이 아니며, 오직 "부하 양단에 $V_{peak} = 6.0\text{V}$ ($V_{rms} = 4.24\text{V}$) 정현파가 단독으로 인가된다고 가정한 단순 계산 예시(`HYPOTHETICAL_CALCULATION_EXAMPLE`)"로만 엄격히 격하**합니다.
  4. **전력 모델 용어 및 계산식 정밀 재정의**:
     - **이상적 양극성 구형파 부하 평균 전력 이론 상한치 (Ideal Square-Wave Average Load Power Ceiling)**:
       - $V_{rms} = V_{peak} = 12.0\text{ V}$ 가정: $P_{avg, square} = \frac{12^2}{R}$
       - $24\,\Omega$ 부하 시: **$6.0\text{ W}$**
       - $16\,\Omega$ 부하 시: **$9.0\text{ W}$**
       - *(주의: 이는 피크 순시전력이 아니라 지속 구형파 인가 시의 평균 부하전력임)*
     - **이상적 풀스케일 정현파 부하 평균 전력 이론치 (Ideal Full-Scale Sine Average Power)**:
       - $V_{peak} = 12.0\text{ V}$, $V_{rms} = 8.485\text{ V}$ 가정: $P_{avg, sine} = \frac{(12/\sqrt{2})^2}{R} = \frac{72}{R}$
       - $24\,\Omega$ 부하 시: **$3.0\text{ W}$**
       - $16\,\Omega$ 부하 시: **$4.5\text{ W}$**
     - **가설적 6.0V peak 정현파 인가 가정 계산 예시 (Hypothetical Clamped Sine Calculation Example)**:
       - $V_{peak} = 6.0\text{ V}$, $V_{rms} = 4.243\text{ V}$ 가정: $P_{avg} = \frac{(6/\sqrt{2})^2}{R} = \frac{18}{R}$
       - $24\,\Omega$ 부하 시: **$0.75\text{ W}$**
       - $16\,\Omega$ 부하 시: **$1.125\text{ W}$**
     - **실제 부하 소모 전력 (Actual Delivered Power)**:
       - 주파수별(30~65Hz) 복소 임피던스 $Z(f)$, 역기전력, 실제 BTL 차동 전압 파형이 반영된 실제 전력은 **`UNVERIFIED (미확정 / 실측 계측 전)`**입니다.
- **공식 판정**:
  - 오실로스코프 고전압 차동 프로브 및 전류 프로브를 통한 BTL 전압/전류 파형 및 RMS 실측 전까지, 8Ω 익사이터의 열안전성은 **`VERIFICATION_PENDING`**으로 유지하며 부품 승인을 엄격히 유보합니다.

---

### 2.4 [ENG-004 / BASE-03] RF 모듈 실물 사양 및 전파법 인증 승계 한계 구분

- **포렌식 증거 및 사실 관계 (Fact Confirmed)**:
  1. **실물 모듈 식별**: 고해상도 사진 검증(`crop_amp.jpg`, `crop_boost.jpg`, `crop_usbc.jpg`)을 통해 U1 모듈은 금도금 u.FL 리셉터클과 금속 쉴드캔을 구비한 **`ESP32-WROOM-32UE-N8` (LCSC C701345)**임이 확인되었습니다.
  2. **시제품 #0005 안테나 미체결 사실**: 실물 사진상 u.FL 단자에 외장 안테나가 체결되지 않은 **미체결(Unpopulated)** 상태였습니다. 10월 24일 통신 성공은 안테나 없는 근거리 누설파 시험이었으므로 정규 RF 통신 시험으로 인정할 수 없습니다 (`UNVERIFIED_CONTROLLED_CONDITIONS`).
  3. **국립전파연구원(RRA) 인증 데이터 대조**:
     - 적합인증 번호: **`R-C-es5-ESP32WROOM32E`** (2021-01-22).
     - `ESP32-WROOM-32UE`는 기본 모델 `ESP32-WROOM-32E`의 파생 모델로 동일 인증번호에 등록되어 있습니다.
     - 등록 안테나 조건: $2.33\text{ dBi}$ 외장 옴니 다이폴 안테나.
- **규제 해석의 엄격한 분리 (Regulatory Interpretation vs Legal Ruling)**:
  - 제안된 3.0 dBi FPC 안테나는 기등록 안테나 규격(2.33 dBi 다이폴) 대비 이득 초과(+0.67 dBi) 및 안테나 형식 변경이 수반됩니다.
  - 전파법령 및 방송통신기자재등의 적합성평가에 관한 고시상 단순 변경신고 대상인지, 호스트 완제품 차원의 변경/신규 적합성평가 대상인지는 법률적 판단의 영역이며 AI가 단정할 수 없습니다.
  - 따라서 "법적 승계 불가"로 확정 선언하지 않고, **공인 시험기관(KTL/DT&C 등)의 공식 서면 유권해석을 접수하기 전까지 승계 여부 판정을 보류(`BLOCKED / REGULATORY_INQUIRY_PENDING`)**합니다.

---

### 2.5 [ENG-005 / BASE-04] 하우징 하판 마운팅 구조 및 기구 간극 재검증 (P0-2 & P0-3 해결)

- **P0-2: 하부 볼트 나사산 맞물림 깊이 계산 오류 정정**:
  1. **기존 계산의 기하학적 오류 분석**:
     - 이전 보고서: 하판 4.5mm, 카운터싱크 1.5mm, "잔여 합판 3.0mm", 볼트 M2.5 × 6mm $\rightarrow$ "하부 맞물림 $3.0\text{ mm} \ge 1.0d$ 만족"이라고 주장함.
     - **실제 물리적 진실**:
       - 접시머리 볼트(ISO 10642 / DIN 7991)의 공칭 길이 $L = 6.0\text{ mm}$는 **머리 상단면부터 나사 끝까지의 전체 길이(Overall length)**입니다.
       - 볼트 머리가 하판 외측면에 플러시(Flush)하게 안착되었을 때, 볼트는 하판의 카운터싱크 원뿔부($1.5\text{ mm}$)와 원통형 관통홀부($3.0\text{ mm}$)를 합친 **합판 전체 두께 $4.5\text{ mm}$를 관통**합니다.
       - 따라서 하판 내측면 너머로 돌출되어 스탠드오프 하부 암나사 안으로 들어가는 실제 맞물림 깊이는:
         $$L_{\text{engagement}} = L_{\text{bolt}} - T_{\text{plate}} = 6.0\text{ mm} - 4.5\text{ mm} = \mathbf{1.5\text{ mm}}$$
       - 이는 M2.5 호칭 직경($d = 2.5\text{ mm}$) 대비 불과 **$0.6 \times d$** ($1.5 / 2.5 = 0.60$)에 불과하여, 기계공학적 최소 맞물림 기준($\ge 1.0d = 2.5\text{ mm}$)에 현저히 미달합니다. (나사산 피치 $0.45\text{ mm}$ 기준 맞물림 나사산 수 약 3.3산).
     - **판정**: **기존 M2.5 × 6mm 하부 체결안은 체결 강도 미달 및 진동 시 나사 풀림/인발 위험으로 공식 "승인 불가(`REJECTED_AS_IS / REVISION_REQUIRED`)"** 처리합니다.
  2. **상하 볼트 충돌(Collision) 간섭 위험 규명**:
     - 하부 볼트를 $L=8.0\text{ mm}$로 단순 연장할 경우: 하부 진입 깊이는 $8.0 - 4.5 = \mathbf{3.5\text{ mm}}$ ($= 1.4d$)로 기준을 만족합니다.
     - 그러나 스탠드오프(Würth `970050154`)의 전장은 **$5.0\text{ mm}$**입니다.
     - 상부 볼트(M2.5 × 5mm)는 PCB(1.6mm) + 나일론 와셔(0.5mm) = 2.1mm를 관통하여 상부에서 **$2.9\text{ mm}$** 진입합니다.
     - 상하 볼트가 스탠드오프 내부로 진입하는 총 깊이는 $3.5 + 2.9 = \mathbf{6.4\text{ mm}}$가 되어, $5.0\text{ mm}$ 스탠드오프 내부에서 상하 볼트 끝단이 **$1.4\text{ mm}$ 충돌(Interference)**하게 됩니다.
  3. **체결 대안 검토 (Candidate Proposals - CAD 미반영, 인간 엔지니어 검토용)**:
     - **대안 1 (볼트 조합 최적화)**: 하부 M2.5 × 7mm ($7.0 - 4.5 = 2.5\text{ mm} = 1.0d$) + 상부 M2.5 × 4mm ($4.0 - 2.1 = 1.9\text{ mm} = 0.76d$). 합산 깊이 $4.4\text{ mm} \le 5.0\text{ mm}$ (내부 여유 $0.6\text{ mm}$). 단, M2.5×7mm는 비표준 조달품.
     - **대안 2 (스탠드오프 높이 상향)**: 스탠드오프를 $L=6.0\text{ mm}$ 또는 $7.0\text{ mm}$로 상향. 하판 정적 간극이 $1.4\text{ mm} \rightarrow 0.4\text{ mm}$로 감소하므로 목재 캐비티 깊이(13.5mm) 재설계 수반.
     - **대안 3 (목재 인서트 너트 적용)**: 하판에 M2.5 황동 목재 인서트(Insert Nut)를 압입하고, 스탠드오프를 체결하는 방식. 하판 관통볼트 완전 제거.
     - *조치: 모든 대안은 제안 초안으로 유지하며, CAD/DXF에는 일체 반영하지 않음.*

- **P0-3: 접지(GND) 및 절연 구조 재검증**:
  1. **"Chassis GND" 표현 완전 배제**:
     - 배시넷 프레임은 4.5T 자작합판 목재 구조이므로 **금속 섀시나 보호접지(PE) 경로가 물리적으로 부재**합니다.
     - 황동 스탠드오프가 PCB 하면 GND 패드와 접촉하더라도 이는 기구 섀시 접지가 아니며, 단지 **"PCB 신호/전원 GND(Signal/Power GND) 플레인과의 기계적 전기 접촉 구조"**입니다. 문서 내 섀시 접지 표기를 전면 정정합니다.
  2. **접촉 면적 및 절연 구조**:
     - Würth `970050154` 육각 대변 거리 $AF = 5.0\text{ mm}$ (대각 길이 $5.77\text{ mm}$).
     - PCB 하면 패드 외경 ⌀5.0mm 도금면과 면접촉을 형성합니다.
     - 상부 M2.5 나일론 와셔(외경 ⌀5.0mm, 두께 0.5mm, PA66)는 상부 팬헤드 볼트 회전 마찰로부터 PCB 상면 솔더마스크 및 표면 배선을 보호·절연합니다.
  3. **조립 후 접지 연속성 품질 검사 항목(QC) 신설**:
     - 조립 후 DMM 4선식 저항 계측으로 4개 스탠드오프 몸체 $\leftrightarrow$ USB-C 외각 셸(GND) 간 저항 **$\le 0.1\,\Omega$** 확인 의무화.

- **P1: 기구 경계조건 및 검증 기준 정합성**:
  1. **6볼트 vs 10볼트 하우징 기준선 충돌 (DISC-005 영향)**:
     - 메인 결정 로그(Decision 10)의 6볼트 도면과 기구 ADR/Master DXF의 10볼트 체결 간 충돌이 공식 해결되기 전까지, **FEA 구조해석의 10볼트 경계조건은 확정 사실이 아닌 "Rev 2 DXF 기준 잠정 가설 경계조건"으로 명시**합니다.
  2. **동적 간극 0.5mm 성격 규정**:
     - 0.5mm는 영아 안전을 보증하는 공인 법적/규제 기준이 아니며, **"30~65Hz 진동 중 내부 부품 간 바터밍(Bottoming) 간섭을 방지하기 위한 잠정 엔지니어링 설계 검증 목표치(Tentative Design Verification Target)"**로 성격을 명확히 규정합니다.
  3. **체결 토크 $0.25 \sim 0.30\text{ N}\cdot\text{m}$**:
     - 정식 규격이 아닌, 목재 섬유 압축 파손을 방지하기 위한 **"잠정 권장 목표치(Tentative Reference Value)"**로 표기하며, 실제 합판 인발/파손 시험 전까지 확정하지 않습니다.

---

### 2.6 [ENG-006 / BASE-05] 제품 라인업 분리 및 IP67 요구사항 격하
- **포렌식 증거**:
  1. 720×390mm 모델은 초기 산후조리원 아크릴 카트 인셋을 위한 CAE 탐색용 콘셉트 모델(`CFG-HOSPITAL-720-CONCEPT`)입니다.
  2. IP67(1m 수중 30분 방수)은 시험 성적서나 실리콘 실링 설계가 전혀 없는 미검증 목표치입니다.
- **공식 판정**: 720×390은 정규 개발 라인업이 아닌 "연구 탐색 콘셉트"로 격하하며, IP67은 확정 사양이 아닌 **`UNVERIFIED_TARGET_REQUIREMENT`**로 재분류하여 관리합니다.

---

## 3. 권장 후속 조치 및 승인 대기 목록

1. **사람 엔지니어 승인 및 결정 필요 항목**:
   - `ECO-2026-001` Rev 4: M2.5 × 6mm 체결안 기각 확인 및 체결 대안(대안 1: M2.5x7mm+M2.5x4mm, 대안 2: 스탠드오프 높이 상향, 대안 3: 목재 인서트) 중 채택 결정.
   - 메인 결정 로그(Decision 10) vs Rev 2 DXF의 6볼트/10볼트 충돌 공식 해소 결정.
   - KC 시험기관 앞 `R-C-es5-ESP32WROOM32E` 안테나 승계 질의서 공식 발송 승인.
   - 8Ω 양산 익사이터 T2 부하·발열 실측 시험 프로토콜 승인.
2. **미해결 잔여 실측 항목 (Verification Pending)**:
   - TAS5805M BTL 차동 전압 파형 및 주파수별 실효 전력 실측 데이터 부재 (오실로스코프 고전압 차동 프로브 계측 대기).
   - 450×250mm 4.5T 자작합판의 15kg 하중 시 실제 휨 변위 및 30~65Hz 진동 중 PCB 간극 실측 부재 (CAE 및 다이얼 게이지 계측 대기).
   - 조립 후 4개 스탠드오프 $\leftrightarrow$ PCB GND 도통 연속성($\le 0.1\,\Omega$) 실측.
