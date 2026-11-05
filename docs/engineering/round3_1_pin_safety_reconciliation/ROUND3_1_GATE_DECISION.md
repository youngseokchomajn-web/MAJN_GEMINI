# MAJN Round 3.1 — Formal Gate Impact & Adjudication Decision Report
## 제3.1차 설계 기준선·핀 레벨 정합 및 게이트 의사결정 판정서

- **문서 ID**: `MAJN-R3.1-GATE-DECISION-001`
- **일자**: 2026-11-06
- **주관 감사자**: Antigravity (독립 기술 검토자 / Independent Investigation Worker)
- **수신**: Chief Authority (최종 설계 승인자)
- **참조**: OpenCode Astra (주 개발 에이전트)
- **현재 형상 기준**: Commit `e5a8f78` (Round 3 비판적 반론 보고서 완료 시점)
- **작업 원칙**: STRICT READ-ONLY / EVIDENCE-BASED AUDIT / GATE FREEZE

---

## 1. 종합 게이트 판정 요약 (Executive Gate Status)

```
========================================================================================
[MAJN Engineering Phase 0 Gate Adjudication — Round 3.1 Decision]
  - Gate G0 (요구사항 및 기준선 동결):   HOLD MAINTAINED (엄격 동결 유지)
  - Gate G1 (개념 및 블록다이어그램):     HOLD MAINTAINED (엄격 동결 유지)
  - Gate G2 (회로도 설계 착수 승인):     HOLD MAINTAINED (설계 변경 착수 보류)
  - Gate G3 (부품 및 넷리스트 확정):     HOLD MAINTAINED (핀 배정 및 넷리스트 미승인)
  - Gate G4 (PCB 레이아웃 및 배선):      HOLD MAINTAINED (배선 작업 절대 금지)
  - Gate G5 (제조 파일 릴리스):          HOLD MAINTAINED (거버/BOM 릴리스 금지)

[결재 안건 심의 결과]
  1. 6.93W RMS 공식 기준선 기각:        동의 및 최종 확정 (FORMALLY DISAPPROVED)
  2. -3.5dBFS 하드웨어 클램프 기각:     동의 및 최종 확정 (FORMALLY DISAPPROVED)
  3. GPIO13 (PDN) / GPIO35 (FAULTz) 배정: 방향성 채택, 공식 승인 보류 (APPROVAL HELD)
  4. 4.03W 시스템 소비전력 기준선:       공식 기준선 승인 보류 (UNVERIFIED MODEL ESTIMATE)
  5. AAP 50dBA 영아 음압 기준선:        공식 제품 규격 승인 보류 (INTERNAL TARGET CANDIDATE)
  6. 0.15g / 10~15µm 진동 기준선:       공식 기준선 승인 보류 (PENDING REDEFINITION)
  7. TP-01~10 마스터 시험 합격 기준:     잠정 공학 목표로 분리, 출처 미검증 수치 기준선 배제
========================================================================================
```

---

## 2. 결재 요청 안건별 정밀 심의 및 의결 내역

### 2.1 안건 1: 6.93W RMS 공식 전력 기준선 기각 건
- **심의 결과**: **동의 (FORMALLY DISAPPROVED / PERMANENTLY REJECTED)**
- **공학적 근거**:
  1. $P_{\text{audio}} = (8.01 - 0.24) \times 0.90 = 6.993\text{W}$ 연산 과정에서 발생한 산술 절사 오류(Truncation Bug)가 확인됨.
  2. $90\%$ Class-D 효율은 $15\text{W} \sim 20\text{W}$ 고출력 동작 조건에서만 달성되며, 채널당 $1\text{W} \sim 2\text{W}$ 저출력 구동 시 실제 효율은 $75\% \sim 82\%$로 급락함.
  3. $6.93\text{W}$ 연속 음향 출력 시 요구되는 1차측 VBUS 입력 전력은 $10.75\text{W} \sim 11.50\text{W}$ ($5\text{V}/2.15\text{A} \sim 2.30\text{A}$)에 달하여 USB Type-C 5V 2.0A (10.0W) 공급 상한을 즉각 초과함.
  4. 따라서 6.93W는 MAJN의 공식 음향 출력 기준선에서 영구 제명함.

---

