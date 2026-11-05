# [비교 검토서] TAS5805M PDN 제어 핀 후보 상세 비교 및 전기적 안전성 분석
(Detailed Comparison & Electrical Safety Analysis of TAS5805M PDN Pin Candidates)

- **문서 식별자**: `GPIO_PDN_ALLOCATION_COMPARISON`
- **리비전**: v1.0
- **작성 일자**: 2026-11-05
- **책임 주체**: Antigravity (독립 기술 심사 에이전트)
- **감사 대상**: ESP32-WROOM-32UE-N8 및 TI TAS5805M 오디오 앰프 회로
- **현재 판정**: **CANDIDATE_EVALUATED (확정 배정 보류, Gate G3 승인 대상)**

---

## 1. 개요 및 검토 배경

선행 PCB #0005 설계 및 초기 펌웨어에서 TAS5805M의 전원 제어 핀(Pin 12, `PDN`)은 `GPIO15`에 할당되어 있었습니다. 그러나 `GPIO15`는 ESP32의 부트 스트래핑 핀(`MTDO`)으로, 부팅 시 내부 약한 풀업이 활성화되어 앰프의 외장 풀다운 요구사항과 전기적 충돌(전압 분배에 따른 부트 모드 불안정 및 기동 퍽 노이즈)을 유발하는 치명적 취약점을 안고 있었습니다.

이에 따라 부트 스트래핑 간섭이 없고 안전한 앰프 음소거(Mute) 상태를 보장할 수 있는 대체 GPIO 후보군을 체계적으로 비교·분석합니다.

> [!IMPORTANT]
> **설계 승인 원칙**: 본 문서는 공학적 비교 분석서이며, **특정 핀을 임의로 확정하지 않습니다.** 최종 배정은 Gate G3에서 회로도 수정 및 펌웨어 동기화 ECO가 Human Chief Authority에 의해 승인될 때 확정됩니다.

---

## 2. TAS5805M PDN 핀의 전기적 입력 사양 (Datasheet 기준)

TI TAS5805M 데이터시트(Section 7.3 Electrical Characteristics)에 규정된 PDN(Pin 12)의 전기적 조건은 다음과 같습니다.

| 파라미터 | 기호 | 최소값 | 대표값 | 최대값 | 단위 | 설계 고려사항 |
| :--- | :---: | :---: | :---: | :---: | :---: | :--- |
| **High-level 입력 전압** | $V_{IH}$ | 2.0 | - | DVDD (3.3V) | V | 앰프 정상 동작(Play/Standby) 진입 조건 |
| **Low-level 입력 전압** | $V_{IL}$ | - | - | 0.8 | V | 앰프 완전 셧다운(Shutdown/Mute) 조건 |
| **입력 누설 전류** | $I_{LK}$ | - | - | 1.0 | µA | 초저전류 입력 |
| **권장 외장 풀다운 저항** | $R_{PD,ext}$ | 4.7 | 10 | 47 | kΩ | **MCU 리셋/미초기화/전원 과도기 동안 확실한 0V 접지 유지 필수** |

- **안전 규칙 (Safety Rule)**:
  - 전원 투입(Power-On) 시점부터 ESP32 펌웨어가 I2S 클록을 안정화할 때까지 PDN 전압은 **반드시 $0.8\text{V}$ 이하(이상적으로 $0\text{V}$)**를 유지해야 합니다.
  - 만약 부팅 과도기에 PDN이 $2.0\text{V}$ 이상으로 부유(Float)하면, 앰프 내부 아날로그 바이어스가 불안정하게 켜지며 스피커(엑사이터)에서 **강한 직류 서지 퍽(Pop) 노이즈**가 발생하거나 I2C 버스가 먹통(Lockup) 상태에 빠집니다.

---

## 3. 후보 GPIO 4종 상세 비교 분석

