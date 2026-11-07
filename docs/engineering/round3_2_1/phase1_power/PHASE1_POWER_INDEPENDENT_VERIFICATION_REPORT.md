# MAJN PCB #0006 엔지니어링 1단계(Phase 1 Power) 전원부 독립 검증 종합 보고서
## MP3426 승압 컨버터 스위칭 주파수, L1 파워 인덕터 열·포화 해석, PVDD MLCC DC Bias 및 리플 정밀 재검증

- **문서 식별자**: `MAJN-DOC-P1-POWER-001`
- **리비전**: v1.1 (Chief Authority 1차 검토 반영 및 결함 보정판)
- **수행 주체**: Antigravity (독립 기술 검토자 / Independent Technical Reviewer)
- **최종 승인 권한자**: Chief Authority (Human Final Design & ECO Approval Authority)
- **인가 근거**: `MAJN PCB #0006 — PHASE 0 CONDITIONAL CLOSE & PHASE 1 AUTHORIZATION`
- **기준 Git 브랜치**: `docs/cad-cae-automation-phase1-assessment`
- **수행 일자**: 2026-11-07
- **수행 모드**: **STRICTLY READ-ONLY INDEPENDENT VERIFICATION (Gate G2~G5 STRICT HOLD 유지)**
- **Phase 1 현 상태**: **`HOLD (종료 승인 보류)`**

---

## 1. 개요 및 1단계 착수 배경

Chief Authority의 최종 결정에 따라 Phase 0(기준선 복원 및 산출물 감사)이 조건부 종료 승인된 후, **Phase 1(전원부 독립 검증)**에 착수하였습니다.
이후 제출된 Phase 1 초안에 대해 Chief Authority께서 제시하신 엄격한 검토 결과(D-01 근거 확인 필요, D-02 열·포화 모델 미확인, D-03 $C_{\text{eff}}$ 산술 불일치, Bleeder 과전압 억제 입증 부족, 단위 오류, 결함 주입 테스트 미비)를 전적으로 수용하여, 본 리비전 v1.1에서는 모든 지적 사항에 대한 정밀 재검증과 투명한 데이터 복원을 완료하였습니다.

본 보고서에서 준수한 핵심 엔지니어링 원칙:
1. **확인된 사실(Fact)과 공학적 가정(Assumption)의 엄격한 분리**: 데이터시트 공식 규격과 엔지니어링 추정 모델을 명확히 구분하여 표기함.
2. **$C_{\text{eff}}$ 감쇄 전과정의 10단계 완전 공개**: 초기 용량 공차, DC 바이어스, 온도, 노화의 복합 감쇄 과정을 투명하게 공개하여 산술 불일치 의혹을 근본적으로 해소함.
3. **물리 단위 및 품번 엄격성 준수**: 커패시터 정전용량 단위 오기($\mu\text{H} \to \mu\text{F}$)를 전면 수정하고 부품 LCSC C-ID를 100% 매핑함.
4. **엄격한 작업 가드레일 유지**: 회로도 CAD(`.epro2`, `.json`, `.sch`, `.pcb`), 레이아웃 배선, BOM, 펌웨어 소스코드를 일절 수정하지 않으며, Gate G2~G5는 `STRICT HOLD` 상태로 유지함.
5. **결함 주입 회귀 테스트 11종 완비**: 7대 결함 주입 테스트(FI-01 ~ FI-07)를 포함한 11개 회귀 테스트를 구축하고, **Exit Code 0**을 달성함.

---

## 2. MP3426 스위칭 주파수 정밀 재검증 (결정 D-01)

### 2.1 공식 데이터시트 Table 1 및 주기 선형 보간 모델링
MPS 공식 데이터시트(Rev 1.01)에 따르면, MP3426의 스위칭 주파수($f_{\text{sw}}$)는 FSET 핀 저항($R_{\text{FSET}}$)에 따른 설계 기준표(Table 1)를 통해 규정됩니다.

```
[MPS MP3426 Datasheet Table 1: Switching Frequency vs. FSET Resistor Values]
  R_FSET = 180.0 kΩ  ->  f_sw = 0.26 MHz (260 kHz)
  R_FSET = 160.0 kΩ  ->  f_sw = 0.29 MHz (290 kHz)
  R_FSET = 150.0 kΩ  ->  f_sw = 0.31 MHz (310 kHz)
  R_FSET = 143.0 kΩ  ->  f_sw = 0.32 MHz (320 kHz)  <-- 상한 인접점
  R_FSET =  66.5 kΩ  ->  f_sw = 0.62 MHz (620 kHz)  <-- 하한 인접점
  R_FSET =  35.7 kΩ  ->  f_sw = 1.06 MHz (1060 kHz)
  R_FSET =  25.0 kΩ  ->  f_sw = 1.44 MHz (1440 kHz)
  R_FSET =  18.0 kΩ  ->  f_sw = 1.91 MHz (1910 kHz)
  R_FSET =  16.0 kΩ  ->  f_sw = 2.12 MHz (2120 kHz)
```