### 2.2 안건 2: -3.5dBFS DSP 레지스터 감쇠의 하드웨어 클램프 승인 기각 건
- **심의 결과**: **동의 (FORMALLY DISAPPROVED / PERMANENTLY REJECTED)**
- **공학적 근거**:
  1. TAS5805M Register `0x4C` (DIG_VOL)는 휘발성 소프트웨어 I2C 레지스터이며, 하드웨어적 전류/전압 제한기(Hardware Interlock)가 아님.
  2. 부팅 과도 구간, I2C 통신 중단, 소프트웨어 예외 발생 시 레지스터 기본값(0dBFS)으로 환원될 위험이 존재함.
  3. Crest Factor가 0dB에 근접하는 구형파, 비정상 클리핑 백색소음, 또는 저주파 임펄스 입력 시 -3.5dBFS 설정 상태에서도 앰프 출력 전력은 **$13.5\text{W} \sim 27\text{W}$**까지 폭증하여 VBUS 붕괴(Brownout)를 초래함.
  4. 제안된 매크로 `0x38`(-4.0dBFS)과 `-3.5dBFS`(`0x37`) 간의 레지스터 매핑 오류도 추가 확인됨.

---

### 2.3 안건 3: GPIO13 (PDN) 및 GPIO35 (FAULTz) 배정 승인 건
- **심의 결과**: **방향성 채택, 공식 설계 승인 보류 (DIRECTION ADOPTED / APPROVAL HELD)**
- **공학적 근거**:
  1. **TAS5805M 핀 오류 정정 확인**: Round 3 보고서의 "Pin 1 = FAULTz" 주장은 치명적 오류이며, TI 공식 데이터시트상 Pin 1은 `DGND`이고 FAULT 기능은 **Pin 3 (`ADR/FAULT`)**임이 확인됨. Pin 1에 MCU 핀을 연결하면 디지털 접지와 직결 단락(Dead Short)됨.
  2. **Pin 3 다중화 및 레지스터 요건 확인**: Pin 3을 FAULT 출력으로 운용하기 위해서는 기동 시 I2C 주소 래치(4.7kΩ to 3.3V) 완료 후 런타임에 Register `0x61 = 0x0B`, `0x60 = 0x01`을 기입하는 소프트웨어 시퀀싱이 필수적임.
  3. **ESP32 핀 특성 확인**:
     - `GPIO13 (Pin 16)`: 비-스트래핑 핀, 리셋 기본값 약한 풀다운, PDN 구동용 최적 후보.
     - `GPIO15 (Pin 23)`: MTDO 스트래핑 핀. PCB #0005의 R13(10kΩ 풀업 to 3.3V) 결선으로 인해 부팅 트랩 및 퍽 소음 유발이 입증되어 분리(Decoupling) 필수.
     - `GPIO35 (Pin 7)`: 입력 전용(GPI) 핀, 내부 풀업/풀다운 회로 없음. 외부 4.7kΩ 풀업(R12)을 갖는 TAS5805M Pin 3(오픈드레인 출력) 감시용으로 전기적으로 적합.
  4. **보류 사유**: 현재 작업공간의 회로도 및 넷리스트(`sch_netlist_final.json`)상 GPIO13과 GPIO35는 여전히 미연결(NC) 상태이며, 펌웨어 소스(`amplifier_manager.h`)에는 `#define PIN_AMP_PDN 15`가 하드코딩되어 있음. 실제 회로도 넷리스트 변경과 펌웨어 동기화가 Gate G3에서 패키지로 이루어지기 전에는 승인할 수 없음.

---

