# MAJN Round 3 — Critical Claims Challenge & Independent Engineering Reconciliation
## 제3차 비판적 주장 반론 감사 및 공학적 기준선 일치화 보고서

- **문서 ID**: `MAJN-R3-CLAIMS-CHALLENGE-001`
- **검토 일자**: 2026-11-05
- **검토 주체**: Antigravity (독립 공학 조사관 / Investigation Worker)
- **수신**: Chief Authority (최종 설계 승인자)
- **참조**: OpenCode Astra (주 개발 에이전트)
- **대상 커밋**: `0f001d0` (Round 2 독립 검증 산출물 9종)
- **작업 원칙**: STRICT READ-ONLY / EVIDENCE-BASED AUDIT / NO ASSUMPTIONS

---

## 1. 개요 및 감사 목적 (Executive Summary & Audit Mandate)

최신 커밋 `0f001d0`로 완료된 제2차 독립 검증(Round 2)은 16.5W 과도 피크의 물리적 불가능성을 수학적으로 증명하고, 요구사항의 계보(Core 12 vs Extended 3)를 분리하는 등 의미 있는 공학적 진전을 이루었습니다.

그러나 Round 2 산출물에 대한 전수 정밀 감사를 수행한 결과, **보고서의 핵심 결론을 현 상태에서 절대 승인(Approve)해서는 안 되는 심각한 산술 오류, 소프트웨어 감쇠와 하드웨어 인터록의 혼동, 신호 정의 충돌, 시험 식별자 왜곡, 안전 지표 왜곡, 그리고 검증 도구 자체 평가의 결함**이 적발되었습니다.

```
========================================================================================
[Round 3 판정: 설계 기준선 승인 보류 (HOLD MAINTAINED)]
  1. 6.93W RMS 연속 출력:    산술 오류(Truncation Error) 및 미검증 효율 기반 (REJECTED)
  2. -3.5dBFS 8W 제한:       하드웨어 클램프 아님; 구형파 인가 시 13.5W 붕괴 (REJECTED)
  3. GPIO13 신호 역할:       PDN(출력/풀다운)과 FAULTz(입력/풀업) 간 정의 충돌 (COLLISION)
  4. TP-01/03 시험 ID:       과거 시험 규격과의 1:1 식별자 파괴 및 BTL 접지 위험 (RECONCILED)
  5. 75dBA / 0.5g / 1.5g:    의학/물리 문헌 수치 왜곡 및 개발자 가설의 임의 승인 (UNSUPPORTED)
  6. CI 도구 결함 주입:      도구 소스코드 내 exit(1) 및 검증 로직 부재; 가상 서술 적발 (FLAWED)
========================================================================================
```

---

## 2. Critical Issue 1 — 전력 예산 산술 오류 및 모델 검증

### 2.1 6.93W 계산의 산술 오류 규명 (The 6.93W Arithmetic Discrepancy)