회로상 실장 저항은 $R_9 = 82.0\text{k}\Omega \pm 1\%$ (`0603WAF8202T5E`, LCSC `C325632`)입니다. $82\text{k}\Omega$은 $66.5\text{k}\Omega$($620\text{kHz}$)과 $143\text{k}\Omega$($320\text{kHz}$) 사이에 위치합니다.

스위칭 컨버터의 내부 발진기 메커니즘에서 램프 충전 주기($T_{\text{sw}} = 1/f_{\text{sw}}$)는 $R_{\text{FSET}}$에 선형 비례하므로, 주파수 직접 보간이 아닌 **주기 기반 선형 보간(Period Linear Interpolation)**을 적용하여 공칭값을 산출합니다:
- $T(66.5\text{k}\Omega) = 1 / 0.62\text{MHz} = 1.6129\,\mu\text{s}$
- $T(143.0\text{k}\Omega) = 1 / 0.32\text{MHz} = 3.1250\,\mu\text{s}$
- $T(82.0\text{k}\Omega) = 1.6129 + \frac{82.0 - 66.5}{143.0 - 66.5} \times (3.1250 - 1.6129) = 1.9192\,\mu\text{s}$
- **보간 공칭 주파수**: $f_{\text{sw,nom}} = \frac{1}{1.9192\,\mu\text{s}} = \mathbf{521.0\,\text{kHz}}$

Chief Authority의 독립 검산에서도 확인된 바와 같이, 공칭값 약 $521\text{kHz}$는 수학적으로 완전히 일치합니다.

### 2.2 확인된 사실(Fact)과 공학적 가정(Assumption)의 분리

| 구분 | 항목 | 공학적 상태 | 상세 내용 |
| :--- | :--- | :---: | :--- |
| **Fact (확인된 사실)** | $R_9$ 공칭 저항 및 정밀도 | **확인 완료** | UNI-ROYAL `0603WAF8202T5E` (LCSC `C325632`), $82.0\text{k}\Omega \pm 1\%$. |
| **Fact (확인된 사실)** | Table 1 이산 데이터 | **확인 완료** | MPS MP3426 데이터시트 공식 Table 1 데이터 포인트 ($66.5\text{k}\Omega \to 620\text{kHz}$, $143\text{k}\Omega \to 320\text{kHz}$). |
| **Fact (확인된 사실)** | 공칭 주기 선형 보간 주파수 | **확인 완료** | $521.0\text{kHz}$ ($T_{\text{sw}} = 1.9192\mu\text{s}$). 과거 가짜 공식($1.22\text{MHz}$)은 영구 폐기됨. |
| **Assumption (공학적 가정)**| 내부 발진기 $\pm 15\%$ 공차 | **미확인 (가정)** | MPS 범용 DC-DC 컨버터의 전온도 범위($-40^\circ\text{C}\sim +125^\circ\text{C}$) 내부 발진기 편차를 $\pm 15\%$로 가정한 모델임. MP3426 데이터시트 Table 1에는 외장 저항 사용 시 공차 Min/Max가 수치로 명시되어 있지 않음. |
| **Assumption (공학적 가정)**| 결합 최악 조건 범위 | **미확인 (가정)** | $R_9$ 오차($\pm 1\%$)와 발진기 가정 오차($\pm 15\%$)를 중첩한 $[439.2\,\text{kHz} \sim 604.3\,\text{kHz}]$는 WCCA 안전 마진 검토를 위한 탐색 범위이며, 제조사 보증 규격으로 확정할 수 없음. |

> [!IMPORTANT]
> **결정 D-01 판정**: **`CONDITIONAL`**
> - 공칭 $521.0\text{kHz}$는 산술적으로 타당함.
> - 최악 범위 $[439.2\,\text{kHz} \sim 604.3\,\text{kHz}]$는 제조사 FAE 공식 답변 또는 Phase 4 벤치 오실로스코프 실측 전까지 **확정 규격이 아닌 WCCA 탐색용 공학적 가정**으로 유지함.

---

## 3. 전원부 최악 조건 회로 해석 (WCCA Matrix)