### 2.4 안건 4: 4.03W 시스템 소비전력 및 1.8~2.5W 음향 출력 공식 기준선 승인 건
- **심의 결과**: **승인 보류 (UNVERIFIED MODEL ESTIMATE / APPROVAL HELD)**
- **공학적 근거**:
  1. Round 3의 계산식:
     $$V_{\mathrm{RMS}} = \frac{11.0 \times 0.5}{\sqrt{2}} = 3.89\text{V}, \quad P_{\mathrm{audio}} = 2 \times \frac{3.89^2}{16} = 1.89\text{W}$$
     $$P_{\mathrm{sys}} = \frac{1.89 / 0.80 + 0.24}{0.83} + 0.90 \approx 4.03\text{W}$$
  2. 본 연산은 산술적으로는 결함이 없으나, $11.0\text{V}$ 피크 가정, 펌웨어 $0.5$ 감쇠 지속성, Class-D 효율 $80\%$, 부스트 효율 $83\%$, 대기전력 $0.24\text{W}$, MCU 전력 $0.90\text{W}$, 부하 $16\Omega$ 순수 저항 가정이 모두 실험적으로 검증되지 않은 **이상적 모델링 추정치(Model Estimate)**에 불과함.
  3. 특히 진동자(TEAX14C02-8)는 주파수에 따라 임피던스가 극심하게 변동(공진 시 $>30\Omega$, 최소 임피던스 $10\sim 14\Omega$, 하네스 저항 $1.6\Omega$)하므로 고정 $16\Omega$ 저항 모델은 실제 하드웨어 소비전력을 대변할 수 없음.
  4. $1.8\text{W} \sim 2.5\text{W}$ 역시 실측 데이터가 확보될 때까지 잠정 공학 목표(Engineering Target)로 유지하며, 공식 소비전력 기준선 승인을 보류함.

---

### 2.5 안건 5: 영아 안전 음압 기준 (AAP 50dBA) 승인 건
- **심의 결과**: **공식 인증 기준선 승인 보류 / 내부 시험 목표 후보로 한정 (INTERNAL CANDIDATE TARGET)**
- **공학적 근거**:
  1. Hugh et al. (Pediatrics 2014; 133(4): e862-e868) 논문이 인용한 50dBA는 1997년 AAP 환경보건위원회가 발표한 **병원 신생아실(Nursery) 및 집중치료실(NICU) 권고 환경 소음 상한선**임.
  2. AAP는 민간 상용 영아 수면 기기에 대해 10cm 거리에서 50dBA를 만족해야 한다는 식의 공식 제품 안전 인증 규격을 제정한 바 없음.
  3. 2023년 AAP 수면 안전 지침은 음향 기기 사용 시 "아기 귀로부터 가능한 멀리(최소 30cm 이상) 배치, 최저 음량 운용, 사용 시간 제한"이라는 행동 지침을 권고함.
  4. 따라서 50dBA는 **"병원 신생아실 가이드라인을 참고한 내부 30cm 음향 시험 목표 후보"**로 엄밀히 규정하며, 공인 제품 인증 규격으로 둔갑시켜 승인하는 것을 불허함.
  5. 65dBA 상한 역시 출처 및 영아 노출 시간이 확인되지 않았으므로 공식 승인을 보류하고, 과거의 75dBA는 영아 청각 손상 위험으로 영구 기각을 확정함.

---

### 2.6 안건 6: 진동 안전 기준 (Kimura 2017 & 0.15g) 승인 건
- **심의 결과**: **공식 기준선 승인 보류 (UNSUPPORTED / PENDING REDEFINITION)**
- **공학적 근거**:
  1. Kimura et al. (2017) 논문 원문의 시험 조건은 45Hz 음향 진동이 아니라 **0.5Hz 주기의 거시적 요람 요동(Rocking motion, 변위 2.4mm ~ 7.5mm)**임.
  2. Round 3에서 새로 제시된 $10\mu\text{m} \sim 15\mu\text{m}$ 미세 진동은 Kimura 2017 논문 본문에서 직접 도출되는 수치가 아님.
  3. 변위($A$)와 가속도($a$)는 주파수($f$) 없이는 상호 변환이 불가능함:
     $$a_{\mathrm{peak}} = (2\pi f)^2 A$$
     - $0.5\text{Hz}$에서 $15\mu\text{m}$ 변위 시 가속도는 불과 $0.000015\text{g}$임.
     - $45\text{Hz}$에서 $15\mu\text{m}$ 변위 시 피크 가속도는 $0.122\text{g}_{\mathrm{peak}}$ ($0.086\text{g}_{\mathrm{RMS}}$)임.
     - $45\text{Hz}$에서 $0.15\text{g}_{\mathrm{peak}}$ 가속도를 달성하려면 변위는 약 $18.4\mu\text{m}$가 되어야 함.
  4. 따라서 0.15g는 10~15µm 또는 Kimura 2017로부터 자동으로 유도되는 안전 기준이 아니며, 진동 규격은 다음 4대 요소를 분리하여 전면 재정의(Pending Redefinition)하기 전까지 승인할 수 없음:
     - 진동 형태 분리: 0.5Hz 거시적 요람 요동 vs 45Hz 보이스코일 미세 음향 진동
     - 물리량 분리: 변위(µm, mm), 주파수(Hz), 가속도(g)
     - 측정 정의 분리: 피크(Peak) vs 실효치(RMS)
     - 탑승 조건 분리: 빈 매트리스 vs 5kg 영아 인체 모형(Dummy) 부하 상태

