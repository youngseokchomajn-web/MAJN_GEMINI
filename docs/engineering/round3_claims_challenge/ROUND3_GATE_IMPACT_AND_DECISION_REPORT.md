# MAJN Round 3 — Gate Impact & Decision Report
## 제3차 게이트 영향 평가 및 엔지니어링 승인 결정 보고서

- **문서 ID**: `MAJN-R3-GATE-DECISION-001`
- **검토 일자**: 2026-11-05
- **검토 주체**: Antigravity (독립 공학 조사관 / Investigation Worker)
- **최종 승인 권한자**: Human Chief Authority (인간 최종 설계 승인자)
- **주 개발 에이전트**: OpenCode Astra
- **근거 산출물**:
  1. `docs/engineering/round3_claims_challenge/ROUND3_CRITICAL_CLAIMS_CHALLENGE.md`
  2. `docs/engineering/round3_claims_challenge/POWER_BUDGET_ERROR_AND_ASSUMPTION_REGISTER.csv`
  3. `docs/engineering/round3_claims_challenge/GPIO_SIGNAL_ROLE_RECONCILIATION.csv`
  4. `docs/engineering/round3_claims_challenge/TP_TEST_ID_AND_ACCEPTANCE_CRITERIA_RECONCILIATION.csv`
  5. `docs/engineering/round3_claims_challenge/SAFETY_LIMITS_SOURCE_VALIDATION.csv`
- **통제 상태**: STRICT READ-ONLY / CAD AND FIRMWARE FREEZE ACTIVE

---

## 1. 개요 및 총괄 결정 (Executive Summary & Decision)

제3차 비판적 반론 감사(Round 3 Critical Claims Challenge) 결과, 커밋 `0f001d0`의 Round 2 보고서가 제안한 핵심 전기 설계 기준선과 안전 수치에는 **명백한 산술 오류, 소프트웨어 감쇠의 물리적 한계 왜곡, 인터페이스 핀 충돌, 문헌 수치 왜곡, 열 계산 오류**가 존재함이 최종 입증되었습니다.

따라서 최고 의사결정권자(Human Chief Authority)에게 전달하는 독립 검토자의 공식 판정은 다음과 같습니다:

```
========================================================================================
[공식 엔지니어링 판정: PCB #0006 착수 및 기준선 승인 전면 보류]
  - Gate G0 (제조 기준선 무결성):      HOLD (유지)
  - Gate G1 (고장 분석 및 FMEA 확정):   HOLD (유지)
  - Gate G2 (전기 설계 요구사항 확정):  HOLD (기각 및 재산정 명령)
  - Gate G3 (회로 상세설계 착수 승인):  HOLD (회로도/CAD 수정 절대 금지 유지)
  - Gate G4 ~ G5 (제조/검증 승인):      HOLD (유지)
  - Gate G6 ~ G8 (인증/양산 릴리스):    NOT_STARTED (유지)
========================================================================================
[절대 작업 통제 명령 (Strict Read-Only Guardrails)]
  - EasyEDA Pro 원본 파일 (.epro2, .json, .sch, .pcb) 수정 일체 불허
  - 제조 거버 파일 및 CPL/BOM 수정 일체 불허
  - 펌웨어 C++ 소스 코드 수정 일체 불허
  - 모든 변경 작업은 Gate G2 미해결 6대 블로커가 완전 해소될 때까지 동결함
========================================================================================
```

---

## 2. Round 2 주요 주장에 대한 명시적 기각 및 승인 결정 사항

Chief Authority가 회로 수정 승인 여부를 판단할 수 있도록, Round 2 주요 주장에 대한 판정을 명확히 확정합니다:

