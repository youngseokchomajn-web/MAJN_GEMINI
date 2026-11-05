# [전원 계산 보고서] MP3426 승압 컨버터 및 L1 파워 인덕터 전류 마진 정밀 공학 계산서
(Precision Engineering Calculation: MP3426 Boost Converter Currents & L1 Inductor Margins)

- **문서 식별자**: `MAJN_MP3426_INDUCTOR_CURRENT_CALCULATION`
- **리비전**: v1.0
- **작성 일자**: 2026-11-05
- **책임 주체**: Antigravity (전력전자 및 신뢰성 공학 검토)
- **적용 대상**: Prototype #0005 복원 기준선 및 차기 PCB #0006 승압 회로 (U3 MP3426, L1 Sunlord MWPA7070S4R7MT)

---

## 1. 개요 및 계산 목적

본 문서는 선행 감사 보고서에서 제시된 **"인덕터 피크 전류 4.39A"**의 정확한 물리적 출처와 수식 유도 과정을 명시하고, L1 파워 인덕터의 데이터시트상 정격(포화 전류 $I_{\text{sat}}$, 온도 상승 전류 $I_{\text{rms}}$)과 비교하여 **상온($25^\circ\text{C}$) 및 밀폐 고온($60^\circ\text{C}$) 환경에서의 실제 설계 마진을 엄격히 규명**하기 위해 작성되었습니다.

---

## 2. 기본 입력 파라미터 및 출처 (Source Traceability)

| 파라미터 명칭 | 기호 | 설계 적용값 | 단위 | 데이터 출처 / 근거 |
| :--- | :---: | :---: | :---: | :--- |
| **입력 공칭 전압** | $V_{in,\text{nom}}$ | 5.0 | V | USB-C 표준 VBUS 전압 |
| **입력 최저 전압 (Worst)** | $V_{in,\text{min}}$ | 4.50 | V | USB 케이블 및 커넥터 전압 강하 고려 최저 전압 |
| **과도 최저 전압** | $V_{in,\text{trans}}$ | 4.60 | V | 음향 피크 인출 시의 순간 입력 전압 |
| **출력 전압** | $V_{out}$ | 12.09 | V | $R_1=110\text{k}\Omega, R_2=12.4\text{k}\Omega, V_{FB}=1.225\text{V}$ ($1.225 \times (1 + 110/12.4)$) |
| **스위칭 주파수** | $f_{sw}$ | 1.0 | MHz | MP3426 내부 발진 주파수 ($T = 1.0\,\mu\text{s}$) |
| **인덕터 공칭 인덕턴스** | $L$ | 4.7 ($\pm 20\%$) | µH | Sunlord MWPA7070S4R7MT (실물 마킹 '4R7') |
| **인덕터 직류 저항** | $DCR$ | 21.0 (최대 27.3) | mΩ | Sunlord MWPA7070S4R7MT 데이터시트 |
| **쇼트키 다이오드 순방향 전압**| $V_D$ | 0.45 | V | SS34 (D3) 순방향 전압 강하 |
| **컨버터 변환 효율** | $\eta$ | 88.0% | - | MP3426 전형적 효율 곡선 (최악 조건 0.88 가정) |
| **내부 FET 전류 제한치** | $I_{\text{sw,limit}}$ | 최소 5.5 / 대표 6.0 | A | MP3426 데이터시트 Section 7.2 Switch Current Limit |
| **인덕터 포화 전류 ($25^\circ\text{C}$)**| $I_{\text{sat}}$ | 7.5 | A | $\Delta L/L \le 30\%$ 감소 기준 직류 전류 |
| **인덕터 온도 상승 전류** | $I_{\text{rms}}$ | 5.0 | A | 인덕터 표면 온도 상승 $\Delta T \le 40^\circ\text{C}$ 기준 전류 |

---

## 3. 부하 동작 모드별 전류 수식 유도

승압 컨버터(Boost Converter)는 연속 도통 모드(CCM)에서 동작하며, 정상 연속 상태와 음향 과도 피크 상태의 전류 거동이 다릅니다.

### 3.1 [모드 1] 정상 연속 최대 동작 (Steady-State 10W System Limit)
요구사항 `REQ-P0-05`에 의해 시스템 전체 전력은 최대 10W로 제한됩니다.

1. **출력 연속 전류**:
   $$I_{out,\text{cont}} = \frac{10.0\,\text{W}}{12.0\,\text{V}} = 0.833\,\text{A}$$
