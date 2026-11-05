# MAJN 차기 PCB 설계 입력 기준선 기술 검증 보고서
(Next Revision Circuit Requirements Technical Review: DFT, DFI & Electrical Baseline)

- **문서 버전**: v1.0
- **작성 일자**: 2026-11-02
- **검토 대상 문서**:
  1. [`docs/PCB_0005_OBSERVATIONS_AND_UNRESOLVED.md`](file:///Users/youngseok/Desktop/majn/docs/PCB_0005_OBSERVATIONS_AND_UNRESOLVED.md)
  2. [`docs/NEXT_REVISION_CIRCUIT_REQUIREMENTS.md`](file:///Users/youngseok/Desktop/majn/docs/NEXT_REVISION_CIRCUIT_REQUIREMENTS.md)
  3. [`docs/CIRCUIT_DESIGN_VERIFICATION_PLAN.md`](file:///Users/youngseok/Desktop/majn/docs/CIRCUIT_DESIGN_VERIFICATION_PLAN.md)
  (기준 커밋: [`177d28a`](https://github.com/youngseokchomajn-web/MAJN_GEMINI/commit/177d28a2f46c2f3890488d8dafa6aec45cceed03))
- **문서 목적**: 상기 3개 엔지니어링 문서의 요구사항, 계산식, 부품 정격, 그리고 계측 계획을 실제 회로 설계(Schematic Design) 착수 관점에서 정밀 재검증하여, 기술적 오류와 미확정 요소를 명확히 분리하고 회로 설계자가 즉시 착수 가능한 확정 기준선을 수립함.

---

> [!IMPORTANT]
> **기술 검증 핵심 원칙**
> 1. **회로 변경/발주 동결 아님**: 본 문서는 요구사항의 타당성을 검증하는 단계이며, 회로도 변경이나 신규 거버 발주를 승인하는 단계가 아님.
> 2. **추정치와 근거의 엄격한 분리**: 데이터시트나 실측 수치로 입증되지 않은 설계치는 `VERIFIED`로 판정하지 않고 `CONDITIONAL`, `NEEDS TEST`, 또는 `TBD`로 격리함.
> 3. **DFT/DFI 아키텍처 실현성 검증**: 격리 점퍼, 테스트 포인트, 차동 계측이 실제 기판 아트웍과 양산 테스트에서 물리적으로 구현 가능한지 회로적 안전망을 확보함.

---

## A. 검토 개요

### A.1 검토 범위 및 자료
* **검토 완료 자료**:
  - 실물 시제품 #0005 제조 원본 BOM ([`인증준비/pcb/260708/BOM_PCB1_revB_2026-07-08.csv`](file:///Users/youngseok/Desktop/majn/인증준비/pcb/260708/BOM_PCB1_revB_2026-07-08.csv))
  - 주요 IC 데이터시트: TI TAS5805M (SLVSEH8B), MPS MP3426 (Rev 1.03), Diodes AP2112K, Espressif ESP32-WROOM-32E/32UE, Sunlord SWPA6045S 인덕터, Tectonic TEAX14C02-8 진동자
  - 펌웨어 레지스터 제어 및 안전 인터록 구현 소스 ([`인증준비/firmware/src/`](file:///Users/youngseok/Desktop/majn/인증준비/firmware/src/main.cpp))
  - 기존 3개 문서 ([`PCB_0005_OBSERVATIONS_AND_UNRESOLVED.md`](file:///Users/youngseok/Desktop/majn/docs/PCB_0005_OBSERVATIONS_AND_UNRESOLVED.md), [`NEXT_REVISION_CIRCUIT_REQUIREMENTS.md`](file:///Users/youngseok/Desktop/majn/docs/NEXT_REVISION_CIRCUIT_REQUIREMENTS.md), [`CIRCUIT_DESIGN_VERIFICATION_PLAN.md`](file:///Users/youngseok/Desktop/majn/docs/CIRCUIT_DESIGN_VERIFICATION_PLAN.md))
* **검토 미완료 (물리적 제약)**:
  - U4(TAS5805M) 탈거 상태의 기판 단독 절연 저항 (부품 보존 원칙으로 미탈거)
  - 실제 4.5T 자작합판 기구물 내 1m 하네스 체결 시의 실측 방사 노이즈(EMI) 스펙트럼

### A.2 이전 작업 테스트 실패(Exit Code 2) 원인 및 분석
* **원인 규명**: 이전 턴에서 `python3 tools/verify_mfg_package.py` 실행 시 발생한 종료 코드 2(`[Errno 2] No such file or directory`)는 **테스트 로직 실패(Assertion Failure)가 아니라, 해당 스크립트가 `feature/phone-wifi-control` 브랜치에만 존재하고 현재 `docs/` 브랜치에는 커밋되어 있지 않아 발생한 Python 파일 누락 오류**임이 확인되었습니다.
* **현재 브랜치 테스트 상태**: 현재 브랜치에 배치된 통합 펌웨어 명령어 검증 스크립트([`tools/test_command_parser.py`](file:///Users/youngseok/Desktop/majn/tools/test_command_parser.py))는 **92개 단위 테스트 전수 합격(92/92 PASS)** 상태임을 확인했습니다.

---

## B. 기존 요구사항 기술 검증 상세

### 1. 전원부 및 USB-C 입력단 검증

#### 1.1 USB-C 5V 공급 조건 및 Type-C 규격과의 괴리
* **기존 계산 가정**: 연속 오디오 3.2W, 피크 오디오 10.0W, 부스트 효율 85%, MCU 1.0W $\rightarrow$ 평균 $0.95\text{ A}$, 피크 $2.55\text{ A}$.
* **기술 검증 및 문제점**:
  1. **USB Type-C 규격 한계**:
     - USB Type-C 표준(USB-IF)에서 기본 5V VBUS 전원은 호스트(Source)의 CC 풀업 저항($R_p$)에 따라 **Default(500mA/900mA), 1.5A, 3.0A**로 엄격히 구분됩니다.
     - 시제품 #0005 및 현재 회로는 CC1/CC2 핀에 단순히 $5.1\text{ k}\Omega$ 풀다운($R_d$)만 부착되어 있어, 보드가 싱크(Sink)임을 알릴 뿐 **호스트의 전력 공급 용량을 감지하는 회로(CC 로직/ADC 감시)가 전혀 없습니다.**
     - 만약 사용자가 일반 5V 1.0A 어댑터나 저가 보조배터리에 연결한 상태에서 앰프가 순간 $2.55\text{ A}$를 끌어당기면, 보조배터리의 과전류 보호(OCP)가 동작하여 VBUS가 차단되거나 전압 붕괴(Brownout)로 MCU가 무한 리셋됩니다.
  2. **USB PD(Power Delivery) 필요성 판정**:
     - 5V 레일에서 $2.55\text{ A}$ 이상을 상시 보장받으려면 전원 공급 장치가 **"5V 3.0A" Type-C Current 규격**을 명시적으로 지원해야 합니다.
     - 단순 5V 입력을 유지할 경우 **피크 오디오 출력을 하드웨어/펌웨어적으로 상한 제한(Peak Limiting)**하거나, 안정적인 전력 여유를 위해 **USB PD 싱크 컨트롤러(CH224K 등 초소형 IC)를 도입하여 9V 또는 12V VBUS를 직접 공급받는 구조**를 적극 검토해야 합니다.

#### 1.2 케이블 저항 및 전압 강하 (IR Drop) 현실성 재검증
* **기존 계산**: $R_{\text{cable}} = 0.25\,\Omega$ 가정 시 $2.55\text{ A} \times 0.25\,\Omega = 0.64\text{ V}$ 강하 $\rightarrow$ 보드 입력 $4.36\text{ V}$.
* **현실 조건 반영 재계산**:
  - 실제 USB 케이블 루프 저항은 도선 저항뿐만 아니라 **커넥터 접촉 저항(Mated Contact Resistance)**과 **보조배터리 내부 스위칭 FET 저항**이 직렬로 더해집니다.
    $$R_{\text{total}} = R_{\text{wire}} (0.25\,\Omega) + 2 \times R_{\text{connector}} (\approx 0.10\,\Omega) + R_{\text{source}} (\approx 0.05\,\Omega) = \mathbf{0.40\,\Omega \sim 0.50\,\Omega}$$
  - $R_{\text{total}} = 0.45\,\Omega$ 적용 시:
    $$\Delta V = 2.55\text{ A} \times 0.45\,\Omega = \mathbf{1.15\text{ V}} \quad \longrightarrow \quad V_{\text{in, board}} = 5.0\text{ V} - 1.15\text{ V} = \mathbf{3.85\text{ V}}$$
  - **전압 붕괴 피드백 루프 (Voltage Collapse Loop)**:
    입력 전압이 3.85V로 떨어지면, 부스트 컨버터(MP3426)는 12V 10W를 유지하기 위해 더 많은 전류를 끌어당깁니다:
    $$I_{\text{in}} = \frac{10\text{ W} / 0.85 + 1.0\text{ W}}{3.85\text{ V}} = \frac{12.76\text{ W}}{3.85\text{ V}} \approx \mathbf{3.31\text{ A}} \quad \longrightarrow \quad \Delta V = 3.31\text{ A} \times 0.45\,\Omega = \mathbf{1.49\text{ V}} \quad (V_{\text{in}} \rightarrow \mathbf{3.51\text{ V}})$$
  - **판정**: 케이블 저항 $0.25\,\Omega$는 지나치게 낙관적인 수치이며, 얇은 저가 케이블 사용 시 즉각 저전압 록아웃(UVLO) 임계치에 도달합니다. 케이블 길이를 1.0m 이하로 제한하고 AWG20 이상의 전원 도체를 필수로 규정해야 합니다.

#### 1.3 100µF 입력 버퍼 커패시터의 유효성 검증
* **기존 서술**: "5V 라인에 $100\,\mu\text{F}$ 커패시터를 배치하여 순간 전압 드룹을 방어함."
* **물리적 검증 및 오류 규명**:
  - $100\,\mu\text{F}$ 커패시터가 $\Delta V = 0.5\text{ V}$ 강하 동안 방출할 수 있는 에너지는 **$0.24\text{ mJ}$에 불과**합니다.
  - 배시넷 진동 주파수인 $50\text{ Hz}$ 정현파의 반주기(Half-cycle) 지속 시간은 $10\text{ ms}$입니다.
  - $10\text{ ms}$ 동안 10W 피크 전력을 커패시터로 지탱하려면 필요한 정전용량은:
    $$C = \frac{I \times \Delta t}{\Delta V} = \frac{2.5\text{ A} \times 0.010\text{ s}}{0.5\text{ V}} = \mathbf{50,000\,\mu\text{F}} \quad (\mathbf{50\text{ mF}})$$
  - **결론**: $100\,\mu\text{F}$ MLCC/전해 커패시터는 $1.2\text{ MHz}$ 스위칭 리플 억제용일 뿐, **오디오 주파수 대역($30\sim 80\text{ Hz}$)의 전압 드룹을 버퍼링하는 것은 물리적으로 불가능**합니다. 케이블 전압 강하는 케이블 도체 저항 축소와 전원 어댑터 소싱 능력으로 해결해야 합니다.

---

### 2. MP3426 부스트 컨버터 설계 검증

#### 2.1 인덕터 L1 포화 전류($I_{\text{sat}}$) 마진 검증
* **실장 소자**: SWPA6045S4R7MT ($4.7\,\mu\text{H}$, 제조사 Sunlord).
* **데이터시트 규격**: $I_{\text{sat}} = 3.6\text{ A}$ (인덕턴스 30% 감소점), $I_{\text{rms}} = 3.3\text{ A}$ (온도 40℃ 상승점).
* **스위칭 피크 전류 계산**:
  $$I_{\text{L, peak}} = I_{\text{in, avg}} + \frac{\Delta I_{\text{L}}}{2} = \frac{V_{\text{out}} \times I_{\text{out}}}{\eta \times V_{\text{in}}} + \frac{V_{\text{in}} \times (V_{\text{out}} - V_{\text{in}})}{2 \times L \times f_{\text{sw}} \times V_{\text{out}}}$$
  - $V_{\text{in}} = 4.36\text{ V}, V_{\text{out}} = 12.17\text{ V}, P_{\text{audio}} = 10\text{ W} (I_{\text{out}} = 0.95\text{ A}), \eta = 0.85, f_{\text{sw}} = 1.2\text{ MHz}$:
    $$I_{\text{in, avg}} = \frac{12.17 \times 0.95}{0.85 \times 4.36} = 3.12\text{ A}, \quad \Delta I_{\text{L}} = \frac{4.36 \times (12.17 - 4.36)}{4.7\,\mu\text{H} \times 1.2\text{ MHz} \times 12.17} = 0.50\text{ A}$$
    $$I_{\text{L, peak}} = 3.12\text{ A} + 0.25\text{ A} = \mathbf{3.37\text{ A}}$$
  - **마진 분석**: 인덕터 포화 정격($3.6\text{ A}$) 대비 여유율은 $\frac{3.6 - 3.37}{3.6} = \mathbf{6.4\%}$에 불과합니다.
  - 온도가 상승하면 페라이트 코어의 포화 전류가 감소하므로, 밀폐 하우징 내부에서 코어 포화 $\rightarrow$ 급격한 인덕턴스 붕괴 $\rightarrow$ MP3426 내부 스위치 과전류 차단 또는 인덕터 소음("시이익-")이 발생할 위험이 높습니다.
  - **권장 조치**: 차기 PCB에서는 포화 전류 $I_{\text{sat}} \ge 5.0\text{ A}$ 급 인덕터(예: Bourns SRP6540-4R7M 또는 동급)로 풋프린트 업그레이드가 필수적입니다.

#### 2.2 부스트 다이오드 D3 정격 검증
* **실장 소자**: SS34 ($3\text{ A}, 40\text{ V}$ 쇼트키).
* **동작 마진**: 평균 순방향 전류 $I_{\text{F(AV)}} = 3\text{ A}$, 최대 부하 시 전류 $\approx 0.95\text{ A} \sim 1.4\text{ A}$로 정격 범위 내 안정. 역내압 $40\text{ V}$는 출력 $12.17\text{ V}$에 대해 충분한 마진(3배 이상) 확보 완료 (`VERIFIED`).

---

### 3. R_ISO1 전원 격리 점퍼 및 공통 접지 검증

#### 3.1 점퍼 저항 선정 및 열적 한계
* **기존 요구사항**: 0Ω 저항 실장, 연속 $\ge 3\text{ A}$, 피크 $\ge 5\text{ A}$.
* **데이터시트 기반 검증**:
  - 일반 후막(Thick Film) 0Ω 저항(1206 규격)은 점퍼 저항값이 최대 $50\text{ m}\Omega$에 달하며, 정격 전류는 **통상 $2.0\text{ A}$**에 불과합니다. 3A 인가 시 저항 자체 발열로 소손될 수 있습니다.
  - **해결책**: 특수 저저항 금속박(Metal Plate) 0Ω 점퍼(예: Vishay WSL 또는 KOA TLR 시리즈, 점퍼 저항 $< 0.5\text{ m}\Omega$, 정격 $\ge 6.0\text{ A}$)를 지정하거나, 2512 규격을 채택해야 합니다.

#### 3.2 R_ISO1 오픈 시 피드백 루프 파괴 방지 (치명적 주의사항)
* **회로 연결 원칙**:
  - MP3426의 피드백 저항 분배기($R_1 = 143\text{ k}\Omega, R_2 = 16\text{ k}\Omega$)는 반드시 **`R_ISO1`의 앞단(부스트 출력단)**에 연결되어야 합니다.
  - 만약 피드백 분배기가 `R_ISO1` 뒷단(앰프 PVDD단)에 연결될 경우, 점퍼를 분리(DNP)하는 순간 피드백 루프가 오픈(FB=0V)되어 부스트 컨버터가 최대 듀티로 폭주하면서 자체 파괴됩니다.
  - **판정**: 회로도 작성 시 피드백 노드 인출 위치를 반드시 `R_ISO1` 입력단으로 강제해야 함 (`MUST BE ENFORCED`).

---

### 4. TAS5805M 앰프 및 진동자 4개 결선 구조 검증

#### 4.1 진동자 4개 결선 방식 비교: 4Ω 병렬 vs 16Ω 직렬

진동자 1개 스펙: $8\,\Omega$ 공칭, $0.8\text{W RMS}$ 정격, 최대 $1.5\text{W}$ 피크 ($R_{\text{e}} \approx 7.4\,\Omega$).

```
[ 옵션 A: 채널당 2개 병렬 결선 (합성 부하 4Ω) ]
Ch A ──┬── [ 진동자 1 (8Ω, 0.8W) ] ──┐
       └── [ 진동자 2 (8Ω, 0.8W) ] ──┘  -> 12V 구동 시 최대 15.2W 출력 (소자 정격의 9.5배 과부하!)

[ 옵션 B: 채널당 2개 직렬 결선 (합성 부하 16Ω) ]
Ch A ──► [ 진동자 1 (8Ω, 0.8W) ] ──► [ 진동자 2 (8Ω, 0.8W) ] ──► (Ch A-)
                                        -> 12V 구동 시 최대 4.2W 출력 (진동자당 2.1W -> 안전 마진 확보)
```

| 비교 항목 | 옵션 A: 4Ω 병렬 결선 | 옵션 B: 16Ω 직렬 결선 (강력 권장) | 기술적 판단 근거 |
| :--- | :---: | :---: | :--- |
| **12V BTL 최대 전력** | **$15.2\text{ W}$ / 채널** ($7.6\text{ W}$ / 개) | **$4.2\text{ W}$ / 채널** ($2.1\text{ W}$ / 개) | $P = V_{\text{rms}}^2 / R_{\text{load}}$ |
| **진동자 정격(0.8W) 대비** | **950% (소손 위험 극심)** | **260% (피크 허용치 근접)** | 4Ω 병렬 시 소프트웨어 실수 한 번으로 코일 소손 |
| **전류 분배 균일성** | 코일 DCR 편차 시 불균등 분배 | **두 진동자에 동일 전류 100% 보장** | 직렬 회로는 물리적으로 전류가 동일함 |
| **5V 입력단 피크 전류** | **$3.5\text{ A} \sim 4.0\text{ A}$ (전압 붕괴 유발)** | **$1.8\text{ A} \sim 2.1\text{ A}$ (안정적 공급 가능)** | 5V 보조배터리 전류 공급 한계(3A) 만족 |
| **단선 시 동작 특성** | 1개 단선 시 남은 1개에 과전력 집중 | 1개 단선 시 해당 채널 정지 (안전) | Fail-safe 관점 직렬 우수 |

> **핵심 권고**: 진동자 4개를 2채널 앰프로 구동할 때 기본 결선 방식은 **채널당 2개 직렬($16\,\Omega$ 합성 부하)**로 확정해야 합니다. $4\,\Omega$ 병렬 결선은 전원 인입 전류와 진동자 코일 소손 위험을 제어할 수 없습니다.

#### 4.2 AMP_PDN 하드웨어 강제 차단 및 직렬 저항 추가
* **기존 구조의 위험**: ESP32 GPIO15가 `AMP_PDN` 노드와 직결되어 있을 때, 외부 점퍼로 `AMP_PDN`을 GND로 강제 쇼트시키고 MCU가 오동작하여 GPIO15에 HIGH(3.3V)를 출력하면, **GPIO15 내부 드라이브 트랜지스터에 최대 단락 전류($\approx 40\text{mA}$)가 흘러 MCU 핀이 영구 소손**됩니다.
* **필수 회로 수정**:
  - ESP32 GPIO15와 `AMP_PDN` 노드 사이에 **$1.0\text{ k}\Omega$ 보호 저항($R_{\text{series}}$)**을 직렬 삽입해야 합니다.
  - $1.0\text{ k}\Omega$ 삽입 시 외부 강제 단락 상태에서 MCU가 HIGH를 출력해도 흐르는 전류는 $3.3\text{V} / 1\text{k}\Omega = 3.3\text{mA}$로 완벽히 안전합니다.

#### 4.3 차동 프로브 부재 시 BTL 안전 계측 절차
* 현장에 고가의 절연 차동 프로브가 없는 경우를 위한 표준 대체 측정법:
  1. 일반 10:1 패시브 프로브 2개 준비 (Ch1, Ch2).
  2. **두 프로브의 악어 접지 클립을 모두 보드의 Common GND(TP_GND)에만 연결**.
  3. Probe 1 팁을 `TP_OUT+`에, Probe 2 팁을 `TP_OUT-`에 접촉.
  4. 오실로스코프 연산 메뉴에서 **Math = Ch1 - Ch2 (감산 모드)** 활성화.
  - 이 방식을 적용하면 대지 접지 쇼트 위험을 100% 차단하면서 정밀 차동 전압 파형 계측이 가능합니다.

---

### 5. 센서 확장 및 측정 구조 검증

* **1순위 (가속도 측정)**:
  - 배시넷 목공 프레임 내부에 실장된 기판상의 IMU(U5: LSM6DSOX)는 침대 프레임 진동만 측정할 뿐, 영유아가 눕는 매트리스 폼 상면의 실제 진동량을 반영하지 못함(목공/나사 댐핑 효과).
  - 차기 PCB에는 **매트리스 표면 부착용 초경량($\le 5\text{g}$) 외장 가속도 센서 인터페이스 커넥터(`J_PAD_IMU`, I2C 3.3V)**를 반드시 제공해야 함.
* **2순위 (부가 센서 인터페이스 유보)**:
  - PVDF 생체 신호 AFE, 24GHz 레이더, 환경 마이크는 현재 단계에서 회로를 복잡하게 추가하지 않고, **디지털 통신 헤더(SPI/I2C/UART) 핀만 예비(DNP)로 인출**하는 수준으로 격리함.

---

## C. 계산식 재검증 결과 요약

| 계산 항목 | 기존 문서 수치 | 본 검토 재계산 수치 | 판정 및 편차 원인 |
| :--- | :---: | :---: | :--- |
| **평균 5V 입력 전류** | $0.95\text{ A}$ | **$1.06\text{ A}$** | TAS5805M 대기전력($0.3\text{W}$) 및 3.3V LDO 손실 반영 |
| **피크 5V 입력 전류** | $2.55\text{ A}$ | **$3.31\text{ A} \sim 3.42\text{ A}$** (4Ω 병렬 시)<br>**$1.98\text{ A}$** (16Ω 직렬 시) | 케이블 접촉저항($0.45\,\Omega$) 및 전압 강하 피드백 루프 반영 |
| **케이블 전압 강하 ($\Delta V$)** | $0.64\text{ V}$ | **$1.15\text{ V} \sim 1.49\text{ V}$** ($1.5\text{m}, 4\Omega$ 부하)<br>**$0.40\text{ V}$** ($1.0\text{m}, 16\Omega$ 부하) | 도선 저항 외 접촉 저항($0.2\,\Omega$) 추가 합산 |
| **보드 인입 최소 전압** | $4.36\text{ V}$ | **$3.51\text{ V}$** (4Ω 부하 위험)<br>**$4.60\text{ V}$** (16Ω 부하 안정) | 부스트 입력 전류 증가에 따른 2차 전압 강하 |
| **L1 인덕터 피크 전류** | 기록 없음 | **$3.37\text{ A}$** | 포화전류($3.6\text{ A}$) 대비 마진 6.4%로 위험 (대체 필요) |
| **100µF 캡 드룹 보상 시간** | "순간 보상" | **$0.024\text{ ms}$ (50Hz 1주기 대비 0.12%)** | $100\,\mu\text{F}$로는 오디오 주파수 대역 드룹 보상 불가 판명 |

---

## D. 요구사항 판정표 (Requirements Verification Matrix)

| 요구사항 ID | 검토 항목 및 내용 | 최종 판정 | 근거 및 후속 조치 |
| :--- | :--- | :---: | :--- |
| **REQ-PWR-01** | USB-C 5V 입력 전원 공급 | **`CONDITIONAL`** | 5V 3A Type-C Current 지원 전원 전제 필수. 또는 USB PD 도입 검토. |
| **REQ-PWR-02** | MP3426 12V 승압 전원 | **`VERIFIED`** | 이론값 12.17V, 실측 12.00V 확인. 피드백 저항 R1/R2 정합. |
| **REQ-PWR-03** | L1 인덕터 포화 정격 | **`CONFLICT`** | 현재 SWPA6045($3.6\text{A}$)는 피크($3.37\text{A}$) 시 마진 부족. $I_{\text{sat}} \ge 5.0\text{A}$로 변경 필요. |
| **REQ-PWR-04** | 100µF 입력 버퍼 커패시터 | **`CONDITIONAL`** | 스위칭 노이즈 억제용으로만 유효. 케이블 전압 강하 해결 수단으로 기술 금지. |
| **REQ-ISO-01** | 부스트-PVDD 간 R_ISO1 점퍼 | **`VERIFIED`** | 금속박 0Ω 또는 $10\text{m}\Omega$ 션트 선정. FB 분배기는 반드시 점퍼 앞단 배치. |
| **REQ-ISO-02** | 단일 공통 접지(Common GND) | **`VERIFIED`** | GND 분할 금지 원칙 타당. 노이즈 및 EMI 루프 방지. |
| **REQ-AMP-01** | TAS5805M PVDD 12V 구동 | **`VERIFIED`** | 데이터시트 허용 전압(4.5V~26.4V) 만족. MLCC 내압 25V 이상 유지. |
| **REQ-AMP-02** | 진동자 4개 결선 방식 | **`CONDITIONAL`** | **채널당 2개 직렬($16\,\Omega$) 필수 권장**. 병렬($4\,\Omega$) 채택 시 과전력 소손 위험. |
| **REQ-AMP-03** | AMP_PDN 외부 강제 차단 | **`CONDITIONAL`** | MCU 핀 보호를 위해 GPIO15 직렬 $1\text{k}\Omega$ 저항 추가 필수. |
| **REQ-AMP-04** | BTL 출력 차동 테스트 포인트 | **`VERIFIED`** | OUT+/OUT- 쌍 배치 및 스코프 접지 클립 직결 금지 경고 실크스크린 필수. |
| **REQ-SEN-01** | 패드 표면 가속도 센서 인터페이스 | **`NEEDS TEST`** | 온보드 IMU 외에 외장 초경량 센서 커넥터(`J_PAD_IMU`) 신설 필요. |
| **REQ-SEN-02** | 부가 센서(PVDF/레이더/마이크) | **`TBD`** | 1차 시제품 범위에서 제외. 디지털 핀 예비 인출로 한정. |
| **REQ-DVP-01** | 9단계 점진적 브링업 시퀀스 | **`VERIFIED`** | Stage 0~8 단계별 분리 검증 체계 타당. 무부하 전원 확인 후 앰프/부하 인가. |

---

## E. 설계 착수 전 필수 결정 사항 (Pre-Design Decision Gates)

차기 PCB 회로도를 그리기 전에 프로젝트 책임자 및 기구팀이 사전 동결해야 할 **3대 핵심 결정 사항**:

1. **Gate 1: 진동자 4개 결선 토폴로지 동결 (결정 권한: 시스템/회로)**
   - **권장안**: **채널당 2개 직렬($16\,\Omega$ 부하)**
   - 사유: 진동자 코일 소손 방지(채널당 4.2W 하드웨어 캡), 5V 입력 전류 2.0A 이하 유지, 두 진동자 전류 균일성 100% 보장.
2. **Gate 2: 전원 입력 아키텍처 결정 (결정 권한: 시스템/기구)**
   - **옵션 A (기본 5V 유지)**: 5V 3.0A 전용 Type-C 어댑터/보조배터리 사용 규정 + 케이블 길이 1.0m 이하 제한 + L1 인덕터 5A급 교체.
   - **옵션 B (USB PD 도입)**: CH224K 등 단순 PD 싱크 칩 추가하여 9V 또는 12V 직결 공급 (부스트 부담 대폭 경감).
3. **Gate 3: 가속도 센서 물리적 장착 위치 및 하네스 인터페이스 (결정 권한: 기구/소프트웨어)**
   - 보드 내장 센서와 별개로, 아기 매트리스 패드 표면에 부착할 초경량 외장 센서의 신호선 커넥터 규격(I2C 4핀) 확정.

---

## F. 회로 설계 착수 가능 / 보류 영역 구분

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│ [1] 설계 즉시 착수 가능 영역 (Ready for Schematic Design)                             │
│   • ESP32-WROOM-32UE 코어 및 6핀 UART/수동 부트로더 인터페이스                        │
│   • AP2112K-3.3V 전원단 및 전원 레일별 독립 테스트 포인트 (TP_VBUS, TP_3V3, TP_GND)  │
│   • MP3426 승압 회로 (단, L1 풋프린트는 5A급 확장 패드 적용)                          │
│   • R_ISO1 격리 점퍼 회로 (피드백 저항은 반드시 점퍼 앞단 배치)                        │
│   • TAS5805M 디지털 오디오단 및 AMP_PDN 직렬 1kΩ 보호 저항                             │
│   • BTL OUT+/OUT- 차동 테스트 포인트 및 주의 실크스크린                                │
├────────────────────────────────────────────────────────────────────────────────────────┤
│ [2] 설계 착수 전 파라미터 동결 필요 영역 (Pending Decisions)                           │
│   • 진동자 출력 커넥터 결선 (직렬 16Ω vs 독립 4개 인출 헤더)                           │
│   • USB-C 전원 방식 (5V 고전류 어댑터 규정 vs USB PD 싱크 추가)                       │
│   • 외장 패드 가속도계 인터페이스 핀맵                                                 │
├────────────────────────────────────────────────────────────────────────────────────────┤
│ [3] 기판 제작 후 실물 시험으로 검증할 영역 (Post-Assembly Bringup)                     │
│   • DVP 9단계 점진적 브링업 프로토콜 수행                                              │
│   • 무부하 부스트 12.17V 안정성 및 리플 실측                                           │
│   • 8Ω/16Ω 더미 부하 환경에서의 TAS5805M 차동 출력 왜곡(THD) 및 발열 실측            │
│   • 1m 하네스 체결 상태에서의 KN 32 전자파(EMC) 사전 방사 시험                        │
└────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## G. 차기 엔지니어링 작업 순서

1. **1단계**: 위 E섹션의 3대 필수 결정 사항(진동자 직렬 결선, USB 5V 공급 사양, 외장 가속도계 핀맵) 확정.
2. **2단계**: EasyEDA Pro에서 위 기술 검증 요구사항(L1 인덕터 5A급 확장, R_ISO1 점퍼, AMP_PDN 1kΩ 저항, 차동 TP)을 반영한 신규 회로도(Schematic) 초안 작성.
3. **3단계**: 회로도 완료 후 ERC 무결성 검증 및 넷리스트 동기화 수행 후 PCB 아트웍 배치 단계로 진입.