| 주장 항목 | Round 2 보고서 주장 내용 | Round 3 최종 판정 | 상세 공학적 사유 및 근거 |
| :--- | :--- | :--- | :--- |
| **6.93W RMS 연속 출력** | 12V 8.01W 공급 하에 연속 6.93W (채널당 3.46W) 확정 | **DISAPPROVED (기각)** | $(8.01 - 0.24) \times 0.90 = 6.993\text{W}$의 산술 절삭 오류. 저출력 Class-D 효율($80\sim 85\%$) 및 열화 반영 시 실제 연속 안전치는 **$5.1\text{W} \sim 5.9\text{W}$**에 불과함. |
| **-3.5dBFS 하드웨어 클램핑** | DSP 볼륨을 -3.5dBFS로 고정하여 VBUS 붕괴 방지 | **DISAPPROVED (기각)** | I2C 디지털 레지스터 쓰기는 하드웨어 인터록이 아님. 구형파/백색소음(Crest factor 0dB) 인가 시 **출력이 13.5W로 폭증하여 VBUS 즉각 붕괴**. |
| **과도 피크 8.0W 상한 보장** | -3.5dBFS 설정으로 어떠한 신호도 8W를 초과하지 않음 | **DISAPPROVED (기각)** | 신호 진폭, 파고율, 익사이터 임피던스 하강($4\Omega$) 시 출력이 최대 27W까지 도달 가능하여 수학적 근거 완전 결여. |
| **GPIO13 FAULTz 배정** | GPIO13을 TAS5805M FAULTz(결함감지 입력) 후보로 기술 | **DISAPPROVED (기각)** | `AMP_PDN`(MCU 출력, Pin 12, 10k 풀다운)과 정반대 신호. 펌웨어 출력과 앰프 오픈드레인 직결 시 **하드웨어 단락 파괴 유발**. |
| **75dBA @ 10cm 음향 한계** | 소아과학회 소음 권고안에서 유도된 음향 상한선 | **DISAPPROVED (기각)** | 기획서의 경쟁사 모터 소음(65~75dBA) 수치 왜곡. AAP 권고안 원문은 **$\le 50.0\text{dBA}$**임. 75dBA는 신생아 청각 손상 유발. |
| **0.5g 연속 진동 가속도** | Kimura 2017 수면 유도 논문에서 도출된 안전 기준선 | **DISAPPROVED (기각)** | Kimura 논문의 최적 요람 주파수 **0.5Hz** 단위를 가속도 단위(g)로 오독 및 변조한 오류. 실제로는 $10\sim 15\mu\text{m}$ Insensible 미세 진동임. |
| **1.5g @ 100ms 충격 차단** | 의학/물리 안전 기준에 기반한 비상 정지 임계치 | **DEMOTED (가설 강등)** | 초기 개발자 메모(`FAULT_MATRIX.md`)의 자의적 가설. 정상 영아 움직임으로 인한 잦은 오작동 셧다운 위험. 임상/물리 시험 전 채택 불가. |
| **ME6211C33 $70^\circ\text{C}$ 허용** | SOT-23-5 패키지로 표면 온도 $70^\circ\text{C}$ 유지 가능 | **DISAPPROVED (기각)** | $\theta_{\text{JA}} = 250^\circ\text{C/W}$로 인해 상온 평상시 부하에서도 **표면 온도가 $101.5^\circ\text{C}$ 돌파, 밀폐 시 $140^\circ\text{C}$ 초과 소손**. |
| **CI 도구 100% 결함 차단** | 5종 CI 도구가 결함 주입 시 Exit 1로 빌드를 완벽 차단 | **FLAGGED (결함 적발)** | 도구 소스코드에 `sys.exit(1)` 및 유효성 검증 로직 부재. 실제 실행되지 않은 가상 서술 보고서임이 적발됨. |

---

## 3. 전체 게이트(Gate G0 ~ G8) 상세 상태 매트릭스

```mermaid
flowchart LR
    G0["G0: 기준선 복원\n[HOLD]"] --> G1["G1: FMEA 실측\n[HOLD]"]
    G1 --> G2["G2: 전기설계\n[HOLD/REVISE]"]
    G2 --> G3["G3: 회로착수\n[FREEZE]"]
    G3 --> G4["G4: 아트웍/BOM\n[HOLD]"]
    G4 --> G5["G5: 보드검증\n[HOLD]"]
    G5 --> G6["G6: KC/FCC인증\n[NOT_STARTED]"]
```