---

### 2.7 안건 7: TP-01~10 계측 규격 합격 기준 확정 건
- **심의 결과**: **잠정 분리 채택, 미검증 수치의 합격 기준 승인 보류 (RECLASSIFIED / PENDING BENCH TEST)**
- **공학적 근거**:
  1. 10대 계측 규격의 식별자 체계 및 BTL 차동 프로빙 안전 규칙(쇼트 파괴 방지)은 정합성을 인정하여 채택함.
  2. 그러나 각 시험 항목의 합격 판정 수치는 공식 합격 기준선이 아닌 4단계 위계(`DATASHEET LIMIT`, `APPROVED SYSTEM REQUIREMENT`, `ENGINEERING TARGET`, `PENDING VALIDATION`)로 엄격히 분리 관리함 ([`TP_ACCEPTANCE_CRITERIA_SOURCE_MATRIX.csv`](file:///Users/youngseok/Desktop/majn/docs/engineering/round3_1_pin_safety_reconciliation/TP_ACCEPTANCE_CRITERIA_SOURCE_MATRIX.csv) 준용).
  3. U2 LDO와 관련하여, 실물 BOM 부품은 AP2112K-3.3TRG1(600mA)임이 확인되었으나, 밀폐 하우징 및 Wi-Fi 버스트 시의 열적 적합성은 실측으로 판단해야 하며, 현 단계에서 SOT-89나 SY8088 벅 컨버터로의 교체를 강제 확정하는 것은 시기상조(Premature)임.

---

## 3. CI 검증 도구 결함 및 도구 강화 의무화 (Mandatory Tool Hardening)

본 감사 과정에서 `tools/majn_circuit_verifier.py` 및 `tools/pcb_verification/` 디렉터리 내 스크립트 3종에 대한 소스코드 전수 검사를 실시한 결과:

1. **결함 적발**:
   - `majn_circuit_verifier.py`, `bom_cpl_comparator.py`, `gerber_integrity_checker.py`, `requirements_traceability_checker.py` 전부에 결함 발견 시 빌드를 중단시키는 **`sys.exit(1)` 호출이 전무**함.
   - 필수 파일 부재, 거버 레이어 누락, CPL 좌표 편차 등 심각한 위반이 발생하더라도 콘솔에 문자열만 출력하고 운영체제 종료 코드 `0 (SUCCESS)`을 반환함.
2. **시정 의무 조치 (Action Item for OpenCode Astra)**:
   - 향후 Gate G1/G2 진행 시 CI 검증 스크립트 전반에 걸쳐 에러 카운터를 도입하고, 실패 시 반드시 `sys.exit(1)`을 명시적으로 반환하도록 도구 강화(Tool Hardening)를 완료할 것.

---

## 4. 최종 지침 및 다음 라운드 지침 (Chief Authority Directives)

1. **Strict Read-Only 유지**:
   - EasyEDA 원본 파일(`.json`, `.epro2`), 회로도, PCB 레이아웃, CPL, BOM, 거버 압축파일(`Gerber_PCB1_revB_2026-07-09.zip`), 펌웨어 소스코드 원본에 대한 일체의 무단 수정을 엄격히 금지함.
2. **Astra에 대한 지침**:
   - 곧바로 PCB #0006 제조 파일 생성이나 EasyEDA 설계를 착수하지 말 것.
   - 본 Round 3.1에서 규명된 TAS5805M Pin 3(ADR/FAULT) 및 Pin 12(PDN), ESP32 GPIO13 및 GPIO35 후보군, 4.7kΩ I2C 풀업, 5.1kΩ CC 저항을 반영한 **공식 ECO(설계 변경 명령서) 초안**을 수립하고 독립 검토 및 사용자 승인을 요청할 것.

---

- **주관 감사관**: Antigravity Independent Investigation Worker
- **최종 판정**: **GATE_G0_G5_HOLD_CONFIRMED / ALL_APPROVAL_REQUESTS_HELD_OR_DISAPPROVED**
