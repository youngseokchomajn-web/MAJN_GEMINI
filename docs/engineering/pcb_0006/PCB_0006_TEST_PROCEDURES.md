# [시험 절차서] MAJN PCB #0006 — 표준 하드웨어 검증 및 계측 시험 절차서
(MAJN PCB #0006 Standard Hardware Test & Measurement Procedures)

- **문서 식별자**: `PCB_0006_TEST_PROCEDURES`
- **리비전**: v1.0
- **작성 일자**: 2026-11-05
- **책임 주체**: Antigravity (시스템 엔지니어링 에이전트)
- **적용 대상**: PCB #0006 실물 보드 벤치 검증

---

## 1. [TP-01] 전원 기동 시퀀싱 및 팝(Pop) 노이즈 계측 절차

### 1.1 계측 장비 세팅
* 오실로스코프 (4채널, 100MHz 이상):
  - Ch1: `TP_3V3` (3.3V LDO 레일)
  - Ch2: `BOOST_EN` (GPIO4 제어선)
  - Ch3: `TP_PVDD` (12V 승압 레일)
  - Ch4: `AMP_PDN` (GPIO13 제어선)
* 트리거 설정: Ch1 상승 에지 (Level 1.5V, Single Trigger).

### 1.2 실행 절차
1. 5V USB 전원 케이블을 체결하여 보드에 전원 인가.
2. ESP32 부팅 시 `BOOST_EN`과 `AMP_PDN`이 LOW 상태를 유지하는지 관측.
3. 펌웨어가 `BOOST_EN`을 HIGH로 올린 후 PVDD 전압이 $12.12\text{V}$로 안정화될 때까지의 시간($\ge 100\text{ms}$) 측정.
4. I2S 클록 송출 후 `AMP_PDN`이 HIGH로 천이하는 선후관계 타이밍을 캡처하여 저장.
5. 합격 기준: 시퀀싱 순서(3.3V $\rightarrow$ BOOST $\rightarrow$ I2S $\rightarrow$ PDN) 100% 준수, 오버슈트 $\le 13.5\text{V}$.

---

## 2. [TP-02] VBUS 전압 강하 및 10W 전력 제한 계측 절차

### 2.1 계측 장비 세팅
* 4.5 Digit DMM: USB-C VBUS 입력단자 양단 전압 측정.
* DMM 또는 마이크로볼트미터: `R_SHUNT1` (50mΩ) Kelvin 패드 양단 전압 측정.
* 16Ω 무유도 방열 더미 부하 체결.

### 2.2 실행 절차
1. USB 전원 투입 후 대기 상태(Idle) 전력 계측: $P_{\text{idle}} = V_{\text{vbus}} \times (V_{\text{shunt}} / 0.05\Omega)$.
2. START 명령으로 진동 세기를 0.1부터 0.5(최대)까지 0.1 단위로 증가.
3. 각 단계에서 VBUS 전압 및 입력 전류($I_{\text{in}}$)를 기록하여 총 소비전력 계산 ($P = V \times I$).
4. 합격 기준: 최대 진동 시 $P_{\text{total}} \le 10.0\text{W}$, $I_{\text{peak}} \le 2.0\text{A}$, $V_{\text{vbus}} \ge 4.50\text{V}$.

---

## 3. [TP-03] BTL 차동 출력 및 유도성 역기전력 계측 절차

### 3.1 계측 장비 세팅 (차동 프로빙)
* 고전압 차동 프로브 체결: (+) 단자를 `TP_OUTA`, (-) 단자를 `TP_OUTB`에 체결.
* (차동 프로브 미보유 시 대안): Ch1과 Ch2 프로브 접지 클립을 오직 기판 `TP_GND`에만 물리고, Math `Ch1 - Ch2` 모드 활성화.
* 부하: TEAX14C02-8 실물 익사이터 체결.

### 3.2 실행 절차
1. 48kHz 정현파(진동 주파수 45Hz)를 인가하여 BTL 차동 전압 파형 관측.
2. 진동 최대 상태에서 긴급 정지(ESTOP 명령 또는 USB 케이블 급탈착) 실행.
3. 싱글 샷 트리거로 차단 순간의 역기전력 전압 스파이크($V_{\text{spike}}$) 캡처.
4. 합격 기준: 과도 전압 스파이크가 TAS5805M 내압($\text{PVDD} + 0.3\text{V} = 12.42\text{V}$)을 초과하지 않고 스너버에 의해 감쇄될 것.

---

## 4. [TP-04] 30분 열 포화 및 표면 온도 계측 절차

1. 주변 온도 $25^\circ\text{C}$ 실내 무풍 환경에서 보드를 하우징 내부에 장착.
2. 45Hz 최대 진동 모드로 30분 연속 운전 시작.
3. 적외선 온도계를 사용하여 5분 간격으로 주요 발열 소자 표면 온도 측정:
   - MP3426 (U3), SWPA/MWPA 인덕터 (L1), SS34 다이오드 (D3), TAS5805M (U4), AP2112K (U2).
4. 합격 기준: 30분 포화 시 모든 IC 및 인덕터 표면 온도 $\le 70^\circ\text{C}$, 하우징 외벽 $\le 40^\circ\text{C}$.
