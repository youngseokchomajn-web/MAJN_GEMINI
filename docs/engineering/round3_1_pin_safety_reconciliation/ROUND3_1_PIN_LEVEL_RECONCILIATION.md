# MAJN Round 3.1 — Pin-Level & Safety Baseline Verification Report
## 제3.1차 핀 레벨 회로 정합 및 영아 안전 기준선 재검증 보고서

- **문서 식별자**: `MAJN-R3.1-PIN-SAFETY-RECONCILIATION-001`
- **검토 일자**: 2026-11-06
- **주관 검토자**: Antigravity (독립 기술 검토자 / Independent Investigation Worker)
- **수신**: Chief Authority (최종 설계 승인자)
- **참조**: OpenCode Astra (주 개발 에이전트)
- **기준 형상**: Commit `e5a8f78`
- **작업 원칙**: STRICT READ-ONLY / EVIDENCE-BASED AUDIT / HARD FACT CITATION

---

## 1. 개요 및 배경 (Executive Summary & Background)

Round 3 비판적 반론 보고서(`e5a8f78`)는 6.93W RMS의 산술 절사 오류를 공식 기각하고, 소프트웨어 -3.5dBFS 설정을 하드웨어 클램프로 취급하지 않으며, 과거 TP-01~10 식별자 체계를 복원하고 CI 검증 도구의 구조적 결함을 공론화하는 등 중요한 공학적 기여를 달성하였습니다.

그러나 Round 3 산출물에 대한 전수 정밀 감사를 수행한 결과, **아직 검증되지 않은 수치(1.89W, 4.03W, AAP 50dBA, 0.15g)가 새로운 공식 기준선처럼 서술**되었고, 특히 **TI TAS5805M의 핀 번호를 잘못 기재(Pin 1을 FAULTz로 명시)하는 치명적인 회로 결함**이 적발되었습니다.

이에 따라 Chief Authority(최종 설계 승인자)의 지침에 의거하여 다음을 확정합니다:
1. **Round 3 산출물의 방향성은 채택하되, 결재 요청 3건은 모두 보류(HOLD) 또는 기각(DISAPPROVED)**한다.
2. 하드웨어 회로도 및 펌웨어 변경을 착수하기 전에, **Round 3.1 — Pin-Level & Safety Baseline Verification**을 통해 틀린 기준선을 제거하고 실측과 데이터시트에 기반한 무결한 공학적 기준선을 수립한다.
3. 본 검증은 **엄격한 읽기 전용(Strict Read-Only)** 원칙 하에 수행되며, 원본 회로도(`.json`, `.epro2`), PCB, 거버, BOM, 펌웨어 소스는 일체 수정하지 않는다.

---

## 2. TAS5805M 핀 레벨 재검증 (TAS5805M Pin-Level Verification)

### 2.1 Round 3 보고서의 Pin 1 오기 적발 및 TI 공식 데이터시트 대조