| 게이트 | 정의 및 마일스톤 | 현재 상태 | 해소되어야 할 선행 필수 증적 (Prerequisites) |
| :--- | :--- | :--- | :--- |
| **Gate G0** | 제조 기준선 무결성 복원 | **HOLD** | 1. 2026-07-09 주문 JLCPCB 공식 인보이스 및 적층 사양서 확인.<br>2. C11 / R12 실물 기판 광학 현미경(50x) 실측 사진 제출. |
| **Gate G1** | 고장 분석 및 FMEA 확정 | **HOLD** | 1. Prototype #0005 실물 벤치 오실로스코프 파형 획득:<br>   - `TP-01`: PVDD 무부하 기동 오버슈트 ($\le 13.2\text{V}$)<br>   - `TP-03`: BTL 차동 역기전력 서지 ($\le 14.0\text{V}$, 차동 프로브 필수)<br>   - `TP-04`: MP3426 SW 노드 링잉 ($\le 18.0\text{V}$)<br>   - `TP-06`: Wi-Fi 송신 시 3.3V LDO 전압 강하 ($\le 100\text{mV}$) |
| **Gate G2** | 전기 설계 요구사항 확정 | **HOLD** | 1. 입력 전원 공급원 사양 및 최대 전류 한계 확정.<br>2. 보수적 연속 음향 전력 포락선($5.1\text{W} \sim 5.9\text{W}$) 공식 승인.<br>3. ME6211 SOT-23-5 발열 문제 해결을 위한 전원단 개정안 확정.<br>4. 영아 안전 기준(AAP 50dBA, 미세 진동 $0.15\text{g}$) 공식 승인. |
| **Gate G3** | 회로 상세설계 착수 승인 | **HOLD (동결)** | 1. Gate G0, G1, G2의 전원 서명 완료.<br>2. Chief Authority의 `GPIO13 -> AMP_PDN` 공식 배정 결재.<br>3. `GPIO35 -> AMP_FAULTz` 분리 배정안 승인.<br>4. 회로도 수정 및 넷리스트 추출 (승인 전까지 CAD 원본 수정 절대 금지). |
| **Gate G4** | PCB 아트웍 및 부품 승인 | **HOLD** | G3 승인 후 4층 동박 레이아웃 DRC 0 Error 및 CPL 100% 매칭 검증. |
| **Gate G5** | 시제품 제조 및 벤치 검증 | **HOLD** | PCB #0006 초도 보드 10대 계측 시험(TP-01~10) 100% PASS. |
| **Gate G6** | 공인 안전 및 전자파 인증 | **NOT_STARTED** | 공인 시험소(KTL/DT&C) KC/FCC 사전 스캔 통과. |
| **Gate G7** | 파일럿 생산 및 신뢰성 | **NOT_STARTED** | 100시간 MTBF 가속 수명 시험 통과. |
| **Gate G8** | 양산 릴리스 (Mass Production) | **NOT_STARTED** | 제조 데이터 최종 릴리스 서명. |

---

## 4. PCB #0006 설계 착수(Gate G3 해제)를 위한 6대 미해결 선결 과제

Chief Authority가 향후 회로도 수정을 승인하기 전에, 주 개발 에이전트(OpenCode Astra)와 하드웨어 팀이 반드시 해결해야 하는 6대 공학적 선결 과제는 다음과 같습니다:

### [과제 1] USB-C 입력 전원단 전류 제한 방식 확정
- 단순 5.1kΩ CC 풀다운 저항만으로는 사용자가 연결하는 5V 전원 어댑터의 용량(500mA ~ 3.0A)을 통제하거나 인지할 수 없음.
- VBUS 전압 모니터링 ADC 분압 회로를 추가하여 전압이 4.60V 이하로 떨어지면 앰프 볼륨을 강제 축소하는 **하드웨어 전압 피드백 루프**를 설계에 포함할 것.

