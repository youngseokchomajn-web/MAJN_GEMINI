# E-001-D Prapela SVS FDA De Novo — 원문 추출 및 MAJN 요구사항 연결

- 작성일: 2026-10-08
- Source: FDA De Novo Summary, DEN240031
- 원문: https://www.accessdata.fda.gov/cdrh_docs/reviews/DEN240031.pdf
- PDF: 9 pages
- Evidence Type: Regulatory / Engineering / Clinical
- Evidence Quality: High for authorized indication and device-risk characterization; not general infant soothing efficacy evidence.

## 1. Source → Evidence

### S-001
FDA는 Prapela SVS hospital bassinet pad (model P01)을 "therapeutic vibrational mattress pad"라는 device type으로 분류하고 Class II, product code QVY, 21 CFR 880.5151을 설정했다.

원문 위치: PDF p.1, lines 3–12.

### S-002
Indication은 37주 이상이며 prenatal opioid exposure가 있고 NOWS가 있는 newborn에서 adjunctive non-pharmacological therapy로 제한된다. 처방전 사용이다.

원문 위치: PDF p.1, lines 19–26.

### S-003
금기/제외 조건에는 <37주, clinically significant congenital/fetal abnormality, hydrocephalus 또는 IVH > grade 2, 비약물성 seizure disorder, significant cardiac shunt, Hb <8 g/dL, HIE, invasive ventilation이 필요한 respiratory failure, MRSA/감염 등이 포함된다.

원문 위치: PDF p.2, lines 27–46.

### S-004
Prapela P01은 foam 내부 중앙에 transducer가 내장된 재사용 mattress pad이며, 작은 입력의 stochastic stimulation을 foam을 통해 전달한다. hand-held controller로 vibration을 ON/OFF하고, ON 상태에서 3시간 ON/OFF cycle로 작동한다.

원문 위치: PDF p.2, lines 47–54.

### S-005
Firmware는 vibration delivery용 feedback loop를 제어한다. startup/initialization, ON/OFF, 지정된 frequency range 내 random signal generation을 담당하며, pad surface vibration의 전체 amplitude를 DRMS(Displacement Root Mean Square)로 정의하고 potentiometer로 설정한다.

원문 위치: PDF p.4, lines 99–111.

### S-006
Bench testing에는 다음이 명시적으로 포함된다.

1. vibration displacement and frequency
2. effect of patient weight on stimulation
3. dimensional testing
4. stimulation uniformity
5. auditory sound level

모두 passing으로 보고됐다.

원문 위치: PDF pp.4–7, lines 112–182.

### S-007
임상 근거는 두 연구에서 제출됐다.

- Bloch-Salisbury et al. 2023 RCT: 181명 분석, SVS 94 / standard care 87.
- Zuzarte et al. 2017: 26명 opioid-exposed newborns.

FDA는 2017 연구의 endpoint들이 intended indication의 effectiveness를 입증하기에는 적절하지 않았다고 명시하면서도 adverse events와 thermoregulation/oxygenation 자료가 safety support에 기여했다고 판단했다.

원문 위치: PDF p.7, lines 183–216.

### S-008
FDA가 therapeutic vibrational mattress pad에 대해 식별한 위험은:

- inappropriate vibration / high sound level에 의한 sleep disruption 또는 hearing loss
- ineffective treatment / symptom worsening
- inappropriate placement
- cord/strap strangulation
- entrapment
- electrical shock/burn
- interference with other medical devices
- adverse tissue reaction
- infection

이다.

원문 위치: PDF pp.8–9, lines 221–254.

### S-009
Special controls에는 다음이 포함된다.

- clinical performance data
- vibration mechanism output verification/validation
- auditory sound level verification/validation
- dimensional compatibility testing
- electrical safety and EMC
- software verification/validation/hazard analysis
- biocompatibility
- fit/placement, compatible bassinets, cleaning/disinfection, suffocation/strangulation warnings

원문 위치: PDF pp.8–9, lines 255–276.

### S-010
FDA의 benefit-risk conclusion은 일반적인 infant soothing 효과가 아니라, stated indication의 NOWS population에서 probable benefits outweigh probable risks라는 판단이다. 특히 morphine-responsive subgroup에서 treatment length와 cumulative morphine dose 감소의 probable benefit을 근거로 들었다.

원문 위치: PDF p.9, lines 277–302.

---

# 2. Quality / Appraisal

## Evidence Type

Primary regulatory evidence + engineering verification framework + clinical evidence summary

## Evidence Quality

### Regulatory characterization: High
FDA가 직접 검토한 1차 규제자료이며 device classification, indication, risks, special controls가 명시되어 있다.

### Engineering evidence: High for design requirements
진동 displacement/frequency, patient weight, uniformity, sound level 등을 실제 bench testing 항목으로 명시한다.

### Clinical efficacy: High only for the narrow intended indication
FDA의 benefit-risk conclusion은 특정 NOWS population에 대한 것이며, 일반 영아의 sleep/soothing efficacy를 입증하는 자료가 아니다.

### Directness to MAJN
Engineering: High
Clinical efficacy: Low–Moderate

---

# 3. Interpretation

이 자료에서 MAJN이 가져와야 할 것은 "Prapela가 효과가 있으므로 MAJN도 효과가 있을 것이다"가 아니다.

가장 중요한 정보는 오히려 FDA가 진동 mattress를 하나의 medical-device system으로 평가할 때 무엇을 측정하도록 요구했는가이다.

즉 다음 구조가 확인된다.

physical stimulation → device performance verification → environmental/clinical use → clinical outcome → risk controls

따라서 MAJN의 초기 연구도 "아기가 편안해지는가?"부터 시작하기보다 실제 접촉면에 어떤 자극이 전달되는가를 먼저 정량화해야 한다.