Round 3 보고서([`ROUND3_CRITICAL_CLAIMS_CHALLENGE.md` L173](file:///Users/youngseok/Desktop/majn/docs/engineering/round3_claims_challenge/ROUND3_CRITICAL_CLAIMS_CHALLENGE.md#L173), L180 및 [`GPIO_SIGNAL_ROLE_RECONCILIATION.csv` L2, L7](file:///Users/youngseok/Desktop/majn/docs/engineering/round3_claims_challenge/GPIO_SIGNAL_ROLE_RECONCILIATION.csv#L2))는 다음과 같이 기술하였습니다:
> - TAS5805M Pin 12 = `PDN`
> - TAS5805M Pin 1 = `FAULTz` (Active-LOW Open-Drain Fault Output)

그러나 Texas Instruments의 TAS5805M 공식 데이터시트(SLVSEH8B) 핀 기능표(Pin Functions)와 대조한 결과는 정반대입니다:

| 신호 명칭 | 데이터시트 실제 핀 | 타입 | 공식 기능 설명 (TI SLVSEH8B) | Round 3 왜곡 표기 |
| :--- | :---: | :---: | :--- | :--- |
| **DGND** | **Pin 1** | Ground | **디지털 접지 (Digital Ground)**. 칩 내부 디지털 로직 기준 전위. | Pin 1 = FAULTz (오류!) |
| **DVDD** | **Pin 2** | Power | 디지털 전원 입력 (3.0V ~ 3.6V, 공칭 3.3V). | 누락 |
| **ADR/FAULT** | **Pin 3** | I/O | **기동 시 I²C 주소 설정 입력 / 동작 중 FAULT 출력**. | 누락 / Pin 1과 혼동 |
| **PDN** | **Pin 12** | Input | **전원 차단 제어 입력 (Active-LOW)**. High = 정상 동작, Low = 완전 셧다운. | Pin 12 = PDN (일치) |

```
[치명적 단락 파괴 위험 분석]
  - TAS5805M Pin 1은 내부 디지털 로직 접지(DGND) 및 방열 패드(EP, Pin 29)와 직결되는 기판 접지면입니다.
  - Round 3의 제안대로 GPIO35(10kΩ 풀업) 또는 GPIO13(출력 버퍼)을 Pin 1에 연결할 경우:
    1) GPIO35 연결 시: 3.3V 전원이 10kΩ 저항을 통해 접지로 상시 흘러 신호선이 영구 0V(상시 결함 감지)로 고착됨.
    2) GPIO13 연결 시: MCU가 PDN HIGH(3.3V)를 구동하는 순간 MCU 내부 푸시풀 High-side FET와 DGND 간에
       직접 단락(Dead Short-Circuit)이 발생하여 ESP32 출력 포트가 영구 소손됨.
```

따라서 Round 3의 **"Pin 1 = FAULTz" 주장은 완전히 기각**되며, 공식 회로 연결점은 **Pin 3 (`ADR/FAULT`)**으로 영구 정정합니다.

---

### 2.2 Pin 3 (ADR/FAULT)의 이중 동작 메커니즘 및 필수 회로 요건

TI TAS5805M 데이터시트에 의거, Pin 3은 전원 인가 시점과 런타임에 서로 다른 기능을 수행하는 다중화 핀입니다:

1. **기동 시퀀스 (I²C 주소 결정 단계)**:
   - 전원 투입(POR) 및 PDN 상승 에지 시점에서 내부 ADC가 Pin 3에 연결된 저항 값을 샘플링하여 7비트 I²C 슬레이브 주소를 결정함 (Table 7-5):
     - **$4.7\,\text{k}\Omega$ 풀업 (to DVDD 3.3V)**: 주소 **`0x2C`** (`0101100b`) — MAJN 하드웨어 표준
     - **$15\,\text{k}\Omega$ 풀업 (to DVDD 3.3V)**: 주소 **`0x2D`** (`0101101b`)
     - **$47\,\text{k}\Omega$ 풀업 (to DVDD 3.3V)**: 주소 **`0x2E`** (`0101110b`)
     - **$120\,\text{k}\Omega$ 풀업 (to DVDD 3.3V)**: 주소 **`0x2F`** (`0101111b`)
2. **런타임 동작 (FAULT 출력 전환 단계)**:
   - 주소 래치가 완료된 후, 펌웨어가 I²C 버스를 통해 특정 제어 레지스터를 재정의해야만 비로소 Pin 3이 FAULT 출력 단자로 활성화됨:
     - **Step 1**: Book 0, Page 0 이동 (`0x00 = 0x00`, `0x7F = 0x00`)
     - **Step 2**: Register **`0x61`** (`ADR_PIN_CONFIG`)에 **`0x0B`** 기입
     - **Step 3**: Register **`0x60`** (`ADR_PIN_CTRL`)에 **`0x01`** 기입
     - **Step 4**: Register **`0x78`** (`FAULT_CLEAR`)에 **`0x80`** 기입하여 이전 래치 플래그 소거
3. **전기적 출력 사양**:
   - FAULT 출력 모드에서 Pin 3은 **오픈 드레인(Open-Drain), Active-LOW**로 동작함.
   - 결함이 없을 때: High-Z 상태를 유지하며 외부 풀업 저항(R12, 4.7kΩ)에 의해 3.3V로 풀업됨.
   - 결함 발생 시(과열 경고/차단 OTW/OTE, 과전류 OCP, DC 검출, 클록 결함): 내부 NMOS FET가 턴온되어 라인을 0V(GND)로 강제 인하함.
4. **외장 풀업 저항 상호 운용성**:
   - 주소 결정을 위해 기판에 실장되는 R12(4.7kΩ)가 런타임에는 오픈드레인 FAULT 라인의 풀업 저항 역할을 겸비하므로, **추가적인 외장 풀업 저항 실장 없이 완벽히 동작**함.

---

### 2.3 실제 EasyEDA 넷리스트 및 기판 연결 추적

작업공간 내 원본 회로도 넷리스트(`sch_netlist_final.json`) 및 PCB 넷리스트(`monogpt_pcb_review/1차_설계원본확인/C_netlist_pcb_2026-06-20.json`)를 정밀 파싱한 결과:

- **U4 (TAS5805MPWPR)**:
  - `Pin 1 (DGND)`: Net = `GND` (정상 접지 연결)
  - `Pin 2 (DVDD)`: Net = `VCC_3V3`
  - `Pin 3 (ADR/FAULT#)`: Net = `GND` (※ 구 회로도에서 0V 체결로 0x2C 주소 오류를 겪은 후, 실물 보드에서 R12 4.7kΩ 풀업으로 개조된 이력 확인)
  - `Pin 12 (PDN#)`: Net = `AMP_PDN`
- **U1 (ESP32-WROOM-32E-N8 / 실물 32UE-N8)**:
  - `Pin 16 (IO13)`: Net = `""` (**완전 미할당 Free 핀 / NC**)
  - `Pin 23 (IO15)`: Net = `AMP_PDN` (**TAS5805M Pin 12와 직결됨**)
  - `Pin 7 (IO35)`: Net = `""` (**완전 미할당 Free 핀 / NC**)

이 실사 결과는 다음을 입증합니다:
1. 현재 원본 회로도 상에서 GPIO13과 GPIO35는 아직 회로가 연결되지 않은 미할당(NC) 상태입니다.
2. 현재 PCB #0005 실물 배선은 GPIO15가 U4 Pin 12(PDN)에 연결되어 있습니다.
3. 따라서 GPIO13(PDN)과 GPIO35(Pin 3 FAULT) 배정은 개념적으로 완전히 타당하나, **실제 넷리스트가 변경되기 전까지는 승인할 수 없으며 "후보(Candidate)" 상태로 유지**되어야 합니다.

---

## 3. ESP32 핀 배정 재검증 (ESP32 Pin Allocation Verification)

ESP32-WROOM-32UE 공식 모듈 데이터시트 및 하드웨어 설계 가이드라인을 기준으로 주요 핀의 물리적 특성을 대조한 결과는 다음과 같습니다:

```
========================================================================================
[ESP32 핵심 핀 물리적 특성 및 하드웨어 제약]
  1. GPIO13 (Module Pin 16 / MTCK):
     - 입출력: 양방향 일반 GPIO (Bidirectional Digital IO)
     - 스트래핑: 비-스트래핑 핀 (부팅 동작에 전혀 영향 없음)
     - 리셋 초기: 내부 약한 풀다운 (Weak Pulldown)
     - 외장 요건: 10kΩ 풀다운 저항 (R13 to GND)
     - 판정: AMP_PDN 출력용 최우선 1순위 후보

  2. GPIO15 (Module Pin 23 / MTDO):
     - 입출력: 양방향 GPIO + 고위험 부트 스트래핑 핀 (MTDO)
     - 스트래핑: 부팅 순간 LOW 유지 시 Silent Boot (ROM 디버그 억제 및 정상 플래시 동작)
                 부팅 순간 HIGH 인가 시 UART0 디버그 로그 방출 및 SDIO 전압 왜곡 위험
     - PCB #0005: R13(10kΩ 풀업 to 3.3V)이 실장되어 부팅 시 강제 HIGH 인가됨 (치명적 결함)
     - 판정: TAS5805M Pin 12에서 무조건 분리(Decoupling) 필수

  3. GPIO35 (Module Pin 7 / SENSOR_CAPE / GPI35):
     - 입출력: 입력 전용 (Input-Only GPI, 출력 버퍼 없음)
     - 스트래핑: 비-스트래핑 핀
     - 내부 풀: 내부 풀업 및 내부 풀다운 회로가 실리콘 레벨에서 전무 (No Internal Pulls)
     - 외장 요건: 반드시 외부 풀업 저항(R12, 4.7kΩ to 3.3V)에 의존해야 함
     - 연결 대상: TAS5805M Pin 3 (ADR/FAULT)에 직결
     - 판정: 오픈드레인 결함 신호 감시용 최우선 입력 후보 (MCU 출력 충돌 위험 원천 배제)
========================================================================================
```

### 3.1 펌웨어 매크로 불일치 실태

현재 작업공간 내 펌웨어 소스코드([`인증준비/firmware/src/amplifier_manager.h` L6](file:///Users/youngseok/Desktop/majn/인증준비/firmware/src/amplifier_manager.h#L6))에는 다음 매크로가 여전히 남아 있습니다:
```c
#define PIN_AMP_PDN 15
```
또한 `tas5805m.cpp` 및 `main.cpp` 어디에도 GPIO35를 통한 외부 인터럽트(ISR) 처리 루틴이 구현되어 있지 않으며, 현재 펌웨어는 I²C 레지스터 `0x70~0x73` 폴링을 통해서만 진단을 수행하고 있습니다.

따라서 하드웨어 회로도 변경(Netlist Update)과 펌웨어 소스코드(`PIN_AMP_PDN 13` 반영 및 Pin 3 FAULT ISR 구현)가 동시에 승인되는 Gate G3 시점까지 본 배정안의 최종 승인을 보류합니다.

---

## 4. 전력 예산 재검증 (Power Budget Recalculation & Sensitivity)

Round 3에서 제시된 수식은 다음과 같습니다:
$$V_{\mathrm{RMS}} = \frac{11.0 \times 0.5}{\sqrt{2}} = 3.89\text{V}$$
$$P_{\mathrm{audio}} = 2 \times \frac{3.89^2}{16} = 1.89\text{W}$$
$$P_{\mathrm{sys}} = \frac{1.89 / 0.80 + 0.24}{0.83} + 0.90 \approx 4.03\text{W}$$

산술 연산 자체는 정합하지만, 본 연산의 기저에 깔린 **7대 공학적 가정이 하드웨어 실측으로 입증되지 않은 모델링 추정치**임을 밝힙니다.

### 4.1 7대 핵심 매개변수 실사 및 민감도 분석 (Sensitivity Analysis)

| 매개변수 | 가정치 | 출처 및 공학적 한계 | 민감도 분석 범위 | 전력 영향도 및 위험 분석 |
| :--- | :---: | :--- | :---: | :--- |
| **출력 피크 전압 ($V_{\mathrm{pk}}$)** | **11.0V** | PVDD 12V 대비 1.0V 드룹 가정. FET RDSon(0.27Ω) 및 페라이트 비드 강하 반영. | $10.5\text{V} \sim 11.5\text{V}$ | $P_{\mathrm{audio}} = 1.72\text{W} \sim 2.06\text{W}$ ($P_{\mathrm{sys}} = 3.83\text{W} \sim 4.22\text{W}$). 12V 전원 리플에 종속적. |
| **펌웨어 감쇠 계수 (`scale`)** | **0.50** | 사인파 생성 루틴의 소수점 곱셈 계수 (-6.0dBFS). **하드웨어 인터록 아님.** | $0.10 \sim 1.00$ (Full) | **치명적 위험**: 코드 예외로 scale=1.00 인가 시 $P_{\mathrm{audio}} = 7.56\text{W}$, **$P_{\mathrm{sys}} = 12.57\text{W}$로 10W USB 전원 즉각 붕괴**. |
| **Class-D 앰프 효율 ($\eta_{\mathrm{amp}}$)** | **80.0%** | 저출력 동작 가정. TAS5805M 데이터시트상 90%는 15W 이상에서만 달성됨. | $70.0\% \sim 85.0\%$ | 채널당 1W 저출력 구동 시 스위칭 손실로 효율 70% 하락 시 $P_{\mathrm{sys}} = 4.43\text{W}$로 상승. |
| **MP3426 부스트 효율 ($\eta_{\mathrm{boost}}$)** | **83.0%** | 상온 무풍 조건 대비 열화 반영 가정. | $80.0\% \sim 88.0\%$ | 밀폐 하우징(40°C) 및 $V_{\mathrm{in}}=4.5\text{V}$ 저전압 시 인덕터 DCR/다이오드 열화로 효율 80% 하락 시 $P_{\mathrm{sys}} = 4.14\text{W}$. |
| **앰프 무신호 손실 ($P_{q,\mathrm{amp}}$)** | **0.24W** | TAS5805M 384kHz BD 모드 무신호 전류 ($20\text{mA} \times 12\text{V}$). | $0.20\text{W} \sim 0.36\text{W}$ | 768kHz 스위칭 주파수 설정 시 무신호 전류 30mA ($0.36\text{W}$)로 상승. |
| **ESP32 + LDO 소비전력 ($P_{\mathrm{MCU}}$)** | **0.90W** | 평상시 평균 $180\text{mA} \times 5.0\text{V}$ 가정. | $0.60\text{W} \sim 2.00\text{W}$ | Wi-Fi 802.11b TX 패킷 전송 순간 피크 전류 $380\sim 500\text{mA}$ ($1.9\text{W} \sim 2.5\text{W}$) 발생. |
| **진동자 임피던스 ($Z_{\mathrm{load}}$)** | **16.0Ω** | 8Ω 진동자 2개 직렬 공칭 임피던스. 순수 저항 부하 가정. | $4.0\Omega \sim 35.0\Omega$ | **임피던스는 주파수 함수**: 공진 시 $>30\Omega$이나 병렬 결선(4Ω) 또는 오결선 시 전력 4배 폭증 ($P_{\mathrm{sys}} > 12\text{W}$). |

### 4.2 실제 4개 진동자의 유도성 및 주파수 종속 임피던스 특성

MAJN에 탑재되는 **Tectonic TEAX14C02-8**은 순수 저항이 아니라 가동 보이스코일을 갖는 전기음향 트랜스듀서입니다:
- 단품 직류 저항(DCR bare): $10.8\,\Omega \pm 5\%$
- 채널당 2개 직렬 결선 시 직류 저항: $21.6\,\Omega$ (하네스 배선 저항 포함 시 약 $23.2\,\Omega$)
- 보이스코일 인덕턴스: $L \approx 0.18\,\text{mH} \times 2 = 0.36\,\text{mH}$
- 배시넷 구조체 부착 시 기계적 공진 주파수($f_s \approx 80\sim 150\,\text{Hz}$) 대역에서 임피던스는 **$30\,\Omega \sim 50\,\Omega$까지 상승**하여 실제 오디오 전류 소비를 감소시키는 반면, 고주파 백색소음 재생 시에는 복소 리액턴스로 인해 무효 전력이 증가합니다.

### 4.3 전력 기준선에 대한 공식 판정

- **6.93W RMS**: 산술 절사 오류 및 VBUS 초과로 **영구 기각 (REJECTED)**.
- **1.89W RMS**: 특정 가정($11\text{V}$, scale 0.5, $16\Omega$) 하의 **계산 모델값 (MODEL ESTIMATE)**.
- **4.03W 시스템 입력**: 특정 효율 가정 하의 **추정치 (MODEL ESTIMATE)**.
- **1.8W ~ 2.5W RMS**: 실측 전까지 **미검증 잠정 엔지니어링 목표 (PENDING BENCH TEST)**.
- **공식 기준선 승인 여부**: 4.03W 및 1.89W를 MAJN의 공식 기준선으로 승인하지 않으며, 실물 벤치 계측(TP-02) 데이터 확보 전까지 **HOLD**를 유지함.

---

## 5. 영아 안전 기준 문헌 재검증 (Infant Safety Baseline Reconciliation)

### 5.1 AAP 50dBA 음압 기준의 원문 규명

Round 3 보고서는 "미국소아과학회(AAP)가 신생아 수면 기기에 대해 50dBA를 공식 권고한다"고 주장하였습니다. 그러나 원전 문헌을 면밀히 대조한 결과는 다음과 같습니다:

1. **Hugh et al. (Pediatrics 2014; 133(4): e862-e868)**:
   - 14종의 시판 영아 수면 기기(Infant Sleep Machines)를 30cm, 100cm, 200cm 거리에서 음압을 실측한 연구임.
   - 본 논문에서 인용한 50dBA는 **1997년 AAP 환경보건위원회(Committee on Environmental Health)가 권고한 병원 신생아실(Hospital Nursery) 및 신생아 집중치료실(NICU)의 지속 환경 소음 허용치**임.
   - 본 논문은 시판 기기들이 최대 볼륨에서 85dBA를 초과하여 청각 위험을 초래할 수 있음을 경고하였을 뿐, 민간 제품에 대한 일률적인 공인 인증 상한선을 제정한 것이 아님.
2. **2023 AAP 정책 보고서 (Pediatrics 2022; 150(1): e2022057990)**:
   - 영아 수면 기기 사용 시 "아기 귀로부터 가능한 멀리(최소 30cm 이상) 둘 것, 가장 낮은 볼륨으로 설정할 것, 사용 시간을 제한할 것"을 가이드라인으로 제시함.
3. **공학적 기준선 정립**:
   - **50.0dBA**: 공인 AAP 제품 인증 기준이 아니라, **"병원 신생아실 환경 가이드라인을 준용한 내부 30cm 음향 설계 목표 후보(Internal Engineering Target Candidate)"**로 공식 명칭을 정정함.
   - **65.0dBA**: 명확한 노출 시간 및 임상 출처가 확인되기 전까지 **미승인(Pending Clinical Validation)**으로 관리함.
   - **75.0dBA**: 영아 청각 유모세포 손상 위험으로 **영구 기각(PERMANENTLY REJECTED)**을 확정함.

---

### 5.2 Kimura 2017 논문 원문 대조 및 진동 기준 오류 정정

Round 3는 선행 보고서가 Kimura 2017의 0.5Hz 주파수를 0.5g 가속도로 오독한 오류를 적발한 점은 훌륭했으나, 그 대안으로 제시한 "10~15µm 미세 진동 및 0.15g" 역시 문헌적·수학적 비약이 존재합니다:

1. **Kimura et al. (2017) 논문 원문 실사**:
   - 연구 대상: 거시적 침대 요동(Rocking motion)이 수면에 미치는 영향.
   - 실험 조건: **주파수 $f = 0.5\,\text{Hz}$** (분당 30회 요람 흔들림), **변위 진폭 $A = 2.4\,\text{mm}$ 및 $7.5\,\text{mm}$**의 밀리미터 단위 기계 운동임.
   - 논문 본문 어디에도 $10\mu\text{m} \sim 15\mu\text{m}$라는 마이크로미터 단위 미세 진동은 언급되지 않음.
2. **조화 진동 변위-가속도 변환 수식 검증**:
   $$a_{\mathrm{peak}} = (2\pi f)^2 A, \quad a_{\mathrm{RMS}} = \frac{a_{\mathrm{peak}}}{\sqrt{2}}$$
   - **조건 A ($f = 0.5\,\text{Hz}$, $A = 15\,\mu\text{m}$)**:
     $$a_{\mathrm{peak}} = (2\pi \times 0.5)^2 \times 15 \times 10^{-6} = 1.48 \times 10^{-4}\,\text{m/s}^2 \approx \mathbf{0.000015\,\text{g}}$$
     (0.15g와 10,000배 차이 발생!)
   - **조건 B ($f = 45\,\text{Hz}$ 음향 진동, $A = 15\,\mu\text{m}$)**:
     $$a_{\mathrm{peak}} = (2\pi \times 45)^2 \times 15 \times 10^{-6} = 79943 \times 15 \times 10^{-6} \approx 1.20\,\text{m/s}^2 \approx \mathbf{0.122\,\text{g}_{\mathrm{peak}}}$$
     $$a_{\mathrm{RMS}} = \frac{0.122\,\text{g}}{\sqrt{2}} \approx \mathbf{0.086\,\text{g}_{\mathrm{RMS}}}$$
   - **조건 C ($f = 45\,\text{Hz}$, $a_{\mathrm{peak}} = 0.15\,\text{g} \approx 1.47\,\text{m/s}^2$)**:
     $$A = \frac{1.47}{(2\pi \times 45)^2} \approx \mathbf{18.4\,\mu\text{m}}$$
3. **판정 및 시정 조치**:
   - 0.15g는 10~15µm 또는 Kimura 2017 논문에서 자동으로 유도되는 상수가 아닙니다.
   - 따라서 **0.15g 진동 기준은 승인 보류**하며, 다음 4대 파라미터가 명시된 시험 규격으로 **전면 재정의(Pending Redefinition)**합니다:
     1) 진동 유형: 0.5Hz 거시적 요람 흔들림 vs 45Hz 보이스코일 음향 진동
     2) 물리량: 변위(µm), 주파수(Hz), 가속도(g)
     3) 신호 표기: 피크(Peak) vs 실효치(RMS)
     4) 부하 조건: 무부하 매트리스 vs 5kg 영아 더미 인체 탑승 상태