| 평가 항목 | 후보 1: GPIO13 | 후보 2: GPIO16 | 후보 3: GPIO32 | 기존: GPIO15 (비교군) |
| :--- | :--- | :--- | :--- | :--- |
| **ESP32 핀 번호** | **Pin 16** (MTCK) | **Pin 27** (U2RXD) | **Pin 8** (32K_XP) | **Pin 23** (MTDO) |
| **스트래핑 여부** | **아님 (Safe)** | **아님 (Safe)** | **아님 (Safe)** | **STRAPPING PIN (Hazard)** |
| **부팅/리셋 기본 상태** | **내부 약한 풀다운** ($\approx 45\text{k}\Omega$) | High-Impedance (Floating) | 내부 약한 풀다운 ($\approx 45\text{k}\Omega$) | **내부 약한 풀업** ($\approx 45\text{k}\Omega$) |
| **외장 10k 풀다운 병렬 전압** | $0\text{V}$ ($45\text{k}\parallel 10\text{k} \rightarrow \text{GND}$) | $0\text{V}$ ($10\text{k} \rightarrow \text{GND}$) | $0\text{V}$ ($45\text{k}\parallel 10\text{k} \rightarrow \text{GND}$) | **약 0.60V ~ 1.6V (위험 전압 형성)** |
| **JTAG / 주변기기 다중화** | MTCK (JTAG Clock) | UART2_RXD / EMAC | 32kHz XTAL / ADC1_CH4 | MTDO (JTAG / ROM Log Print) |
| **JTAG 디버깅 영향** | 하드웨어 4선 JTAG 디버거 연결 시 동시 사용 불가 | JTAG 영향 없음 | JTAG 영향 없음 | JTAG 영향 및 부트로그 간섭 |
| **WROOM-32UE 내부 연결** | 독립 GPIO (가용) | 독립 GPIO (PSRAM 없음) | 독립 GPIO (가용) | 독립 GPIO |
| **PCB 물리적 배선 경로** | 보드 좌측 (U4 앰프와 최단 거리) | 보드 우측 상단 (원거리 교차) | 보드 좌측 하단 (아날로그 영역) | 보드 우측 중앙 |
| **펌웨어 초기화 실패 시 상태** | **확실한 Shutdown (0V)** | **확실한 Shutdown (0V)** | **확실한 Shutdown (0V)** | 불확정 중간 전압 부유 |
| **종합 적합도 평가** | **1순위 유력 후보** | **2순위 대체 후보** | **3순위 예비 후보** | **부적격 (REJECTED)** |

---

## 4. 후보 1 (GPIO13) 심층 분석

### 4.1 기본 기능 및 JTAG 영향
- **다중화 기능**: GPIO13 / MTCK / Touch4 / ADC2_CH4 / HS2_CLK / SD_DATA2.
- **JTAG 사용성**: MTCK는 표준 IEEE 1149.1 JTAG 클록 핀입니다.
  - MAJN 프로젝트는 양산 및 R&D 펌웨어 플래싱/로그 수집에 **UART0 (GPIO1 TXD0, GPIO3 RXD0)**을 사용하며, JTAG 전용 핀헤더는 실장되어 있지 않습니다.
  - 만약 향후 OpenOCD를 통한 하드웨어 JTAG 디버깅이 요구될 경우, GPIO13을 PDN으로 제어하는 동안에는 JTAG 클록을 사용할 수 없다는 제약이 있습니다. (단, USB-UART 직렬 디버깅 및 FreeRTOS 트레이스는 100% 정상 동작함).

### 4.2 부팅 및 리셋 시 전기적 안전성
- ESP32 리셋 시 GPIO13은 내부 풀다운 저항($R_{PD,int} \approx 45\text{k}\Omega$)이 활성화됩니다.
- 여기에 TAS5805M PDN 핀의 외장 풀다운 저항($R_{PD,ext} = 10\text{k}\Omega$)이 병렬로 연결되면 합성 임피던스는:
  $$R_{eff} = 45\text{k}\Omega \parallel 10\text{k}\Omega = 8.18\text{k}\Omega \quad (\text{to GND})$$
- 어떠한 풀업 소스도 존재하지 않으므로 전원 투입 순간부터 GPIO 초기화 전까지 **PDN 핀 전압은 완벽하게 $0\text{V}$($V_{IL} \le 0.8\text{V}$ 충족)**로 유지됩니다.
- 펌웨어 크래시, 하드웨어 와치독 리셋(WDT), 또는 무한 루프 발생 시에도 GPIO가 리셋 상태로 돌아가면 앰프는 즉각 **안전 셧다운(Hardware Fail-Safe)** 상태로 복귀합니다.

### 4.3 액티브 구동 시 구동 전류
- 펌웨어가 I2S 클록 공급 후 GPIO13을 HIGH(3.3V)로 전환 시:
  $$I_{drive} = \frac{3.3\text{V}}{10\text{k}\Omega} = 0.33\text{mA}$$
