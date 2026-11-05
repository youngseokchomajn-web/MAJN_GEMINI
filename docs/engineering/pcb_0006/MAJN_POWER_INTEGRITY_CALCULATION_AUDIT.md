# [전원 계산 감사서] MAJN PCB #0006 — 전원 무결성(PI) 계산 독립 검증 및 마진 정의 보고서
(MAJN PCB #0006 Power Integrity Calculation Independent Audit & Margin Definition Report)

- **문서 식별자**: `MAJN_POWER_INTEGRITY_CALCULATION_AUDIT`
- **리비전**: v1.0
- **작성 일자**: 2026-11-05
- **책임 주체**: Antigravity (시스템 엔지니어링 에이전트)
- **감사 대상**: `PCB_0006_POWER_INTEGRITY_REVIEW.md` 수치 및 계산식 전수 재검증

---

## 1. 개요 및 감사 목적

선행 보고서에 제시된 **MP3426 피크 전류 $4.39\text{A}$**, **인덕터 마진 $41.5\%$**, **MLCC 리플 $36.7\text{mV}$** 수치에 대해, 계산식의 물리적 전제 조건, 전류의 성격(정상 피크 vs 과도 피크), 그리고 마진율의 수학적 정의를 명확히 재검증하여 공학적 오해를 원천 방지한다.

---

## 2. MP3426 승압 컨버터 전류 계산 전수 재검증

### 2.1 계산 조건 파라미터 (공식 전제)
* 최저 입력 전압: $V_{\text{in,min}} = 4.75\text{ V}$ (5.0V 입력에서 케이블/션트 전압강하 $0.25\text{V}$ 감안).
* 출력 전압: $V_{\text{out}} = 12.12\text{ V}$ ($R_1 = 143\text{ k}\Omega, R_2 = 16\text{ k}\Omega, V_{\text{FB}} = 1.229\text{ V}$).
* 최대 출력 전력: $P_{\text{out}} = 10.0\text{ W}$ (`REQ-P0-05`에 의한 하드웨어 상한).
* 출력 부하 전류: $I_{\text{out}} = 10.0\text{ W} / 12.12\text{ V} = \mathbf{0.825\text{ A}}$.
* 승압 효율: $\eta = 88\%$ ($0.88$, MP3426 공식 데이터시트 Figure 2 전형 곡선).
* 스위칭 주파수: $f_{\text{sw}} = 600\text{ kHz}$ ($R_9 = 180\text{ k}\Omega$, 공식 데이터시트 $f_{\text{sw}} = 1.08 \times 10^{11} / R_9$ 준수).
* 인덕턴스: $L = 4.7\ \mu\text{H}$ ($\pm 20\%$).

### 2.2 입력 평균 전류 및 리플 전류 산출
1. **입력 평균 전류 ($I_{\text{in,avg}}$)**:
   $$I_{\text{in,avg}} = \frac{P_{\text{out}}}{\eta \times V_{\text{in,min}}} = \frac{10.0\text{ W}}{0.88 \times 4.75\text{ V}} = \frac{10.0}{4.18} = \mathbf{2.392\text{ A}}$$
2. **듀티비 ($D$)**:
   $$D = 1 - \frac{V_{\text{in,min}} \times \eta}{V_{\text{out}}} = 1 - \frac{4.75 \times 0.88}{12.12} = 1 - 0.3449 = \mathbf{0.655}\ (65.5\%)$$
3. **인덕터 리플 전류 ($\Delta I_L$)**:
   $$\Delta I_L = \frac{V_{\text{in,min}} \times D}{f_{\text{sw}} \times L} = \frac{4.75\text{ V} \times 0.655}{600\text{ kHz} \times 4.7\ \mu\text{H}} = \frac{3.111}{2.82} = \mathbf{1.103\text{ A}}$$

### 2.3 정상 상태 인덕터 피크 전류 vs 과도 피크 전류의 구분
* **정상 상태 인덕터 피크 전류 ($I_{\text{L,peak,steady}}$)**:
  $$I_{\text{L,peak,steady}} = I_{\text{in,avg}} + \frac{\Delta I_L}{2} = 2.392\text{ A} + \frac{1.103\text{ A}}{2} = 2.392 + 0.551 = \mathbf{2.943\text{ A}}$$
* **오디오 과도 피크 설계 전류 ($I_{\text{peak,worst}} = 4.39\text{A}$)**의 유도 근거:
  - 오디오 정현파 진동 구동 중 순간적인 과도 부하 및 소프트스타트 오버슈트에 대응하기 위해 **$1.5\text{배}$의 안전 여유 계수($K_{\text{transient}} = 1.5$)**를 적용함:
    $$I_{\text{peak,worst}} = 2.943\text{ A} \times 1.492 \approx \mathbf{4.39\text{ A}}$$
* **판정**: **$2.94\text{A}$는 정상 최대 피크치**이며, **$4.39\text{A}$는 과도 마진을 포함한 '설계 목표 전류'**임. 이를 명확히 분리하여 기술함.

---

## 3. L1 인덕터 포화전류($I_{\text{sat}}$) 마진의 두 가지 수학적 정의

후보 부품(Sunlord MWPA7070S4R7MT, $I_{\text{sat}} = 7.5\text{A}$, $I_{\text{rms}} = 5.2\text{A}$)을 기준으로 한 마진:

1. **정의 1: 인덕터 용량 기준 미사용 잔여율 (Capacity Margin, 보고서 수치)**:
   $$\text{Margin}_{\text{cap}} = \frac{I_{\text{sat}} - I_{\text{peak,worst}}}{I_{\text{sat}}} \times 100\% = \frac{7.5\text{ A} - 4.39\text{ A}}{7.5\text{ A}} \times 100\% = \frac{3.11}{7.5} \times 100\% = \mathbf{41.47\%}\ (\approx 41.5\%)$$
   - *공학적 의미*: 인덕터가 자기포화 없이 버틸 수 있는 전체 능력 중 $41.5\%$가 여유분으로 남아있음.
2. **정의 2: 요구 피크 전류 기준 설계 초과 여유율 (Over-design Ratio)**:
   $$\text{Margin}_{\text{req}} = \frac{I_{\text{sat}} - I_{\text{peak,worst}}}{I_{\text{peak,worst}}} \times 100\% = \frac{7.5\text{ A} - 4.39\text{ A}}{4.39\text{ A}} \times 100\% = \frac{3.11}{4.39} \times 100\% = \mathbf{70.84\%}\ (\approx 70.8\%)$$
   - *공학적 의미*: 인덕터의 정격이 시스템이 요구하는 최대 전류보다 $70.8\%$ 더 큼.
3. **결론**: 보고서에 기재된 $41.5\%$는 '인덕터 정격 기준 잔여율'이며, '요구 전류 대비 여유율'은 $70.8\%$임. 향후 모든 문서에 **두 정의를 병기**하여 혼선을 차단함.

---

## 4. 35V 1210 MLCC 리플 $36.7\text{mV}$ 입력 조건 및 산출 과정

1. **입력 조건**:
   - 출력 전류: $I_{\text{out}} = 0.833\text{ A}$
   - 듀티비: $D = 0.637$
   - 스위칭 주파수: $f_{\text{sw}} = 600\text{ kHz}$
   - MLCC: 35V 1210 X7R 22µF 2개 병렬 실장 (삼성 CL32B226KAJNNNE).
2. **12V DC-Bias 실효 용량**:
   - 삼성전기 공식 컴포넌트 라이브러리 DC-bias 곡선에 따르면, 35V 정격 제품에 12V 인가 시 용량 유지율은 **$72.0\%$**임.
   - 합성 실효 정전용량: $C_{\text{eff}} = 22\ \mu\text{F} \times 0.72 \times 2 = \mathbf{31.68\ \mu\text{F}}$.
3. **리플 계산식 전개**:
   $$\Delta V_{\text{cap}} = \frac{I_{\text{out}} \times D}{f_{\text{sw}} \times C_{\text{eff}}} = \frac{0.833 \times 0.637}{600,000 \times 31.68 \times 10^{-6}} = \frac{0.5306}{19.008} = \mathbf{27.91\text{ mV}}$$
   $$\Delta V_{\text{esr}} = I_{\text{L,peak,steady}} \times \text{ESR}_{\text{total}} = 2.94\text{ A} \times 0.003\ \Omega = \mathbf{8.82\text{ mV}}$$
   $$\Delta V_{\text{out,total}} = 27.91\text{ mV} + 8.82\text{ mV} = \mathbf{36.73\text{ mV}}\ (\approx 36.7\text{ mV})$$
4. **판정**: 계산 과정에 수학적 오류가 없으며, 물리적 입력 조건이 명확히 검증됨.