---

### 5.3 1.5g 비상 충격 차단 임계값 재검증

- 출처: 초기 개발자 메모([`docs/FAULT_MATRIX.md` L12](file:///Users/youngseok/Desktop/majn/docs/FAULT_MATRIX.md#L12))의 임의 가설.
- 한계: 영아의 강한 기침, 뒤척임, 또는 부모가 기저귀를 갈기 위해 배시넷 프레임을 건드리는 일상 충격으로도 PCB 실장 IMU는 순간 1.5g를 초과할 수 있어 빈번한 오작동 셧다운(False Trigger)을 유발함.
- 판정: 공식 안전 기준선에서 배제하고 **`UNSUPPORTED_DEVELOPER_HEURISTIC`**으로 격하함. 실물 더미 낙하 및 동적 진동 시험을 통해 재수립할 것.

---

## 6. AP2112K LDO 실체 확인 및 열적 적합성 구분

- **부품 실체 교차 검증**:
  - 원본 BOM([`BOM_PCB1_revB_2026-07-09.csv` L17](file:///Users/youngseok/Desktop/majn/monogpt_pcb_review/3차_제작데이터/BOM_PCB1_revB_2026-07-09.csv#L17)): `AP2112K-3.3TRG1, U2, SOT-25-5, C51118`
  - Diodes Incorporated 공식 정격: 최대 출력 전류 **600mA**, 전압 강하(Dropout) **250mV @ 600mA**.
  - 과거 보고서에서 180mA급 ME6211로 기재했던 것은 문서 오류였으며, 실물 부품은 600mA급 AP2112K임이 최종 확인됨.
- **부품 실체 vs 열적 적합성의 엄격한 분리**:
  - 600mA 정격 부품이라고 해서 열적 검증이 끝난 것은 아닙니다.
  - SOT-25(SOT-23-5) 패키지의 접합부 열저항은 $\theta_{\mathrm{JA}} \approx 169^\circ\text{C/W}$입니다.
  - 전력 손실: $P_{\mathrm{diss}} = (5.0\text{V} - 3.3\text{V}) \times I_{\mathrm{LDO}} = 1.7\text{V} \times I_{\mathrm{LDO}}$
    - 평상시 ($I_{\mathrm{avg}} \approx 120\text{mA}$): $P = 0.204\text{W} \implies \Delta T \approx 34.5^\circ\text{C}$ ($40^\circ\text{C}$ 챔버 시 $T_j \approx 74.5^\circ\text{C}$, 안전)
    - Wi-Fi 스트리밍 ($I_{\mathrm{avg}} \approx 240\text{mA}$): $P = 0.408\text{W} \implies \Delta T \approx 69.0^\circ\text{C}$ ($40^\circ\text{C}$ 챔버 시 $T_j \approx 109.0^\circ\text{C}$, $125^\circ\text{C}$ 한계 접근)
    - Wi-Fi 연속 송신 피크 ($I_{\mathrm{peak}} \approx 450\text{mA}$): $P = 0.765\text{W} \implies$ 과열 위험.
- **판정 및 조치**:
  - 현 단계에서 SOT-89 패키지나 SY8088 벅 컨버터로의 교체를 단정하는 것은 **시기상조(Premature)**임.
  - AP2112K의 존치 여부는 실제 PCB 방열 구리 면적과 밀폐 하우징 상태에서의 **실측 표면 온도(TP-08)를 측정한 후 최종 확정**함.

---

## 7. TP-01~10 계측 규격 합격 기준 위계 재분류 (Reclassified TP Matrix)

10대 표준 계측 규격의 수치들을 단일 합격선이 아닌 엄격한 공학적 위계로 재분류하였습니다 ([`TP_ACCEPTANCE_CRITERIA_SOURCE_MATRIX.csv`](file:///Users/youngseok/Desktop/majn/docs/engineering/round3_1_pin_safety_reconciliation/TP_ACCEPTANCE_CRITERIA_SOURCE_MATRIX.csv) 참조):

```
========================================================================================
[TP-01~10 수치 위계 분류 및 안전 계측 프로토콜]

1. TP-01 (PVDD 기동 시퀀싱 & 오버슈트 <= 13.2V):
   - 분류: ENGINEERING_TARGET (12.0V + 10% 공학적 마진)
   - 데이터시트 상한: TAS5805M PVDD 권장 상한 26.4V, 절대 최대 30.0V
   - 안전 수칙: PCB TP_GND 기준 10:1 수동 프로브 계측

2. TP-02 (VBUS 전압 강하 >= 4.50V & 총 전력 <= 10.0W):
   - 분류: APPROVED_SYSTEM_REQUIREMENT (USB-IF 규격 및 DOC03 REQ-P0-02)
   - 근거: USB 케이블 손실 후 최저 전압 보장 및 2.0A 벽면 어댑터 OCP 보호

3. TP-03 (BTL 차동 출력 역기전력 서지 <= 14.0V):
   - 분류: ENGINEERING_TARGET / PENDING_BENCH_VALIDATION
   - [초치명적 계측 경고]: 오실로스코프 접지 클립을 OUTA/OUTB에 절대 직접 물리지 말 것!
     H-Bridge 하이사이드 FET 접지 직결 단락으로 앰프 즉각 폭발.
     반드시 고전압 능동 차동 프로브 또는 Math (Ch1 - Ch2) 모드로만 계측할 것.

4. TP-04 (MP3426 SW 노드 링잉 피크 <= 18.0V):
   - 분류: DATASHEET_LIMIT (22.0V Abs Max) / ENGINEERING_TARGET (18.0V, 18.2% 마진)
   - 안전 수칙: 10cm 악어 접지선 사용 금지! 5mm 이하 초단축 동축 스프링 접지팁 필수.

5. TP-05 (부스트 인덕터 동적 피크 전류 <= 2.65A cont / <= 3.10A worst):
   - 분류: DATASHEET_LIMIT (3.6A Isat) / ENGINEERING_TARGET (2.65A 계산값)
   - 판정: 실물 고주파 전류 프로브 삽입 벤치 계측 전까지 PENDING VALIDATION.

6. TP-06 (3.3V LDO Wi-Fi 버스트 전압 강하 <= 100mV, Vmin >= 3.10V):
   - 분류: DATASHEET_LIMIT (ESP32 최저 3.0V) / APPROVED_SYSTEM_REQUIREMENT (100mV 강하)
   - 근거: ESP32 브라운아웃(2.80V) 대비 300mV 이상의 하드웨어 노이즈 마진 확보.

7. TP-07 (USB-C CC 5.1kΩ 로직 & 핫플러그 인러시 <= 5.75V):
   - 분류: DATASHEET_LIMIT (CC 5.1kΩ ±10%) / ENGINEERING_TARGET (5.75V 오버슈트)
   - 근거: USB Type-C 표준 Table 4-36 및 C-to-C 충전기 협상 필수 조건.

8. TP-08 (30분 부품 열 포화: U3<=85°C, U4<=75°C, U2<=70°C, 외벽<=40°C):
   - 분류: APPROVED_SYSTEM_REQUIREMENT (외벽 40°C IEC 62368-1) / ENGINEERING_TARGET (IC 표면)
   - 판정: 밀폐 챔버 60분 열평형 열화상 실측 전까지 PENDING VALIDATION.

9. TP-09 (영아 음압: 평상시 Leq <= 50.0dBA, 최대 Lmax <= 65.0dBA):
   - 분류: ENGINEERING_TARGET (50dBA 내부 목표) / UNSUPPORTED (65dBA) / REJECTED (75dBA)
   - 판정: 50dBA는 내부 시험 목표 후보이며 공인 AAP 규격 아님. 임상 자문 전까지 PENDING.

10. TP-10 (배시넷 표면 진동 a_RMS <= 0.15g, 긴급 정지 지연 <= 100ms):
    - 분류: UNSUPPORTED (0.15g) / ENGINEERING_TARGET (100ms)
    - 판정: 주파수·변위·가속도·영아 탑승 조건 분리 재정의 전까지 PENDING REDEFINITION.
========================================================================================
```

---

## 8. CI 검증 도구 결함 실태 및 강화 조치 (CI Verification Hardening)

본 감사에서 작업공간 내 검증 스크립트 4종의 소스코드를 분석한 결과:
- `tools/majn_circuit_verifier.py` (L113-117)
- `tools/pcb_verification/bom_cpl_comparator.py` (L156-160)
- `tools/pcb_verification/gerber_integrity_checker.py` (L78-81)
- `tools/pcb_verification/requirements_traceability_checker.py` (L93-95)

모든 스크립트에서 치명적 위반, 부품 불일치, 거버 레이어 결함이 발견되더라도 `print()` 문만 실행하고 운영체제 종료 코드 `sys.exit(1)`을 호출하지 않습니다. 결과적으로 **CI 파이프라인에서 도구가 항상 종료 코드 `0 (SUCCESS)`을 반환하여 어떠한 결함 데이터도 빌드를 차단하지 못하는 허점**이 존재합니다.

향후 Gate G1/G2 진행 시 반드시 에러 발생 시 `sys.exit(1)`을 명시적으로 반환하도록 도구 강화(Hardening)를 선행해야 합니다.

---

## 9. 산출물 일람 및 게이트 상태 (Deliverables & Gate Decision)

본 Round 3.1을 통해 작성된 공식 산출물 7종은 다음과 같습니다:

1. [`ROUND3_1_PIN_LEVEL_RECONCILIATION.md`](file:///Users/youngseok/Desktop/majn/docs/engineering/round3_1_pin_safety_reconciliation/ROUND3_1_PIN_LEVEL_RECONCILIATION.md) (본 종합 정합 보고서)
2. [`TAS5805M_ADR_FAULT_AND_PDN_VERIFICATION.csv`](file:///Users/youngseok/Desktop/majn/docs/engineering/round3_1_pin_safety_reconciliation/TAS5805M_ADR_FAULT_AND_PDN_VERIFICATION.csv) (TAS5805M 핀 기능 및 레지스터 요건 검증표)
3. [`ESP32_GPIO_ASSIGNMENT_VERIFICATION.csv`](file:///Users/youngseok/Desktop/majn/docs/engineering/round3_1_pin_safety_reconciliation/ESP32_GPIO_ASSIGNMENT_VERIFICATION.csv) (ESP32 전체 GPIO 스트래핑 및 배정 실사표)
4. [`POWER_BUDGET_ASSUMPTION_RECALCULATION.csv`](file:///Users/youngseok/Desktop/majn/docs/engineering/round3_1_pin_safety_reconciliation/POWER_BUDGET_ASSUMPTION_RECALCULATION.csv) (전력 예산 매개변수 실사 및 민감도 재계산표)
5. [`INFANT_SAFETY_EVIDENCE_RECONCILIATION.csv`](file:///Users/youngseok/Desktop/majn/docs/engineering/round3_1_pin_safety_reconciliation/INFANT_SAFETY_EVIDENCE_RECONCILIATION.csv) (AAP 음압 및 Kimura 진동 문헌 근거 일치화표)
6. [`TP_ACCEPTANCE_CRITERIA_SOURCE_MATRIX.csv`](file:///Users/youngseok/Desktop/majn/docs/engineering/round3_1_pin_safety_reconciliation/TP_ACCEPTANCE_CRITERIA_SOURCE_MATRIX.csv) (10대 표준 계측 규격 합격 기준 위계 매트릭스)
7. [`ROUND3_1_GATE_DECISION.md`](file:///Users/youngseok/Desktop/majn/docs/engineering/round3_1_pin_safety_reconciliation/ROUND3_1_GATE_DECISION.md) (게이트 의결 및 심의 판정서)

**최종 게이트 상태**: **Gate G0 ~ G5 HOLD 전면 유지 / STRICT READ-ONLY 동결 유지**

---

- **검토관**: Antigravity Independent Investigation Worker
- **보고 일시**: 2026-11-06