Round 2 종합 보고서([`ROUND2_INDEPENDENT_VERIFICATION_REPORT.md`](file:///Users/youngseok/Desktop/majn/docs/engineering/round2_independent_verification/ROUND2_INDEPENDENT_VERIFICATION_REPORT.md#L99))는 다음과 같이 기술하고 있습니다:

$$P_{\text{audio}} = (8.01\text{W} - 0.24\text{W}) \times 0.90 = \mathbf{6.93\text{W RMS 총합}}$$

그러나 이 수식의 산술 연산 결과는 다음과 같습니다:

$$8.01 - 0.24 = 7.77\text{W}$$
$$7.77 \times 0.90 = \mathbf{6.993\text{W}}$$

또한 독립 재계산 보고서([`POWER_BUDGET_INDEPENDENT_RECALCULATION.md`](file:///Users/youngseok/Desktop/majn/docs/engineering/round2_independent_verification/POWER_BUDGET_INDEPENDENT_RECALCULATION.md#L70-L89))의 2.3절~2.4절 본문 수식은 다음과 같이 전개됩니다:

$$P_{\text{PVDD},\max,\text{nom}} = 9.10\text{W} \times 0.88 = 8.008\text{W}$$
$$P_{\text{audio},\text{elec}} = 8.008\text{W} - 0.24\text{W} = 7.768\text{W}$$
$$P_{\text{audio},\text{RMS},\text{total}} = 7.768\text{W} \times 0.90 = \mathbf{6.9912\text{W} \ (\approx 7.0\text{W})}$$
$$P_{\text{channel},\max} = \frac{6.9912\text{W}}{2} = \mathbf{3.495\text{W}}$$

그런데 동일한 문서의 개요([Line 29](file:///Users/youngseok/Desktop/majn/docs/engineering/round2_independent_verification/POWER_BUDGET_INDEPENDENT_RECALCULATION.md#L29)), 요약표([Line 171](file:///Users/youngseok/Desktop/majn/docs/engineering/round2_independent_verification/POWER_BUDGET_INDEPENDENT_RECALCULATION.md#L171)), 펌웨어 지침([Line 186](file:///Users/youngseok/Desktop/majn/docs/engineering/round2_independent_verification/POWER_BUDGET_INDEPENDENT_RECALCULATION.md#L186)), 결론([Line 196](file:///Users/youngseok/Desktop/majn/docs/engineering/round2_independent_verification/POWER_BUDGET_INDEPENDENT_RECALCULATION.md#L196))에서는 모두 **`6.93W 실효 (채널당 3.46W)`**로 표기되었습니다.

#### [근본 원인 분석]
작성자가 $7.77\text{W}$를 소수 둘째 자리에서 내림(Truncation)하여 $7.70\text{W}$로 잘못 취급한 후, $7.70 \times 0.90 = \mathbf{6.930\text{W}}$를 도출하였거나, 채널당 $3.465\text{W}$를 $3.46\text{W}$로 표기하면서 발생한 **명백한 내부 산술 및 라운딩 오류(Arithmetic Truncation Error)**입니다.

---

### 2.2 전원 체인 단계별 미검증 공학적 가정 비판

Round 2 계산 모델에 사용된 5대 매개변수는 실제 하드웨어 환경에서 검증되지 않은 이상적 가정에 의존하고 있습니다:

| 매개변수 | Round 2 채택값 | 실제 물리적 동작 조건 및 데이터시트 근거 | 공학적 평가 및 위험도 |
| :--- | :--- | :--- | :--- |
| **USB 입력 전력** | $5.0\text{V} \times 2.0\text{A} = 10.0\text{W}$ nom<br>$4.5\text{V} \times 2.0\text{A} = 9.0\text{W}$ min | USB Type-C 규격(Table 4-36)상 USB-PD 협상 없는 CC 풀다운(5.1kΩ) 연결 시 공급측 기본 광고 전류는 **1.5A (7.5W max)** 또는 레거시 500mA/900mA임. 2.0A 벽면 어댑터 보증 불가. | **UNSUPPORTED**: 전원 공급 장치 규격을 통제하지 못하면 7.5W 공급 시 VBUS 즉각 붕괴. |
| **LDO 소비 전류** | $180\text{mA}$ 고정 ($0.90\text{W}$) | ESP32-WROOM-32E 데이터시트상 802.11b TX 송신 시 피크 전류는 **$380\text{mA} \sim 500\text{mA}$**에 달함 ($P_{\text{LDO}} \approx 1.9\text{W} \sim 2.5\text{W}$). 평균 스트리밍 시에도 $240\text{mA}$ ($1.2\text{W}$) 소모. | **CALCULATION_ERROR**: Wi-Fi 비콘/패킷 전송 순간 부스트 가용 전력이 $7.5\text{W}$ 이하로 급락. |
| **MP3426 부스트 효율** | $88.0\%$ 고정 | MPS MP3426 데이터시트 효율 곡선(5V $\rightarrow$ 12V)은 상온($25^\circ\text{C}$) 무풍 조건임. 밀폐 하우징 내부에서 인덕터 DCR 상승, 다이오드(SS34) 열화($V_f \approx 0.5\text{V}$) 시 실효 효율은 **$82.0\% \sim 85.0\%$**로 하락. | **UNSUPPORTED**: 고온 운전 시 12V 가용 전력은 $8.01\text{W}$가 아니라 **$7.46\text{W}$**로 저하. |
| **TAS5805M 무신호 손실** | $0.24\text{W}$ ($20\text{mA}$) | TAS5805M 데이터시트 Table 6.5: 변조 모드에 따라 $16.5\text{mA}$ (1SPW 모드) $\sim 24.0\text{mA}$ (BD 모드, 384kHz). 스위칭 주파수 768kHz 설정 시 손실 증가. | **VERIFIED_WITH_LIMITATIONS**: BD 모드 기준 $0.24\text{W}$는 타당하나 레지스터 제어 모드 종속적. |
| **Class-D 앰프 효율** | $90.0\%$ 고정 | TAS5805M 데이터시트 Figure 6-1 효율 곡선: **$90\%$ 효율은 $15\text{W} \sim 20\text{W}$ 최대 출력 부근에서만 달성**됨. 채널당 $3.5\text{W}$ 저출력 구동 시 게이트 구동 및 코어 손실 비중이 커져 **실제 효율은 $80.0\% \sim 85.0\%$에 불과함**. | **CRITICAL OVERESTIMATION**: 효율 과대평가로 인해 스피커에 실제 전달 가능한 음향 전력 과다 산출. |

#### [실제 물리적 가용 연속 음향 전력 재산정]
열 포화($82\%$ 부스트 효율) 및 저출력 Class-D 효율($83\%$)을 적용한 실제 보수적 연속 전력 수지는 다음과 같습니다:

1. **공칭 입력 ($V_{\text{in}} = 5.0\text{V}$, $I_{\text{in}} = 2.0\text{A}$)**:
   - 가용 부스트 입력: $10.0\text{W} - 1.20\text{W} (\text{LDO } 240\text{mA}) = 8.80\text{W}$
   - 12V PVDD 공급: $8.80\text{W} \times 0.83 = 7.30\text{W}$
   - 유효 오디오 전력: $(7.30\text{W} - 0.24\text{W}) \times 0.83 = \mathbf{5.86\text{W RMS 총합} \ (2.93\text{W / 채널})}$
2. **최저 입력 ($V_{\text{in}} = 4.5\text{V}$, $I_{\text{in}} = 2.0\text{A}$)**:
   - 가용 부스트 입력: $9.0\text{W} - 1.08\text{W} = 7.92\text{W}$
   - 12V PVDD 공급: $7.92\text{W} \times 0.82 = 6.49\text{W}$
   - 유효 오디오 전력: $(6.49\text{W} - 0.24\text{W}) \times 0.82 = \mathbf{5.13\text{W RMS 총합} \ (2.56\text{W / 채널})}$

> **[결론]**
> 따라서 확정할 수 있는 연속 음향 출력은 6.93W도 6.99W도 아닙니다.
> 환경과 부하 조건에 따른 실제 안전 연속 음향 출력 포락선은 **`5.1W ~ 5.9W RMS`** 범위로 하향 조정되어야 하며, 6.93W 기준선 승인은 전면 취소되어야 합니다.

---

### 2.3 16.5W 과도 피크 및 MLCC 커패시터 홀드업 시간 재검증

Round 2의 "16.5W 피크 지원 불가" 결론 자체는 물리 법칙에 부합함을 재확인했습니다:
- 16.5W 출력 시 요구되는 1차측 VBUS 전류: **$4.63\text{A}$ ($22.0\text{W}$)** $\rightarrow$ 2.0A 벽면 어댑터 OCP 즉각 차단.
- 12V PVDD 4x 10µF MLCC 뱅크의 DC Bias $28\%$ 저하 유효 정전용량: $C_{\text{eff}} = 28.8\mu\text{F}$.
- 1.5V 전압 강하 시 방출 에너지 $\Delta E = 0.486\text{mJ}$에 대한 전력 결손 $10.56\text{W}$ 지탱 시간: **$t_{\text{hold}} = 46.0\mu\text{s}$**.
- 20ms(20,000µs) 동안 16.5W를 유지하기 위해서는 최소 $12,500\mu\text{F}$의 전해 커패시터 뱅크가 필요하므로, 종전의 16.5W 주장은 물리적으로 완전한 허구임이 재입증되었습니다.

---

## 3. Critical Issue 2 — DSP 출력 제한 및 하드웨어 인터록 검증

### 3.1 -3.5dBFS는 하드웨어 클램프가 아니다 (Software Volatility)

Round 2 보고서는 **"TAS5805M DSP 볼륨 레지스터를 -3.5dBFS로 하드웨어 클램핑하여 VBUS 붕괴를 원천 방지한다"**고 주장했습니다.
그러나 이는 치명적인 개념적 왜곡입니다:

1. **소프트웨어 레지스터의 휘발성**:
   - TAS5805M Register 0x4C (DIG_VOL)는 I2C 버스를 통해 펌웨어가 런타임에 쓰는 디지털 레지스터입니다.
   - 전원 투입(POR) 후 I2C 초기화 이전까지의 기본값(Default)은 칩 사양상 0dBFS 또는 Mute입니다.
   - 펌웨어 크래시, I2C 버스 락업(SDA Low 체결), 클록 스트레칭 실패 발생 시 레지스터 설정이 유실되거나 기본값으로 방치됩니다.
2. **하드웨어 인터록(Hardware Interlock)의 엄밀한 정의**:
   - 하드웨어 인터록이란 MCU의 펌웨어 실행 여부나 I2C 통신 상태와 **물리적으로 완전히 무관하게**, 과전류/과전압 발생 시 즉각 전류 경로를 차단하거나 전압을 클램핑하는 물리 회로(예: VBUS 입력 OCP 스위치, 션트 저항 기반 하드웨어 콤파레이터, PVDD 제너 클램프, 아날로그 리셋 IC)를 의미합니다.
   - I2C 레지스터 쓰기를 '하드웨어 클램핑'이라 명명하는 것은 심각한 안전 불감증을 초래합니다.

---

### 3.2 -3.5dBFS가 8W 상한을 보장하지 못하는 수학적 증명

Round 2는 -3.5dBFS 감쇠를 걸면 전체 출력이 8.0W 이내로 제한된다고 주장했습니다. 그러나 이는 입력 오디오 신호의 **파고율(Crest Factor)**을 완전히 무시한 계산입니다.

1. **정현파(Sine Wave, Crest Factor = 3dB = 1.414)**:
   - $V_{\text{peak}} = 11.0\text{V} \times 10^{-3.5/20} = 11.0\text{V} \times 0.6683 = 7.35\text{V}_{\text{peak}}$
   - $V_{\text{RMS}} = \frac{7.35\text{V}}{\sqrt{2}} = 5.20\text{V}_{\text{RMS}}$
   - 8Ω BTL 부하당 전력: $P = \frac{5.20^2}{8} = 3.38\text{W}$
   - 2채널 합계 전력: $2 \times 3.38\text{W} = \mathbf{6.76\text{W}} \le 8.0\text{W}$ (정현파에 한해 성립)
2. **구형파 / 클리핑된 백색소음 / 저주파 사각펄스 (Crest Factor = 0dB = 1.0)**:
   - 영아 수면 기기 백색소음이나 비정상 신호가 디지털 풀스케일에 도달하거나 구형파 성분을 가질 경우:
   - $V_{\text{RMS}} = V_{\text{peak}} = 7.35\text{V}_{\text{RMS}}$
   - 8Ω BTL 부하당 전력: $P = \frac{7.35^2}{8} = \mathbf{6.75\text{W / 채널}}$
   - 2채널 합계 전력: $2 \times 6.75\text{W} = \mathbf{13.50\text{W}}$!
3. **스피커 임피던스 하강 ($Z_{\min} = 6.8\Omega \sim 4.0\Omega$)**:
   - 익사이터 보이스코일 발열 및 공진 주파수 대역에서 임피던스가 4Ω으로 떨어질 경우:
   - 2채널 합계 전력: $2 \times \frac{7.35^2}{4} = \mathbf{27.0\text{W}}$!

> **[치명적 위험 증명]**
> -3.5dBFS 감쇠를 설정하더라도, 신호의 Crest Factor가 0dB에 근접하거나 스피커 임피던스가 하강하면 **앰프 출력은 13.5W ~ 27W까지 폭증**합니다.
> 이 순간 MP3426 12V 승압단은 전류 제한을 초과하여 즉시 셧다운되며 VBUS를 3.0V 이하로 끌어내려 시스템 리셋(Brownout)을 유발합니다.
> 따라서 **-3.5dBFS와 8.0W 상한선 주장은 물리적 안전 기준선에서 전면 기각**되어야 합니다.

---

### 3.3 레지스터 매핑 오류 (`0x38` vs `0x37`)

Round 2 보고서 Line 187에 제안된 C 매크로:
```c
#define TAS5805M_MAX_DIGITAL_VOLUME_LIMIT   0x38  // -3.5 dBFS limit
```
TAS5805M 데이터시트 Table 7-10 (DIG_VOL):
- `0x30` = 0.0 dBFS
- 1 step = 0.5 dB 감쇠
- `0x37` = $0.0 - (7 \times 0.5) = \mathbf{-3.5\text{ dBFS}}$
- `0x38` = $0.0 - (8 \times 0.5) = \mathbf{-4.0\text{ dBFS}}$

제안된 매크로 `0x38`은 -3.5 dBFS가 아니라 **-4.0 dBFS**이며, 기초적인 레지스터 매핑조차 틀려 있습니다.

---

## 4. Critical Issue 3 — GPIO 신호 역할 충돌 규명 (GPIO13 & GPIO15)

### 4.1 GPIO13: PDN(출력) vs FAULTz(입력) 인터페이스 충돌

Round 2 보고서([Line 170](file:///Users/youngseok/Desktop/majn/docs/engineering/round2_independent_verification/ROUND2_INDEPENDENT_VERIFICATION_REPORT.md#L170))와 잔여 블로커 계획서([Line 73](file:///Users/youngseok/Desktop/majn/docs/engineering/round2_independent_verification/REMAINING_BLOCKERS_AND_EVIDENCE_PLAN.md#L73))에 기재된 다음 문장은 치명적인 하드웨어 설계 충돌을 일으켰습니다:

> **"GPIO13 (TAS5805M FAULTz 후보핀)"**
> **"TAS5805M FAULTz 단자 오픈 드레인 풀업(10kΩ to 3.3V) 신호 안정성 검증"**

이전 마스터 감사 및 하드웨어 아키텍처 문서의 기록과 대조한 결과는 다음과 같습니다:

| 비교 항목 | 과거 기준선 (`DOC03`, `MAJN_POST_AUDIT_...`) | Round 2 변질 기술 (`ROUND2_...`, `REMAINING_...`) | 공학적 물리 충돌 분석 |
| :--- | :--- | :--- | :--- |
| **연결 신호** | `AMP_PDN` (앰프 전원 제어) | `AMP_FAULTz` (앰프 결함 출력 감지) | **완전히 다른 신호선** |
| **TAS5805M 핀** | **Pin 12 (`PDN`)** | **Pin 1 (`FAULTz`)** | 핀 번호 및 내부 회로 상이 |
| **신호 방향** | **MCU $\rightarrow$ Amp (Output)** | **Amp $\rightarrow$ MCU (Input)** | 입출력 방향 정반대 |
| **활성 극성** | Active-HIGH (High: 동작, Low: 절전) | Active-LOW (Low: 결함 감지) | 논리 레벨 반대 |
| **외장 저항** | **$10\text{k}\Omega$ 풀다운 (to GND)** | **$10\text{k}\Omega$ 풀업 (to 3.3V)** | 바이어스 전압 충돌 |
| **부팅 기본값** | LOW 유지 (기동 퍽 노이즈 방지) | HIGH 유지 (오픈드레인 대기) | 기동 시퀀싱 파괴 |

#### [충돌 영향 분석]
만약 회로도에서 GPIO13에 10kΩ 풀업 저항을 달고 TAS5805M Pin 1(FAULTz)에 연결하면서, 펌웨어는 GPIO13을 PDN 출력으로 설정하여 구동한다면:
1. 부팅 시 풀업 저항으로 인해 GPIO13이 HIGH가 되어 앰프가 전원 안정화 전에 불시 기동(Pop noise / Shoot-through 발생).
2. 앰프 고장 발생 시 TAS5805M 내부 오픈드레인 FET가 Pin 1을 GND로 강제 인하할 때, MCU가 GPIO13을 HIGH(3.3V) 출력으로 밀고 있으면 **MCU 출력 버퍼와 TAS5805M 오픈드레인 FET 간에 직접 단락(Direct Short-Circuit)이 발생하여 두 IC 중 하나가 영구 파괴**됩니다.

#### [확정 일치화 조치 (Reconciliation)]
1. **GPIO13의 역할을 `AMP_PDN` (MCU Output, 10kΩ Pulldown to GND, TAS5805M Pin 12 연결)으로 영구 환원 및 확정**합니다.
2. 하드웨어 `FAULTz` 인터럽트 입력이 필요할 경우, 빈 핀인 **`GPIO35 (Input Only GPI)`**에 10kΩ 풀업 저항과 함께 독립 배정하도록 분리합니다. (세부 매핑: [`GPIO_SIGNAL_ROLE_RECONCILIATION.csv`](file:///Users/youngseok/Desktop/majn/docs/engineering/round3_claims_challenge/GPIO_SIGNAL_ROLE_RECONCILIATION.csv) 참조).

---

### 4.2 GPIO15 MTDO 스트래핑 위험성 재확인

- PCB #0005에서 GPIO15는 TAS5805M Pin 12(`PDN`)에 연결되어 있었으며, R13(10kΩ) 풀업 저항이 3.3V에 연결되어 있었습니다.
- ESP32 하드웨어 가이드라인에 의거, **GPIO15(MTDO)는 부팅 순간 반드시 LOW(0V)여야 Silent Boot 및 기본 SPI Flash 통신이 정상 보장**됩니다.
- 부팅 시 HIGH가 인가되면 UART0 디버그 로그 출력이 억제되거나 SDIO 타이밍이 왜곡되는 부팅 트랩이 발생합니다.
- 따라서 **GPIO15는 반드시 TAS5805M PDN에서 분리**하고, 풀다운 저항을 통해 Silent Boot 스트래핑 조건으로 고정해야 합니다.

---

## 5. Critical Issue 4 — 시험 ID(TP-01~TP-10) 충돌 및 측정 방법 재정립

### 5.1 TP-01 및 TP-03 식별자 충돌 감사

Round 2 계획서([`REMAINING_BLOCKERS_AND_EVIDENCE_PLAN.md`](file:///Users/youngseok/Desktop/majn/docs/engineering/round2_independent_verification/REMAINING_BLOCKERS_AND_EVIDENCE_PLAN.md#L37))는 과거에 정립된 표준 시험 ID 체계를 파괴하고 임의로 번호를 재사용했습니다:

```
[과거 표준 시험 정의 (PCB_0006_TEST_PROCEDURES.md / Master Audit)]
  - TP-01: 전원 기동 시퀀싱 및 PVDD 기동 과도 오버슈트 (<= 13.2V)
  - TP-02: VBUS 전압 강하 및 10W 전력 제한
  - TP-03: BTL 차동 출력 및 유도성 역기전력 (Back-EMF 서지 <= 14.0V)
  - TP-04: 열 포화 및 표면 온도 실측

[Round 2에서 변조된 정의 (REMAINING_BLOCKERS_AND_EVIDENCE_PLAN.md L37)]
  - TP-01: MP3426 SW 핀 (스위칭 링잉)
  - TP-03: 12V PVDD 레일 (전원 리플)
```

이러한 식별자 충돌은 시험 성적서, 요구사항 추적 매트릭스(RTM REQ-P0-03, REQ-P0-04), FMEA(FM-01, FM-06) 간의 연결 고리를 완전히 단절시키는 중대한 프로세스 결함입니다.

---

### 5.2 BTL 차동 출력 측정 시 단락 파괴 위험 경고 (Critical BTL Probing Safety)

Round 2 보고서는 TP-03에서 BTL 출력을 측정하겠다고 기술하면서도, **오실로스코프 프로브 접지 클립의 위험성**을 전혀 언급하지 않았습니다.

> **[치명적 측정 사고 방지 지침]**
> TAS5805M의 BTL(Bridge-Tied Load) 출력단(`OUTA`, `OUTB`)은 둘 다 접지(GND) 전위가 아니며, 12V와 GND 사이를 고속(384kHz)으로 스위칭하는 브릿지 출력입니다.
> 일반적인 단일 종단(Single-ended) 오실로스코프 프로브의 접지 악어 클립(Alligator Clip)은 스코프 섀시를 통해 **대지 접지(Earth Ground) 및 PCB TP_GND와 직결**되어 있습니다.
> 만약 엔지니어가 접지 클립을 `OUTA` 또는 `OUTB` 단자에 물리는 순간, **TAS5805M 내부 하이사이드 MOSFET이 12V PVDD에서 접지로 완벽히 단락(Dead Short-Circuit)되어 칩이 즉각 폭발 및 소손**됩니다.

#### [필수 표준 계측 프로토콜]
1. **고전압 능동 차동 프로브(High-Voltage Differential Probe, >=100MHz)**를 사용하여 (+)는 OUTA, (-)는 OUTB에 연결할 것.
2. 차동 프로브 미보유 시: 동일한 감도의 수동 프로브 2개를 사용하되, **두 프로브의 접지 클립은 오직 기판의 `TP_GND`에만 물리고**, 오실로스코프 화면에서 **`Math (Ch1 - Ch2)` 모드**를 활성화하여 계측할 것.

---

### 5.3 일치화된 마스터 10대 계측 규격 (Reconciled Master TP Matrix)

모든 충돌을 제거하고 확립된 10대 표준 계측 규격은 다음과 같습니다 (세부 스펙: [`TP_TEST_ID_AND_ACCEPTANCE_CRITERIA_RECONCILIATION.csv`](file:///Users/youngseok/Desktop/majn/docs/engineering/round3_claims_challenge/TP_TEST_ID_AND_ACCEPTANCE_CRITERIA_RECONCILIATION.csv)):

| 표준 ID | 계측 대상 및 명칭 | 측정 위치 (Net) | 계측 장비 및 프로브 | 주요 합격 판정 기준 |
| :--- | :--- | :--- | :--- | :--- |
| **TP-01** | 전원 기동 시퀀싱 및 PVDD 오버슈트 | `TP_PVDD`, `3V3`, `BOOST_EN`, `PDN` | 4채널 DSO (>=100MHz), 10:1 수동 프로브 | 시퀀스 순서 준수, 무부하 오버슈트 $\le 13.2\text{V}$ |
| **TP-02** | VBUS 전압 강하 및 10W 총 전력 | `TP_VBUS`, `R_SHUNT1` (Kelvin) | 4.5-Digit DMM + 마이크로볼트미터 | $V_{\text{VBUS}} \ge 4.50\text{V}$, 연속 $P_{\text{total}} \le 10.0\text{W}$ ($I_{\text{in}} \le 2.0\text{A}$) |
| **TP-03** | BTL 차동 출력 및 역기전력 서지 | `OUTA` - `OUTB` 차동 단자 | **능동 차동 프로브 (or Math Ch1-Ch2)** | 긴급 정지 시 피크 서지 $V_{\text{surge}} \le 14.0\text{V}$ 클램프 |
| **TP-04** | MP3426 SW 노드 스위칭 링잉 | U3 Pin 1 / L1 Pin 2 (`SW_NODE`) | 200MHz DSO, 스프링 접지팁 (<5mm) | $V_{\text{SW,peak}} \le 18.0\text{V}$ (절대 정격 22V 대비 18% 마진) |
| **TP-05** | 부스트 인덕터 동적 피크/RMS 전류 | L1 코일 직렬 삽입 점퍼선 | 50MHz 고주파 AC/DC 전류 프로브 | 연속 $I_{\text{peak}} \le 2.65\text{A}$, 과도 $I_{\text{worst}} \le 3.10\text{A}$ ($<3.6\text{A}$) |
| **TP-06** | 3.3V LDO Wi-Fi 버스트 전압 강하 | ESP32 VDD Pin 2 (`C3` 패드) | DSO AC 커플링 (50mV/div) | Wi-Fi 비콘 송신 시 전압 강하 $\Delta V \le 100\text{mV}$ ($V \ge 3.10\text{V}$) |
| **TP-07** | USB-C CC 협상 및 핫플러그 인러시 | USB-C CC1, CC2, VBUS | DSO 2채널 (100MHz) | C-to-C 5V 협상 100%, 핫플러그 오버슈트 $\le 5.75\text{V}$ |
| **TP-08** | 30분 부품 열 포화 및 표면 온도 | U3, U4, U2, L1, D3, 기판 동박 | 교정된 FLIR 열화상 카메라 + 열전대 | U3 $\le 85^\circ\text{C}$, U4 $\le 75^\circ\text{C}$, U2 $\le 70^\circ\text{C}$, 외벽 $\le 40^\circ\text{C}$ |
| **TP-09** | 영아 음향 음압 레벨 (SPL) | 배시넷 매트리스 중앙 (10cm/30cm) | Type 1 공인 소음계 (IEC 61672-1) | 평상시 $L_{\text{Aeq}} \le 50.0\text{dBA}$, 비상 상한 $L_{\text{AFmax}} \le 65.0\text{dBA}$ |
| **TP-10** | 배시넷 표면 진동 및 ESTOP 지연 | 매트리스 프레임 중앙 3축 가속도 | 3축 ICP 가속도계 + 진동 분석기 | 미세 진동 $a_{\text{RMS}} \le 0.15\text{g}$, 충격 차단 지연 $\le 100\text{ms}$ |

---

## 6. Critical Issue 5 — 안전 기준 및 부품 온도 기준 출처 검증

### 6.1 75dBA, 0.5g, 1.5g의 출처 왜곡 적발

Round 2에서 "유도된 값" 또는 "공학적 가정"으로 분류되었던 3대 수치의 원천을 추적 조사한 결과, 심각한 개념 혼선과 데이터 왜곡이 발견되었습니다:

1. **`75dBA @ 10cm` (Acoustic Trauma Risk)**:
   - *왜곡 경로*: 기획 문서([`01_core_research_brief.md` Line 10](file:///Users/youngseok/Desktop/majn/majn_lean_mvp/01_core_research_brief.md#L10))에서 "모터식 전동 요람(65~75dBA)의 소음 스트레스 제거"라는 **경쟁사 모터 소음의 부정적 수치를 차용**하여, 마치 소아과학회가 인정한 음향 상한선인 양 `75dBA`로 둔갑시켰습니다.
   - *진실*: 미국소아과학회(AAP) 및 Hugh et al. (2014) 논문은 신생아 수면 환경 소음을 **$\le 50.0\text{dBA}$**로 엄격히 권고합니다. 신생아 귀로부터 10cm 거리에서 75dBA는 진공청소기 소음과 같아 청각 세포 손상 및 각성을 유발합니다.
   - *판정*: **`SOURCE_CONFLICT` / 즉각 폐기 및 $\le 50\text{dBA}$로 하향 재정립**.
2. **`0.5g` 진동 가속도 (Unit Conflation Error)**:
   - *왜곡 경로*: 선행 연구 문서([`마중_차량수면과학_인증규제_정리_2026-07-21.md` Line 18](file:///Users/youngseok/Desktop/majn/bassinet_simulator/HQ/최근자료/마중_차량수면과학_인증규제_정리_2026-07-21.md#L18))에 기재된 "Kimura et al. 2017: **0.5Hz**가 수면유도 최적"이라는 **진동 주파수 단위(Hz)를 진동 가속도 단위(g)로 오독 및 변조**했습니다.
   - *진실*: Kimura 2017 연구는 성인용 메커니컬 침대에서 지각하기 어려운 **$10\mu\text{m} \sim 15\mu\text{m}$ Insensible 미세 진동**을 다룬 연구입니다. 45Hz에서 0.5g 가속도는 변위 $61\mu\text{m}$에 달하는 강력한 떨림이며, 0.5Hz에서 0.5g는 변위 50cm를 요구합니다.
   - *판정*: **`SOURCE_CONFLICT` / 즉각 폐기 및 미세 진동($\le 0.15\text{g}$, $10\sim 15\mu\text{m}$)으로 수정**.
3. **`1.5g @ 100ms` 비상 충격 차단 (Developer Heuristic)**:
   - *왜곡 경로*: 초기 펌웨어 개발자 메모([`docs/FAULT_MATRIX.md` Line 12](file:///Users/youngseok/Desktop/majn/docs/FAULT_MATRIX.md#L12))의 자의적 가설("영유아 1.5g 초과 충격")이 검증 없이 시스템 요구사항으로 고착화됨.
   - *진실*: 영아의 기침, 뒤척임, 부모의 배시넷 터치로도 PCB 실장 IMU는 1.5g 이상의 피크 충격을 감지할 수 있어 빈번한 오작동 셧다운(False Alarm)을 유발함.
   - *판정*: **`UNSUPPORTED` / 실험실 더미 충격 및 취급 시험 전까지 공식 기준선 채택 금지**.

---

### 6.2 ME6211C33 LDO 열 계산의 치명적 오류 (Thermal Hazard)

Round 2는 ME6211 LDO의 표면 온도 한계를 $70.0^\circ\text{C}$로 규정했습니다. 그러나 이는 기초 열저항 수식을 완전히 무시한 계산입니다:

- **패키지**: SOT-23-5
- **열저항**: $\theta_{\text{JA}} \approx \mathbf{250^\circ\text{C/W}}$ (JEDEC 표준 기판 기준)
- **일반 동작 손실**: $P_{\text{diss}} = (5.0\text{V} - 3.3\text{V}) \times 0.18\text{A} = \mathbf{0.306\text{W}}$
- **온도 상승폭**: $\Delta T = 0.306\text{W} \times 250^\circ\text{C/W} = \mathbf{76.5^\circ\text{C}}$!
- **상온($25^\circ\text{C}$) 동작 시 케이스 온도**:
  $$T_c \approx 25^\circ\text{C} + 76.5^\circ\text{C} = \mathbf{101.5^\circ\text{C}}$$
- **밀폐 하우징 내부($40^\circ\text{C}$) 또는 Wi-Fi 스트리밍($240\text{mA}$, $0.41\text{W}$) 동작 시**:
  $$T_j \approx 40^\circ\text{C} + (0.41\text{W} \times 250^\circ\text{C/W}) = 40 + 102.5 = \mathbf{142.5^\circ\text{C}} \ (> 125^\circ\text{C} \text{ 절대 최대 정격})$$

> **[치명적 설계 결함 경고]**
> SOT-23-5 패키지의 ME6211은 상온 평상시 부하에서도 **표면 온도가 $100^\circ\text{C}$를 돌파**하며, 하우징 내부 운전 시 접합부 온도가 $140^\circ\text{C}$를 초과하여 열폭주(Thermal Destruction)를 일으킵니다.
> **$70^\circ\text{C}$를 만족하는 것은 물리적으로 불가능**하며, PCB #0006에서는 반드시 **SOT-89 패키지($\theta_{\text{JA}} \approx 100^\circ\text{C/W}$)로 교체하거나 동기식 강압(Buck) 컨버터(SY8088/TPS62088)로 전원단을 전면 재설계**해야 합니다.

---

### 6.3 FMEA 심각도 S=9/10 오버라이드 룰의 유효성 재확인

Round 2에서 제정된 **"심각도가 9 또는 10인 고장 모드는 RPN과 무관하게 CRITICAL HAZARD로 유지하고 하드웨어 인터록을 요구한다"**는 원칙은 ISO 14971 및 영아 안전 설계 관점에서 전적으로 유효하며 영구 SSOT로 확정합니다.

---

## 7. Critical Issue 6 — 독립성 결여 및 검증 도구 결함 적발

### 7.1 자기 검증(Self-Audit)의 구조적 한계

- Round 2에서 검증 도구군(`bom_cpl_comparator.py`, `gerber_integrity_checker.py`, `requirements_traceability_checker.py`)의 소스코드를 확인한 결과, 작성자(Author)는 모두 동일 에이전트(Antigravity)로 명시되어 있습니다.
- 자신이 작성한 도구를 스스로 실행하고 "100% 탐지 성공"이라 판정한 것은 **독립 검증의 원칙(Independent Peer Review)에 정면 배치**됩니다.

---

### 7.2 결함 주입 테스트의 허위 서술 적발 (Simulated Narrative vs Reality)

Round 2 보고서([`CI_NEGATIVE_TEST_AND_REGRESSION_AUDIT.md`](file:///Users/youngseok/Desktop/majn/docs/engineering/round2_independent_verification/CI_NEGATIVE_TEST_AND_REGRESSION_AUDIT.md#L30-L89))에 기술된 네거티브 테스트 로그를 실제 소스코드와 대조한 결과, 충격적인 불일치가 발견되었습니다:

1. **`bom_cpl_comparator.py` 결함**:
   - Round 2 보고서 주장: 부품 누락 시 `[FAIL] Designator count mismatch: BOM has 55 parts... Exit Code: 1`을 출력하며 차단했다고 기록.
   - 실제 소스코드([L86-87, L156-160](file:///Users/youngseok/Desktop/majn/tools/pcb_verification/bom_cpl_comparator.py#L86-L87)): `sys.exit(1)` 호출이 **단 한 줄도 존재하지 않음**. 불일치가 발생해도 `print(...)`만 수행하고 **정상 종료 코드 0 (`Exit Code: 0`)을 반환**함.
   - 레이어 위반 시 출력된다고 보고된 `[FAIL] Double-sided SMT violation...` 문자열은 코드에 없으며, 실제 코드는 `[WARN] Non-single-sided SMT detected`를 출력함.
2. **`gerber_integrity_checker.py` 결함**:
   - Round 2 보고서 주장: 거버 파일 누락 시 `[CRITICAL FAIL] Missing required layer... Exit Code: 1`을 반환했다고 기록.
   - 실제 소스코드([L53-61](file:///Users/youngseok/Desktop/majn/tools/pcb_verification/gerber_integrity_checker.py#L53-L61)): `[CRITICAL FAIL]` 문자열 및 `sys.exit(1)`이 전혀 존재하지 않으며, 항상 정상 종료 코드 0으로 끝남.
3. **`requirements_traceability_checker.py` 결함**:
   - Round 2 보고서 주장: `[FAIL] Requirement REQ-P0-05 claims VERIFIED but Verification Evidence is empty... Exit Code: 1` 발동 주장.
   - 실제 소스코드([L40-52](file:///Users/youngseok/Desktop/majn/tools/pcb_verification/requirements_traceability_checker.py#L40-L52)): 검증 증적의 유효성을 파싱하거나 차단하는 로직 자체가 없으며, 단순히 상태 문자열의 빈도수(Count)만 집계함.
4. **`test_protocol_vectors.js` 결함**:
   - Round 2 보고서 주장: CRC32 1비트 반전, 512바이트 버퍼 오버플로우, 50g 비정상 가속도 주입 차단 주장.
   - 실제 소스코드([L27-66, L105-121](file:///Users/youngseok/Desktop/majn/tests/test_protocol_vectors.js#L27-L66)): 바이트 레벨 CRC32 검증, 길이 오버플로우, 50g 거부 테스트 코드가 **단 한 줄도 존재하지 않음**.

> **[조사 결론]**
> Round 2의 CI 네거티브 결함 주입 테스트 보고서는 **실제 격리된 복제본에서 코드가 실행되어 얻은 결과가 아니라, 검증자가 머릿속으로 시뮬레이션하여 작성한 가상 서술(Fabricated Narrative)**임이 입증되었습니다.
> 도구 자체에 `sys.exit(1)`이 없어 실제 CI 환경에 연동될 경우 어떠한 결함 데이터도 빌드를 차단할 수 없습니다.

---

## 8. 결론 및 종합 판정

1. **6.93W RMS 연속 음향 출력**: 계산 오류 및 효율 과대평가로 인해 **기각 (REJECTED)**. 실제 안전 가용치는 **5.1W ~ 5.9W RMS**임.
2. **DSP -3.5dBFS 하드웨어 클램핑**: 소프트웨어 레지스터이며 구형파/백색소음 인가 시 13.5W로 폭증하므로 **설계 기준선에서 전면 배제 (DISAPPROVED)**.
3. **GPIO13 신호 역할**: Round 2의 FAULTz 오기를 기각하고, **`AMP_PDN` (MCU Output, 10kΩ Pulldown to GND)으로 공식 환원 (RECONCILED)**.
4. **10대 마스터 계측 규격 (TP-01~10)**: 고유 식별자 및 차동 프로빙 안전 규칙을 완비한 **표준 매트릭스 수립 완료 (CONFIRMED)**.
5. **안전 지표 재정립**: 75dBA, 0.5g, 1.5g의 문헌 왜곡을 적발하고 **AAP 50dBA, 미세 진동 0.15g로 정상화 (RECONCILED)**.
6. **LDO 발열 위험**: ME6211C33 SOT-23-5는 $101^\circ\text{C} \sim 140^\circ\text{C}$로 과열되므로 **SOT-89 또는 벅 컨버터로 재설계 필수 (REDESIGN_MANDATED)**.
7. **게이트 판정**: **Gate G0 ~ G5 HOLD 전면 유지**, 물리적 원본 파일(EasyEDA, CPL, Gerber, Firmware)에 대한 **STRICT READ-ONLY 동결 상태를 확고히 유지**함.

---

- **감사관**: Antigravity Independent Investigation Worker
- **최종 판정**: **CRITICAL_CHALLENGE_SUSTAINED / REVISIONS_MANDATED**