2. **소비 입력 전력**:
   $$P_{in,\text{cont}} = \frac{P_{out}}{\eta} = \frac{10.0\,\text{W}}{0.88} = 11.36\,\text{W}$$
3. **인덕터 평균 전류 (입력 평균 전류)** at $V_{in,\text{min}} = 4.5\,\text{V}$:
   $$I_{L,\text{avg,cont}} = \frac{P_{in,\text{cont}}}{V_{in,\text{min}}} = \frac{11.36\,\text{W}}{4.50\,\text{V}} = \mathbf{2.525\,\text{A}}$$
4. **듀티비 ($D$)**:
   $$D = \frac{V_{out} + V_D - V_{in}}{V_{out} + V_D} = \frac{12.0 + 0.45 - 4.5}{12.0 + 0.45} = \frac{7.95}{12.45} = \mathbf{0.6385}$$
5. **인덕터 피크-투-피크 리플 전류 ($\Delta I_L$)**:
   $$\Delta I_L = \frac{V_{in} \cdot D}{f_{sw} \cdot L} = \frac{4.50\,\text{V} \times 0.6385}{1.0 \times 10^6\,\text{Hz} \times 4.7 \times 10^{-6}\,\text{H}} = \frac{2.873}{4.7} = \mathbf{0.611\,\text{A}}$$
6. **정상 동작 인덕터 피크 전류 ($I_{L,\text{peak,cont}}$)**:
   $$I_{L,\text{peak,cont}} = I_{L,\text{avg,cont}} + \frac{\Delta I_L}{2} = 2.525\,\text{A} + 0.306\,\text{A} = \mathbf{2.831\,\text{A}}$$

---

### 3.2 [모드 2] 오디오 동적 과도 피크 동작 (Transient Audio Dynamic Condition)
- **4.39A 전류의 정체 (Identity of 4.39A)**:
  TAS5805M 오디오 앰프가 저주파 음향(수면 유도 백색소음의 저주파 비트 또는 심박음 버스트, 듀레이션 $< 20\,\text{ms}$)을 강하게 재생할 때, 순간적인 동적 피크 출력이 **약 16.5W ($I_{out,\text{trans}} \approx 1.375\,\text{A}$)**까지 도달할 수 있습니다.
  
1. **순간 입력 소비 전력**:
   $$P_{in,\text{trans}} = \frac{16.5\,\text{W}}{0.88} = 18.75\,\text{W}$$
2. **순간 인덕터 평균 전류** at $V_{in} = 4.60\,\text{V}$:
   $$I_{L,\text{avg,trans}} = \frac{18.75\,\text{W}}{4.60\,\text{V}} = \mathbf{4.076\,\text{A}}$$
3. **과도 리플 전류** ($D = (12.45 - 4.6)/12.45 = 0.630$):
   $$\Delta I_{L,\text{trans}} = \frac{4.60\,\text{V} \times 0.630}{1.0\,\text{MHz} \times 4.7\,\mu\text{H}} = \mathbf{0.617\,\text{A}}$$
4. **최악 조건 과도 인덕터 피크 전류 ($I_{L,\text{peak,worst}}$)**:
   $$I_{L,\text{peak,worst}} = I_{L,\text{avg,trans}} + \frac{\Delta I_{L,\text{trans}}}{2} = 4.076\,\text{A} + 0.309\,\text{A} = \mathbf{4.385\,\text{A}} \approx \mathbf{4.39\,\text{A}}$$

> [!NOTE]
> **공학적 정의 확정**: **4.39A는 RMS나 평균전류가 아니라, 최저 입력전압에서 순간 음향 과도 부하(16.5W)가 인출될 때 인덕터 코일과 스위칭 FET를 통과하는 "순시 피크 전류(Worst-case Instantaneous Peak Inductor Current)"**입니다.

---

## 4. 데이터시트 정격 정의와의 직접 비교 타당성 검토

### 4.1 포화 전류 ($I_{\text{sat}} = 7.5\text{A}$)와의 비교 타당성
- **자기학적 원리**: 인덕터 자기 코어의 자속 밀도 $B = \mu H = \mu \frac{N \cdot i(t)}{l_e}$는 전류의 실효치(RMS)가 아니라 **순시 순시 피크 전류 $i(t)$에 직결**됩니다. 피크 전류가 코어의 포화 자속 밀도($B_{\text{sat}}$)를 넘어서면 급격한 인덕턴스 붕괴가 발생합니다.
- **데이터시트 정의**: Sunlord MWPA7070S4R7MT의 $I_{\text{sat}} = 7.5\text{A}$는 직류 전류 인가 시 인덕턴스가 $30\%$ 저하($\Delta L/L \le 30\%$)되는 지점입니다.
- **결론**: 따라서 계산된 **피크 전류 $4.39\text{A}$를 $I_{\text{sat}}$ $7.5\text{A}$와 직접 비교하는 것은 100% 이론적·공학적으로 타당**합니다.