---

# 4. Gap

## G-001-D1 — General infant extrapolation

Prapela의 authorized indication은 NOWS newborn에 한정된다.

따라서 Prapela FDA authorization을 일반 영아의 sleep/soothing efficacy evidence로 사용할 수 없다.

## G-001-D2 — Parameter disclosure

FDA summary에는 vibration displacement/frequency testing이 존재한다는 것은 명확하지만, 상세 시험값의 일부는 redacted되어 있다.

따라서 FDA summary만으로 Prapela의 전체 stimulation envelope를 복원할 수 없다.

→ 상세 parameter는 원 임상 논문 및 공개 engineering 자료를 별도로 추적해야 한다.

## G-001-D3 — Clinical outcome vs engineering parameter

FDA 자료는 engineering performance와 clinical performance를 모두 요구하지만, public summary만으로 특정 parameter와 clinical outcome 사이의 dose-response를 완전히 연결할 수 없다.

---

# 5. Decision

### D-001-D1
Prapela를 MAJN의 efficacy claim 근거로 직접 사용하지 않는다.

### D-001-D2
Prapela FDA 문서를 MAJN vibration engineering requirement의 강한 선행근거로 사용한다.

### D-001-D3
임상 연구 전 MAJN prototype의 contact-surface stimulation을 계측한다.

### D-001-D4
vibration과 acoustic output을 분리해서 평가한다.

### D-001-D5
load dependence와 spatial uniformity를 반드시 포함한다.

### D-001-D6
software/firmware가 stimulation을 생성한다면 stimulation log와 actual measured output의 traceability를 확보한다.

---

# 6. MAJN Requirements

## REQ-VIB-01 — Contact-surface output

영아가 실제로 접촉하는 mattress surface에서 vibration을 측정할 수 있어야 한다.

최소 기록 후보:
- frequency
- RMS acceleration
- displacement 또는 이에 상응하는 vibration magnitude
- waveform / spectral characteristics

## REQ-VIB-02 — Load dependence

dummy/load를 이용해 하중 변화에 따른 output 변화를 측정한다.

최소 조건:
- low load
- nominal load
- high load / worst-case load

목적은 "아기 체중에서 진동이 강해지는가/약해지는가"를 정량적으로 확인하는 것이다.

## REQ-VIB-03 — Spatial uniformity

mattress의 여러 위치에서 동일 stimulation command가 실제로 어느 정도 균일하게 전달되는지 측정한다.

최소 grid:
- center
- head-side
- foot-side
- left
- right

필요하면 finer grid로 확장한다.

## REQ-VIB-04 — Acoustic output

vibration motor/transducer가 만드는 audible sound를 별도 계측한다.

이유:
FDA가 inappropriate vibration과 high auditory sound level을 별개의 risk로 취급하기 때문이다.

## REQ-VIB-05 — Mechanical compatibility

mattress/bassinet geometry가 변경되면 vibration transfer가 바뀔 수 있으므로 enclosure, mattress thickness, support structure 등을 configuration item으로 기록한다.

## REQ-VIB-06 — Stimulation traceability

commanded stimulation과 measured stimulation을 시간축으로 연결한다.

예:
timestamp → firmware state → commanded parameter → measured vibration → measured sound

## REQ-VIB-07 — Safety evidence separation

효과를 입증하는 실험과 안전성을 입증하는 실험을 별도 evidence stream으로 관리한다.

---

# 7. Engineering experiment — E-M001

## 목적

MAJN prototype이 의도한 vibration을 실제 contact surface에 재현 가능하게 전달하는지 검증한다.

효과를 시험하지 않는다.

## Setup

- MAJN bassinet prototype
- mattress
- infant-equivalent dummy/load
- accelerometer
- microphone
- data acquisition
- stimulation controller log

## Test matrix

### A. Frequency / spectrum
동일 command에서 실제 surface output 측정.

### B. Amplitude
command level별 RMS acceleration/displacement 측정.

### C. Load
최소 3개 load condition 비교.

### D. Position
5-point 이상 spatial measurement.

### E. Time stability
장시간 stimulation에서 output drift 확인.

### F. Acoustic
동일 조건에서 sound pressure level 기록.

---

# 8. Evidence chain

현재 가장 좋은 연결은 다음이다.

FDA Prapela
→ REQ-VIB-01~07
→ E-M001 engineering characterization
→ surrogate validation
→ medical collaboration
→ RQ-001/RQ-002
→ human clinical/observational evidence

즉 Prapela 자료가 바로 사람 실험으로 넘어가는 게 아니라 engineering evidence를 먼저 만들도록 중간 단계가 생긴다.

---

# 9. 추가로 확인된 중요한 원문 근거

Prapela 관련 2017 연구는 26명 opioid-exposed newborns에서 30–60 Hz, 10–12 μm RMS surface displacement의 SVS를 사용했고, 30분 ON/OFF를 반복했다. movement activity가 35% 감소했으며 HR/호흡 관련 지표도 변화했다. 연구는 movement, ECG, respiratory inductance plethysmography, SpO2, temperature를 지속적으로 측정했고 sound/light 및 caregiver intervention도 time-stamped로 기록했다.

이것은 MAJN의 후속 임상연구 설계에서 특히 중요하다.

"진동을 줬다"만 기록하지 말고, 자극 조건과 physiological/behavioral signals를 같은 time base에 놓는 구조를 처음부터 설계하는 것이 좋다.

---

# 10. Next

1. E-001-A Smith 2015 원문을 Methods/Results/Figure/Table 단위로 extraction
2. 실제 Prapela stimulation parameter의 출처별 reconciliation
3. E-001-A~E를 하나의 Evidence Matrix로 통합
4. 그 결과로 MAJN E-M001 dummy vibration test matrix를 확정