### [과제 2] 3.3V LDO 전원단 열적 재설계 (Thermal Redesign)
- 현행 SOT-23-5 패키지 ME6211C33은 $100^\circ\text{C}$ 이상 과열되어 화재 및 칩 소손 위험이 확실함.
- **조치 방안**:
  - 대안 A: 열저항이 낮은 SOT-89 패키지 LDO($\theta_{\text{JA}} \approx 100^\circ\text{C/W}$)로 교체하고 넓은 방열 동박 확보.
  - 대안 B (권고): 효율 92% 이상의 초소형 동기식 스텝다운 벅 컨버터(예: SY8088, TPS62088)로 변경하여 발열을 $0.05\text{W}$ 이하로 차단.

### [과제 3] GPIO 신호 배정의 공식 확정 및 동기화 결재
- 회로도 넷리스트와 펌웨어 헤더의 인터페이스 충돌을 해소하기 위해 다음 배정안에 대한 최종 결재가 필요함:
  - `GPIO13 (Pin 16)`: **`AMP_PDN`** (MCU Output, 10kΩ Pulldown to GND, TAS5805M Pin 12 연결)
  - `GPIO15 (Pin 23)`: **`MTDO`** (Silent Boot Strapping Pin 전용, 10kΩ Pulldown to GND, 앰프 연결 해제)
  - `GPIO35 (Pin 7)`: **`AMP_FAULTz`** (MCU Input Only, 10kΩ Pullup to 3.3V, TAS5805M Pin 1 연결)

### [과제 4] Prototype #0005 실물 벤치 계측 파형 확보
- 소프트웨어적 논쟁을 종결하기 위해, 실제 보유 중인 Prototype #0005 기판에서 다음 4대 파형 스크린샷과 CSV 데이터를 조속히 획득하여 첨부할 것:
  - `TP-01`: PVDD 무부하 기동 오버슈트
  - `TP-03`: BTL 긴급 차단 역기전력 (차동 프로빙)
  - `TP-04`: MP3426 SW 노드 링잉
  - `TP-06`: Wi-Fi 송신 시 3.3V 전압 강하

### [과제 5] 기구-음향 전달함수 및 실제 영아 안전 수치 도출
- 허위로 판명된 75dBA와 0.5g를 공식 문서에서 전면 삭제하고:
  - 실제 배시넷 프레임에 익사이터를 결합한 상태에서 Class 1 소음계로 매트리스 표면 음압 측정 (목표: $\le 50.0\text{dBA}$).
  - 3축 가속도계로 매트리스 표면 진동 가속도 측정 (목표: Insensible 미세 진동 $a_{\text{RMS}} \le 0.15\text{g}$).

### [과제 6] CI 자동화 검증 스크립트 소스코드 보완
- 검증 도구(`bom_cpl_comparator.py`, `gerber_integrity_checker.py`, `requirements_traceability_checker.py`)에 실제로 불일치 검출 시 파이프라인을 중단시키는 **`sys.exit(1)` 로직을 구현**하고, 실제 임시 복제본에서 결함 주입을 재수행하여 검증의 진실성을 회복할 것.

---

## 5. 최종 결론 및 엔지니어링 서명

본 제3차 감사(Round 3)를 통해 수립된 비판적 반론과 정정 데이터는 MAJN 배시넷 하드웨어가 "검증되지 않은 수치적 환상"에서 벗어나 "철저한 물리 법칙과 영아 생명 안전"에 기반한 견고한 엔지니어링 기준선으로 복귀하도록 이끌 것입니다.

Chief Authority의 추가 승인 서명이 있기 전까지, **전체 프로젝트의 모든 원본 파일은 엄격한 동결(STRICT FREEZE) 상태를 유지**합니다.

```
========================================================================================
검토 일자: 2026-11-05
검토 주체: Antigravity Independent Investigation Worker
게이트 판정: Gate G0 ~ G5 HOLD MAINTAINED / STRICT READ-ONLY ACTIVE
산출물 일체: docs/engineering/round3_claims_challenge/ 6종 완비
========================================================================================
```