### 4.2 온도 상승 전류 ($I_{\text{rms}} = 5.0\text{A}$)와의 비교
- **열적 원리**: 줄 발열($P_{\text{loss}} = I_{\text{rms}}^2 \times DCR$)은 실효 전류에 의해 결정됩니다.
- 정상 동작 시 인덕터 실효 전류:
  $$I_{L,\text{rms}} \approx \sqrt{I_{L,\text{avg}}^2 + \frac{\Delta I_L^2}{12}} = \sqrt{2.525^2 + \frac{0.611^2}{12}} = \mathbf{2.531\,\text{A}}$$
- 정격 $5.0\text{A}$ 대비:
  $$\frac{I_{L,\text{rms}}}{I_{\text{rms}}} = \frac{2.531\,\text{A}}{5.0\,\text{A}} = \mathbf{50.6\%}$$
- 인덕터 표면 온도 상승 추정치:
  $$\Delta T \approx 40^\circ\text{C} \times \left(\frac{2.531}{5.0}\right)^2 \approx \mathbf{10.25^\circ\text{C}}$$
- 정상 동작 시 인덕터 자체 발열은 $10.3^\circ\text{C}$에 불과하여 열적으로 매우 여유롭습니다.

---

## 5. 정밀 마진 분석: 상온($25^\circ\text{C}$) vs 고온($60^\circ\text{C}$)

금속 분말 몰딩 인덕터는 고온에서 자기 포화 특성이 완만하게 감소합니다. 밀폐 하우징 내부 온도 $60^\circ\text{C}$를 가정하여 $15\%$ 디레이팅을 적용합니다.

| 검토 항목 | 기호 | 상온 조건 ($25^\circ\text{C}$) | 고온 밀폐 조건 ($60^\circ\text{C}$) | 안전 기준 권고치 | 적합성 판정 |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **인덕터 실효 포화 전류** | $I_{\text{sat,eff}}$ | $7.50\,\text{A}$ (데이터시트) | $6.375\,\text{A}$ (15% Derated) | - | 기준치 |
| **과도 피크 전류** | $I_{L,\text{peak,worst}}$ | $4.39\,\text{A}$ | $4.39\,\text{A}$ | - | 인출치 |
| **인덕터 잔여 용량 마진 (Margin 1)** | $\frac{I_{\text{sat}} - I_{\text{peak}}}{I_{\text{sat}}}$ | **41.47%** | **31.14%** | $\ge 20\%$ | **PASS** |
| **요구치 대비 초과 설계율 (Margin 2)**| $\frac{I_{\text{sat}} - I_{\text{peak}}}{I_{\text{peak}}}$ | **70.84%** | **45.22%** | $\ge 30\%$ | **PASS** |
| **MP3426 FET 스위치 제한 마진** | $\frac{5.5\text{A} - I_{\text{peak}}}{5.5\text{A}}$ | **20.18%** | **20.18%** | $\ge 15\%$ | **PASS** |

---

## 6. 결론 및 공학적 제언

1. **4.39A 계산의 타당성**:
   - $4.39\text{A}$는 저주파 대출력 과도 부하 시의 **순시 인덕터 피크 전류**이며, $I_{\text{sat}}$와의 비교는 전력전자 설계 원칙에 완전히 부합합니다.
2. **실제 여유도 확정**:
   - 상온 잔여 용량 마진은 **41.5%**, 초과 설계율은 **70.8%**입니다.
   - 밀폐 케이스 내부 온도 $60^\circ\text{C}$ 디레이팅 환경에서도 잔여 마진은 **31.1%**로 유지되어 최소 안전 기준($\ge 20\%$)을 상회합니다.
3. **스위칭 FET 보호 마진**:
   - MP3426의 내부 하한 스위치 전류 트립 기준($5.5\text{A}$) 대비 $20.2\%$의 여유를 확보하여 과도 부하 시 원치 않는 FET 셧다운이 발생하지 않습니다.
4. **한계 및 물리 검증 권고**:
   - 본 계산은 제조사 데이터시트와 이론적 CCM 방정식에 기반한 수치적 증명이므로, **Gate G1/G6에서 실제 전류 프로브(Current Probe)를 통한 오실로스코프 파형 측정으로 최종 승인**되어야 합니다.