4대 운용 시나리오별 전기적 파라미터 계산 대장입니다:
[`POWER_WORST_CASE_ANALYSIS_MATRIX.csv`](file:///Users/youngseok/Desktop/majn/docs/engineering/round3_2_1/phase1_power/POWER_WORST_CASE_ANALYSIS_MATRIX.csv)

| 시나리오 명칭 | $V_{\text{in}}$ | $P_{\text{out}}$ | $f_{\text{sw}}$ | $L$ 값 | 듀티비 ($D$) | 평균 입력전류 ($I_{\text{in,avg}}$) | 리플 전류 ($\Delta I_L$) | **피크 전류 ($I_{\text{peak}}$)** | **실효 전류 ($I_{\text{rms}}$)** |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **SCEN-1 (공칭)** | $5.00\,\text{V}$ | $7.56\,\text{W}$ | $521.0\,\text{kHz}$ | $4.70\,\mu\text{H}$ | $0.6038$ | $1.718\,\text{A}$ | $1.233\,\text{A}$ | **$2.335\,\text{A}$** | **$1.755\,\text{A}$** |
| **SCEN-2 (최악 강하)** | $4.50\,\text{V}$ | $7.56\,\text{W}$ | $439.2\,\text{kHz}$ | $3.76\,\mu\text{H}$ | $0.6434$ | $1.976\,\text{A}$ | $1.753\,\text{A}$ | **$2.853\,\text{A}$** | **$2.040\,\text{A}$** |
| **SCEN-3 (고전압)** | $5.50\,\text{V}$ | $7.56\,\text{W}$ | $604.3\,\text{kHz}$ | $4.70\,\mu\text{H}$ | $0.5642$ | $1.527\,\text{A}$ | $1.093\,\text{A}$ | **$2.074\,\text{A}$** | **$1.559\,\text{A}$** |
| **SCEN-4 (10W 피크)** | $4.50\,\text{V}$ | $10.00\,\text{W}$ | $439.2\,\text{kHz}$ | $3.76\,\mu\text{H}$ | $0.6434$ | $2.614\,\text{A}$ | $1.753\,\text{A}$ | **$3.491\,\text{A}$** | **$2.663\,\text{A}$** |

---

## 4. L1 파워 인덕터 정밀 열해석 및 자기 포화 적격성 검증 (결정 D-02)

### 4.1 부품 정격 및 제조사 기준치 (Fact)
- **적용 부품**: Sunlord `SWPA6045S4R7MT` (LCSC `C78804`, 6.0 x 6.0 x 4.5 mm)
- **공칭 인덕턴스**: $4.7\,\mu\text{H} \pm 20\%$ (최소 $3.76\,\mu\text{H}$)
- **직류 저항 (DCR)**: $26.0\,\text{m}\Omega$ (Typ) / $34.0\,\text{m}\Omega$ (Max) at $20^\circ\text{C}$
- **온도 상승 정격 ($I_{\text{rms}}$)**: **$3.30\,\text{A}$ (Min)** / **$3.60\,\text{A}$ (Typ)** ($\Delta T = 40^\circ\text{C}$ 상승 기준)
- **포화 전류 정격 ($I_{\text{sat}}$)**: **$4.97\,\text{A}$ (Min)** / **$5.50\,\text{A}$ (Typ)** ($\Delta L/L = -30\%$ 기준 at $25^\circ\text{C}$)

### 4.2 열저항 ($R_{\text{th}} = 108.0^\circ\text{C/W}$)의 출처 및 유효 조건
- **도출 근거**: 제조사 규격에서 $I_{\text{rms}} = 3.30\,\text{A}$ 인가 시 최대 DCR($34.0\,\text{m}\Omega$)에서 $\Delta T = 40.0^\circ\text{C}$ 상승하므로:
  $$R_{\text{th}} = \frac{\Delta T}{I_{\text{rms}}^2 \times \text{DCR}_{\text{max}}} = \frac{40.0^\circ\text{C}}{3.30^2 \times 0.034\,\Omega} \approx \mathbf{108.0^\circ\text{C/W}}$$
- **유효 한계 및 미확인 사항**: 본 열저항은 Sunlord의 **표준 4층 FR4 테스트 기판(자연 대류 환경)**에서 측정한 규격값입니다. 실제 MAJN PCB는 $80 \times 60\text{mm}$ 협소 기구 공간에 위치하며, 하우징 밀폐 및 인접 열원(TAS5805M 앰프, ESP32-S3)의 복합 발열로 인해 실제 현물 기판에서의 유효 열저항은 달라질 수 있습니다.

### 4.3 인덕터 내부 코어 온도와 영아 접촉 외장 표면 온도의 엄격한 분리
Chief Authority의 지적에 따라 다음 사항을 명확히 정의합니다:
- **인덕터 코어 온도 ($T_{\text{core}} = 41.0^\circ\text{C} \sim 86.6^\circ\text{C}$)**:
  인덕터 내부 권선 및 페라이트 코어의 열평형 온도로서, 부품 절연 등급(Class B/F, 최대 내열 한계 $125^\circ\text{C}$) 만족 여부를 판단하는 전자 부품 신뢰성 지표입니다.
- **영아 접촉 외장 표면 온도 ($<43^\circ\text{C}$)**:
  영아용 의료/돌봄 기기 안전 표준(IEC 62368-1 표면 접촉 한계)에 따른 기구 외장 표면 온도입니다.
- **분리 원칙**: 인덕터 코어 온도가 $41^\circ\text{C}$라고 해서 "영아 접촉 안전성이 입증되었다"고 결론 내리는 것은 중대한 논리적 비약입니다. 인덕터 발열이 기구 케이스 표면으로 전달되는 열경로는 내부 공기층, 기구 벽면 두께, 차폐 구조에 의해 결정되므로, 외장 표면 온도는 Phase 4 완성품 기구 환경 챔버 시험을 통해 별도로 독립 측정해야 합니다.

### 4.4 온도 디레이팅에 따른 포화전류 ($I_{\text{sat}}$) 모델링 및 한계
[`INDUCTOR_SWPA6045_DETAILED_THERMAL_SATURATION_ANALYSIS.csv`](file:///Users/youngseok/Desktop/majn/docs/engineering/round3_2_1/phase1_power/INDUCTOR_SWPA6045_DETAILED_THERMAL_SATURATION_ANALYSIS.csv) 결과 요약:

| 시나리오 명칭 | 주위온도 ($T_a$) | 실효전류 ($I_{\text{rms}}$) | 총 손실 ($P_{\text{total}}$) | **온도 상승 ($\Delta T$)** | **코어 온도 ($T_{\text{core}}$)** | 감쇄 포화전류 ($I_{\text{sat,min}}$) | 인출 피크전류 ($I_{\text{peak}}$) | **최소 포화 마진 (Margin)** |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **SCEN-1 (공칭)** | $25.0^\circ\text{C}$ | $1.755\,\text{A}$ | $0.148\,\text{W}$ | $+16.0^\circ\text{C}$ | **$41.0^\circ\text{C}$** | $4.74\,\text{A}$ | $2.335\,\text{A}$ | **$+50.8\%$** |
| **SCEN-2 (최악 강하)**| $50.0^\circ\text{C}$ | $2.040\,\text{A}$ | $0.206\,\text{W}$ | $+22.2^\circ\text{C}$ | **$72.2^\circ\text{C}$** | $4.32\,\text{A}$ | $2.853\,\text{A}$ | **$+34.0\%$** |
| **SCEN-3 (고전압)** | $25.0^\circ\text{C}$ | $1.559\,\text{A}$ | $0.124\,\text{W}$ | $+13.3^\circ\text{C}$ | **$38.3^\circ\text{C}$** | $4.78\,\text{A}$ | $2.074\,\text{A}$ | **$+56.6\%$** |
| **SCEN-4 (10W 피크)**| $50.0^\circ\text{C}$ | $2.663\,\text{A}$ | $0.339\,\text{W}$ | $+36.6^\circ\text{C}$ | **$86.6^\circ\text{C}$** | $4.14\,\text{A}$ | $3.491\,\text{A}$ | **$+15.7\%$** |

- **$4.97\text{A} \to 4.14\text{A}$ 감쇄 근거**: 페라이트/컴포지트 코어 재질의 일반적 큐리 온도 감쇄 곡선 모델(상온 $100\%$, $60^\circ\text{C}$ $90\%$, $85^\circ\text{C}$ $85\%$, $100^\circ\text{C}$ $80\%$)을 적용하여 SCEN-4 코어 온도 $86.6^\circ\text{C}$에서 감쇄 계수 $0.833$을 곱한 결과입니다.
- **한계점**: Sunlord의 공식 데이터시트는 $25^\circ\text{C}$ 포화 곡선만 제공하며 고온 포화 곡선은 제조사에 별도 요청해야 합니다. 또한 코어 손실($35\text{mW}$)은 Steinmetz 추정식에 기반한 가정값입니다.

> [!IMPORTANT]
> **결정 D-02 판정**: **`HOLD`**
> - 6045 패키지 유지가능성은 높으나, 실제 PCB 열환경 및 고온 포화 감쇄 모델이 실측으로 입증되지 않았으므로 적격 확정 불가.
> - 따라서 **8040 교체안 기각 역시 현재 시점에서 승인 보류(`HOLD`)**하며, Phase 4 벤치 전류 프로브 파형 및 열화상 카메라 실측 결과로 최종 확정함.

---

## 5. PVDD 12V 출력 MLCC DC Bias 및 전압 리플 정밀 재검증 (결정 D-03)

### 5.1 $C_{\text{eff}}$ 산술 불일치 원인 규명 및 10단계 투명 감쇄 복원
Chief Authority께서 지적하신 산술 불일치:
> "보고서에는 22µF 커패시터 2개 병렬 구성에 잔존율을 적용한 결과가 기재되어 있어. 그런데 2x22µF 50V 부품의 경우 $44\mu\text{F} \times 75\% = 33.0\mu\text{F}$인데 보고서에는 $24.5\mu\text{F}$로 기재되어 불일치함."

**원인 규명**:
선행 보고서에서 제시된 $24.5\mu\text{F}$는 단순 12V DC 바이어스 최소 잔존율($75\%$)만 곱한 것이 아니라, **초기 용량 공차($0.90$) $\times$ 온도 드리프트($0.85$) $\times$ 경시 노화($0.97$) = $0.7421$의 복합 감쇄 계수(Compound Derating Factor)**를 중첩 곱하여 산출한 최악 유효용량($C_{\text{eff,worst}}$)이었습니다:
$$C_{\text{eff,worst}} = 44.0\,\mu\text{F} \times 0.75 \times (0.85 \times 0.90 \times 0.97) = 33.0\,\mu\text{F} \times 0.74205 \approx \mathbf{24.5\,\mu\text{F}}$$
그러나 선행 보고서가 이 중간 계산 과정(10개 항목)을 생략한 채 최종 결과만 표기하고 단위를 $\mu\text{H}$로 오기함으로써 중대한 혼선을 초래하였습니다.

### 5.2 10개 중간 파라미터 완전 공개 대조표
모든 단위 오기($\mu\text{H} \to \mu\text{F}$)를 바로잡고, 순수 DC 대표값($C_{\text{eff,typ}}$)과 최악 복합 유효용량($C_{\text{eff,worst}}$)의 연결 과정을 전면 공개합니다:
[`CAPACITOR_DC_BIAS_AND_RIPPLE_ANALYSIS.csv`](file:///Users/youngseok/Desktop/majn/docs/engineering/round3_2_1/phase1_power/CAPACITOR_DC_BIAS_AND_RIPPLE_ANALYSIS.csv)

| 후보군 구성 (Part) | 공칭 용량 ($C_{\text{nom}}$) | DC 바이어스 Typ (%) | **순수 DC 대표용량 ($C_{\text{eff,typ}}$)** | DC 바이어스 Min (%) | DC 최소 용량 ($C_{\text{dc,min}}$) | 온도 계수 (Temp) | 공차 계수 (Tol) | 노화 계수 (Aging) | **복합 감쇄 계수 (Compound)** | **최악 유효용량 ($C_{\text{eff,worst}}$)** | SCEN-1 리플 (Typ / Worst) | SCEN-2 리플 (Typ / Worst) |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Legacy (2x 0603 10µF 25V)** | **$20.0\,\mu\text{F}$** | $28.0\%$ | **$5.6\,\mu\text{F}$** | $22.0\%$ | $4.40\,\mu\text{F}$ | $0.85$ | $0.80$ | $0.97$ | **$0.6596$** | **$2.9\,\mu\text{F}$** | $134.7\,\text{mV}$ / $254.1\,\text{mV}$ | $171.2\,\text{mV}$ / $322.2\,\text{mV}$ |
| **Candidate A (2x 1210 22µF 25V)** | **$44.0\,\mu\text{F}$** | $45.0\%$ | **$19.8\,\mu\text{F}$** | $38.0\%$ | $16.72\,\mu\text{F}$ | $0.85$ | $0.90$ | $0.97$ | **$0.7421$** | **$12.4\,\mu\text{F}$** | $40.0\,\text{mV}$ / $61.7\,\text{mV}$ | $51.2\,\text{mV}$ / $78.6\,\text{mV}$ |
| **Candidate B (2x 1210 22µF 35V)** | **$44.0\,\mu\text{F}$** | $60.0\%$ | **$26.4\,\mu\text{F}$** | $52.0\%$ | $22.88\,\mu\text{F}$ | $0.85$ | $0.90$ | $0.97$ | **$0.7421$** | **$17.0\,\mu\text{F}$** | $30.3\,\text{mV}$ / $45.5\,\text{mV}$ | $38.8\,\text{mV}$ / $58.0\,\text{mV}$ |
| **Candidate C (2x 1210 22µF 50V)** | **$44.0\,\mu\text{F}$** | $85.0\%$ | **$37.4\,\mu\text{F}$** | $75.0\%$ | $33.00\,\mu\text{F}$ | $0.85$ | $0.90$ | $0.97$ | **$0.7421$** | **$24.5\,\mu\text{F}$** | **$22.0\,\text{mV}$** / **$32.1\,\text{mV}$** | **$28.2\,\text{mV}$** / **$41.0\,\text{mV}$** |

### 5.3 리플 계산 재검증 및 부품 선정 권고
$$\Delta V_{\text{out}} = \frac{I_{\text{out}} \cdot D}{f_{\text{sw}} \cdot C_{\text{eff}}} + \Delta I_L \cdot \text{ESR}_{\text{parallel}}$$
- **Candidate B (35V 정격, `GRM32ER7YA226`)**:
  - 공칭 순수 DC 조건 리플: $30.3\,\text{mV}$ (양호).
  - 최악 강하 조건(SCEN-2): 유효용량이 $17.0\mu\text{F}$로 떨어져 최악 리플이 **$58.0\,\text{mV}$**로 목표 상한($\le 50\,\text{mV}$)을 $16\%$ 초과함.
- **Candidate C (50V 정격, `GRM32ER71H226`) [최우선 권고 부품]**:
  - 공칭 순수 DC 조건 리플: **$22.0\,\text{mV}$**.
  - 최악 극단 조건(SCEN-2): 모든 감쇄를 적용한 최악 용량($24.5\mu\text{F}$)에서도 리플이 **$41.0\,\text{mV}$**에 불과하여 목표 기준($\le 50\,\text{mV}$)을 전 시나리오에서 완전 만족함.

> [!IMPORTANT]
> **결정 D-03 판정**: **`CONDITIONAL PASS`**
> - 산술 불일치 원인을 10단계 복합 감쇄 모델로 완벽히 해명하고 투명하게 복원함.
> - 단위 오기($\mu\text{H} \to \mu\text{F}$) 전수 수정 완료.
> - 최악 조건에서도 $50\text{mV}$ 이내 리플을 보장하는 **50V 정격 1210 22µF MLCC (`GRM32ER71H226`)를 최우선 확정 부품으로 강력 권고**함.
> - 최종 승인은 Phase 4 벤치 스프링 접지 프로브 실측($\le 50\text{mV}$)으로 종결함.

---

## 6. Bleeder 저항 및 무부하 방전/과전압 억제 정밀 검증

Chief Authority의 지적에 따라 **수동 방전 안전성**과 **무부하 펄스 스킵 과전압 억제**를 엄격히 분리하여 평가합니다.

### 6.1 수동 방전 안전성 (Passive Safe Discharge): `PASS`
- **블리더 저항**: $R_{\text{BLEED}} = 1.5\,\text{k}\Omega \pm 1\%$, 1206 패키지 ($0.25\,\text{W}$ 정격).
- **소비 전력**: $P = \frac{12.17^2}{1500} = \mathbf{98.7\,\text{mW}}$ (정격 $250\text{mW}$ 대비 부하율 $39.5\%$, 열적 매우 안전).
- **방전 소요 시간 계산 ($12.17\text{V} \to <1.0\text{V}$)**:
  감쇄비 인자: $\ln(12.17 / 1.0) \approx 2.499$.
  - 최악 유효용량 ($C_{\text{eff,worst}} = 24.5\,\mu\text{F}$):
    $$\tau_{\text{min}} = 1500\,\Omega \times 24.5\,\mu\text{F} = 36.75\,\text{ms} \implies t_{\text{dis,min}} = 36.75 \times 2.499 = \mathbf{91.8\,\text{ms}}$$
  - 공칭 미감쇄 용량 ($C_{\text{nom}} = 44.0\,\mu\text{F}$):
    $$\tau_{\text{max}} = 1500\,\Omega \times 44.0\,\mu\text{F} = 66.00\,\text{ms} \implies t_{\text{dis,max}} = 66.00 \times 2.499 = \mathbf{164.9\,\text{ms}}$$
- **평가**: 유효 정전용량의 불확실성 전 대역($24.5\mu\text{F} \sim 44.0\mu\text{F}$)에서 전원 차단 후 잔류 전압이 $1.0\text{V}$ 미만으로 떨어지는 시간은 **$91.8\,\text{ms} \sim 164.9\,\text{ms}$ (0.17초 미만)**으로, 영아 및 사용자 감전 안전 기준($<1.0\text{초}$)을 완벽히 만족합니다.

### 6.2 무부하 펄스 스킵 과전압 억제 (Pulse-Skipping Overvoltage Suppression): `HOLD`
- **이론적 최소 펄스 전력**:
  $$E_{\text{min}} = \frac{V_{\text{in}}^2 \cdot t_{\text{on,min}}^2}{2 L} = \frac{5.0^2 \times (100 \times 10^{-9})^2}{2 \times 4.7 \times 10^{-6}} = 26.6\,\text{nJ} \implies P_{\text{min,pulse}} = 26.6\,\text{nJ} \times 521\,\text{kHz} = 13.86\,\text{mW}$$
- **Chief Authority 지적 수용**:
  정적 소비 전력($98.7\text{mW}$)이 최소 펄스 전력($13.86\text{mW}$)보다 크다는 사실만으로 동적 과전압 억제를 단정할 수 없습니다. MP3426의 경부하/무부하 히스테리시스 버스트 스위칭 동작, 최소 온타임 펄스 방출 주기, 출력 MLCC 에너지 흡수 및 과도 피크 오버슈트 억제 여부는 회로 시뮬레이션이나 정적 수식만으로 확정할 수 없으며, **실제 0mA 무부하 상태에서 벤치 오실로스코프로 실측 검증**해야 합니다.

> [!IMPORTANT]
> **블리더 저항 종합 판정**: **`HOLD`**
> - 수동 방전 시간($91.8\sim 164.9\text{ms}$)은 PASS.
> - 무부하 펄스 스킵 과전압 억제는 벤치 실측 전까지 **`HOLD`**로 분류함.

---

## 7. 자동화 검증 스크립트 및 11개 회귀 테스트 (`verify_phase1_power_design.py`)

Chief Authority께서 요구하신 **7대 결함 주입 테스트(Fault Injection Suite)**를 스크립트에 완전히 내장하고, 기존 4대 단위 테스트와 통합하여 총 11개 테스트를 전수 통과(Exit Code 0)하도록 개선하였습니다.

```
=== RUNNING COMPLETE 11-TEST REGRESSION SUITE ===
[PASS] Test 1: Table 1 boundary point interpolation verified
[PASS] Test 2: Frequency min/nom/max bounds sanity verified
      Worst-Case 10W Inductor Stress: Ipk=3.491A, Tcore=86.6C, Isat_min(T)=4.14A, Margin=15.7%
[PASS] Test 3: Worst-case thermal & saturation computation verified
[PASS] Test 4: Capacitor voltage rating DC bias hierarchy verified
[PASS] Test 5 (FI-01): Ceff compound derating arithmetic verified (Cnom * ret_min * comp == Ceff_worst)
[PASS] Test 6 (FI-02): Physical unit integrity verified (zero uH in capacitor tables)
[PASS] Test 7 (FI-03): Component provenance & LCSC ID integrity verified (L1: C78804, R9: C325632)
[PASS] Test 8 (FI-04): Datasheet provenance citations verified
[PASS] Test 9 (FI-05): Copper thermal coefficient physical range verified (0.0030 < alpha < 0.0050)
[PASS] Test 10 (FI-06): Min/Max boundary condition monotonicity verified (f_min < f_nom < f_max)
[PASS] Test 11 (FI-07): Tolerance and derating parameter bounds sanity verified

[ALL 11 TESTS PASSED CLEANLY - EXIT CODE 0]
```

### 7.1 결함 주입 테스트(FI-01 ~ FI-07) 검증 상세
1. **FI-01 ($C_{\text{eff}}$ 복합 감쇄 산술 무결성)**: $C_{\text{dc,min}} = C_{\text{nom}} \times \text{ret}_{\text{min}}$ 및 $C_{\text{eff,worst}} = C_{\text{dc,min}} \times \text{Compound Derating}$ 수식을 전 부품에 대해 엄격 검증. 불일치 주입 시 예외 발생 확인.
2. **FI-02 (물리 단위 무결성)**: 커패시터 모델 딕셔너리, CSV 헤더, 마크다운 표에서 $\mu\text{H}$ 사용을 원천 차단.
3. **FI-03 (부품 LCSC ID 무결성)**: L1(`C78804`), R9(`C325632`), U1(`C72213`), R_BLEED(`C17936`)의 BOM 품번 및 LCSC ID 일치 검증.
4. **FI-04 (데이터시트 출처 무결성)**: Table 1, SimSurfing 등 필수 인용 문헌 존재 여부 검증.
5. **FI-05 (구리 온도계수 물리 범위)**: 구리 저항 온도계수가 물리적 타당 범위($0.0030 < \alpha < 0.0050$) 내에 있는지 검증.
6. **FI-06 (경계 조건 단조성)**: 스위칭 주파수 경계 조건($f_{\text{min}} < f_{\text{nom}} < f_{\text{max}}$)의 역전 방지 검증.
7. **FI-07 (공차 및 디레이팅 파라미터 유효 범위)**: 모든 감쇄 계수가 $(0.0, 1.0]$ 범위 내에 있는지 파라미터 위생 검증.

---

## 8. Phase 1 핵심 결정 최종 판정 요약표

| 결정 ID | 검증 항목 | 선행 보고서 주장 | Phase 1 v1.1 정밀 재검증 결과 | **최종 판정** | 후속 게이트 종결 조건 |
| :---: | :--- | :--- | :--- | :---: | :--- |
| **D-01** | **MP3426 스위칭 주파수** | 1.22MHz (날조 공식) | 주기 선형 보간 기반 **공칭 $521.0\,\text{kHz}$** 확인 완료. $\pm 15\%$ 발진기 공차는 공학적 가정. | **`CONDITIONAL`** | Phase 4 벤치 SW 노드 오실로스코프 주파수 실측 또는 MPS 공식 FAE 확인 |
| **D-02** | **L1 인덕터 적격성** | 8040 교체 주장 | SWPA6045S4R7MT 포화 마진 유지 가능성 높음. 단, 실 PCB 열환경 및 고온 포화 모델 미확인. | **`HOLD`** | Phase 4 벤치 전류 프로브 실측 (선형 램프 유지) 및 열화상 카메라 실측 |
| **D-03** | **PVDD 12V MLCC 적격성** | 산술 불일치 ($24.5\mu\text{F}$ 도출 미공개) | 10단계 복합 감쇄 전과정 공개 복원. **50V 정격 부품(`GRM32ER71H226`) 최우선 권고** (최악 리플 $41.0\text{mV} \le 50\text{mV}$). | **`CONDITIONAL PASS`** | Phase 4 벤치 스프링 접지 프로브 리플 실측 ($\le 50\text{mV}$ 확인) |
| **Bleeder**| **블리더 저항 기능** | 무부하 과전압 완전 억제 단정 | 수동 방전 시간($91.8\sim 164.9\text{ms}$)은 PASS. 무부하 펄스 스킵 동적 과전압 억제는 미확인. | **`HOLD`** | Phase 4 벤치 0mA 무부하 오실로스코프 파형 실측 |
| **Engine** | **자동화 검증 엔진** | 4개 기본 테스트 | 7대 결함 주입 테스트(FI-01~07) 포함 **총 11개 회귀 테스트 100% 통과 (Exit Code 0)**. | **`PASS`** | CI/CD 파이프라인 지속 모니터링 |
| **Phase 1**| **1단계 공식 종료** | 즉시 종료 승인 요청 | Chief Authority 결정에 따라 **종료 승인 보류**. Phase 2 착수 보류. | **`HOLD`** | D-01/D-02 실측 시험 계획서 확정 및 승인권자 인가 |
| **G2~G5**  | **설계 단계 진입** | - | 원본 보호 가드레일에 따라 **회로도/PCB/BOM/펌웨어 수정 일체 동결 유지**. | **`STRICT HOLD`** | Chief Authority의 정식 ECO 승인 |

---

## 9. 결론 및 단계 통제 권고

1. **지적 사항 전면 해명 및 투명성 회복**:
   Chief Authority께서 지적하신 D-03 유효용량 산술 불일치는 10단계 복합 감쇄 계수 체계를 통해 완벽하게 해명되었으며, 단위 오류($\mu\text{H} \to \mu\text{F}$) 및 품번 매핑을 완료하였습니다.
2. **독립적 비판 시각 견지**:
   D-01 발진기 공차의 근거 한계, D-02 실 PCB 열저항 및 영아 접촉 표면 온도의 분리 필요성, Bleeder의 무부하 동적 제어 한계를 가감 없이 인정하고, 판정을 Chief Authority의 기준에 맞춰 **`HOLD`** 및 **`CONDITIONAL`**로 엄격히 조정하였습니다.
3. **엄격한 가드레일 준수**:
   본 1단계 재검증 과정에서도 회로도 CAD(`.epro2`, `.json`, `.sch`, `.pcb`), 레이아웃 파일, BOM 원본, 펌웨어 소스코드는 단 1바이트도 변경되지 않았습니다.
4. **단계 통제 준수**:
   본 재검증 보고서를 제출하고 **Phase 2로 절대 임의 진행하지 않으며, Gate G2~G5 동결 상태를 확고히 유지**합니다.