- ESP32 GPIO13의 소싱 능력은 최대 $40\text{mA}$(권장 $12\text{mA}$)이므로 $0.33\text{mA}$는 구동 능력의 $2.75\%$에 불과하여 LDO 전력 소모 및 MCU 발열에 영향이 전무합니다.

---

## 5. 후보 2 (GPIO16) 및 후보 3 (GPIO32) 비교 평가

### 5.1 후보 2: GPIO16 (Pin 27)
- **장점**: JTAG과 완전 독립된 순수 GPIO입니다. ESP32-WROOM-32UE는 외장 PSRAM이 내장되지 않은 모델이므로 GPIO16이 완전히 자유롭습니다.
- **단점 (물리적 라우팅)**: Pin 27은 모듈 우측 상단에 위치합니다. 반면 TAS5805M(U4)은 보드 좌측 영역에 실장되어 있으므로, 제어 트랙이 ESP32 모듈 하부 또는 고주파 RF 영역을 가로질러 배선되어야 하므로 EMI 유도 노이즈 위험이 증가합니다.

### 5.2 후보 3: GPIO32 (Pin 8)
- **장점**: 모듈 좌측에 위치하여 TAS5805M과 가깝고 스트래핑 간섭이 없습니다.
- **단점 (아날로그/RTC 간섭)**: GPIO32는 32.768kHz 저전력 크리스탈 연결 핀(`32K_XP`)이자 RTC GPIO입니다. 가속도 센서(U5)의 아날로그 비드 전원 영역과 인접하여 디지털 스위칭 잡음이 센서에 커플링될 가능성이 존재합니다.

---

## 6. 기존 GPIO15의 전기적 충돌 메커니즘 (폐기 사유)

ESP32 공식 기술문서(ESP32 Datasheet Section 2.4 Strapping Pins)에 따르면:
- `GPIO15 (MTDO)`는 부팅 시 **UART0 ROM 디버그 메시지 출력 여부를 결정**하는 스트래핑 핀입니다.
  - MTDO = High (기본값): 부팅 로그 정상 출력.
  - MTDO = Low: 부팅 로그 음소거(Silent Boot).
- 칩 리셋 시 GPIO15 내부에는 **약한 풀업 저항($R_{PU,int} \approx 45\text{k}\Omega$)**이 기본 작동합니다.
- 만약 앰프 셧다운을 위해 외부에 $10\text{k}\Omega$ 풀다운을 연결하면 다음과 같은 전압 분배가 발생합니다:
  $$V_{GPIO15,boot} = 3.3\text{V} \times \frac{10\text{k}\Omega}{45\text{k}\Omega + 10\text{k}\Omega} = 3.3\text{V} \times \frac{10}{55} \approx 0.60\text{V}$$
- $0.60\text{V}$는 ESP32 입력 임계치 상 Low로 인식될 수 있으나, 전원 전압 변동 또는 부품 공차에 의해 중간 논리 레벨(Metastable State)에 머물며 ROM 부트 타임아웃을 유발하거나, 외장 풀다운 값이 커질 경우($22\text{k}\Omega \rightarrow 1.08\text{V}$) TAS5805M의 $V_{IL}$ 최대값($0.8\text{V}$)을 초과하여 앰프가 부분 기동되는 위험을 초래합니다.
- 따라서 **GPIO15를 PDN 제어선으로 유지하는 것은 엄격히 부적격**합니다.

---

## 7. 결론 및 향후 Gate 승인 절차

1. **기술적 우위**:
   - 전기적 안전성, 디폴트 풀다운 특성, 물리적 최단 배선 경로 관점에서 **`GPIO13`이 가장 우수한 최우선 후보(Primary Candidate)**로 검증되었습니다.
   - JTAG 비간섭이 절대적으로 요구될 경우를 대비한 **대체 후보(Alternative Candidate)로는 `GPIO16`**이 대기합니다.
2. **현 상태 유지**:
   - 본 분석 결과는 **"승인 대기 후보"**로 유지하며, 회로도(`Netlist`) 및 펌웨어 코드(`PIN_AMP_PDN 15`)는 일체 변경하지 않습니다.
3. **Gate G3 승인 요건**:
   - Human Chief Authority가 JTAG 미사용 및 GPIO13 배정을 승인하고, 펌웨어와 회로도 동시 갱신 ECO를 발령할 때 최종 반영합니다.
