# MAJUNG E-001-C — Zuzarte 2017 Primary Source Extraction

- Citation: Zuzarte I, Indic P, Barton B, Paydarfar D. Vibrotactile stimulation: A non-pharmacological intervention for opioid-exposed newborns. PLOS ONE. 2017;12(4):e0175981.
- DOI: 10.1371/journal.pone.0175981
- PMID: 28426726
- PMCID: PMC5398650
- Evidence Type: Prospective within-subject physiological/behavioral study
- Population: 26 opioid-exposed newborns, >37 weeks
- Directness to MAJN engineering: High
- Directness to ordinary infant soothing/sleep efficacy: Low

## 1. Research question

The study evaluates whether stochastic vibrotactile stimulation (SVS) can act as a complementary non-pharmacological intervention for opioid-exposed newborns receiving pharmacologic treatment for neonatal abstinence syndrome.

It does not test healthy term infants or ordinary sleep/soothing.

## 2. Study design

Prospective, single-center, within-subject study.

N = 26.

The mattress delivered:
- 30–60 Hz
- 10–12 μm RMS surface displacement
- whole-body stimulation

Exposure:
- continuous SVS ON
- no-vibration OFF
- alternating 30-minute intervals
- total session 6–8 hours.

Because ON and OFF occurred within the same newborn, each infant supplied an internal comparison.

However, this is not a randomized parallel-group RCT. Time-varying clinical care and within-subject temporal effects therefore remain important confounders.

## 3. Device configuration

The standard hospital crib mattress was replaced by one of two specially constructed mattresses.

Dimensions:
23 × 12 × 3 inches.

The mattresses were designed to fit a standard hospital crib:
26 × 14 × 8 inches.

Two device configurations were used:
- TheraSound, Bellingham, WA
- Wyss Institute / Harvard University system

Both delivered whole-body SVS at the stated surface displacement range.

## 4. Physical stimulation

The exposure is explicitly defined at the mattress surface:

30–60 Hz
10–12 μm RMS surface displacement
near-linear surface displacement.

This is consistent with the earlier neonatal SR studies and is strong support for using contact-surface output as the exposure variable in MAJN.

## 5. Outcome measurement

The study measured:
- movement activity
- heart rate
- respiratory rate
- axillary temperature
- blood oxygen saturation.

Signals were separated into ON and OFF periods.

Movement was quantified using an accelerometer attached to the infant's limb.

The study also used physiological signal acquisition and time-synchronized event annotation.

## 6. Environmental and intervention logging

This is one of the most useful methodological features for MAJN.

A sound meter and light meter were positioned by the infant's head.

Investigators recorded:
- sound intensity
- light level
- caregiver/nursing interventions
- feeding
- pharmacologic dosing
- diapering
- experimental conditions

as time-stamped comments synchronized with physiological signals.

Video recordings were also used to identify interventions and technical contamination.

### MAJN implication

A future medical-research-ready MAJN system should support a common timeline:

timestamp
→ stimulation command
→ measured vibration
→ measured sound
→ physiological signal
→ behavioral annotation
→ caregiver intervention.

This makes later causal interpretation substantially stronger.

## 7. Main findings

SVS was associated with:
- approximately 35% reduction in movement activity
- fewer movement periods longer than 30 seconds
- reductions in tachypneic breaths
- reductions in tachycardic heart beats
- increases in eupneic breaths
- increases in eucardic heart beats.

The authors interpret these findings as evidence that SVS may reduce physiologic dysregulation in opioid-exposed newborns.

## 8. Important interpretation boundary

The movement reduction should not be translated directly into:

“SVS calms normal infants.”

The enrolled infants had prenatal opioid exposure and were receiving pharmacologic treatment for neonatal abstinence syndrome.

Movement activity was an objective signal, but it is not identical to subjective comfort, soothing, or sleep quality.

Therefore the correct evidence statement is:

“Under a defined 30–60 Hz, 10–12 μm RMS whole-body SVS exposure, opioid-exposed newborns showed measurable changes in movement and cardiorespiratory activity.”

## 9. Sound/light and caregiver-event control

The paper's use of synchronized sound, light, video and caregiver-event annotations is particularly valuable.

This helps distinguish:
- response to vibration
from
- response to feeding,
- medication,
- diapering,
- handling,
- environmental change,
- technical contamination.

This should become a direct requirement for any eventual MAJN human study.

## 10. Evidence appraisal

### Evidence Type
Prospective within-subject observational/interventional study.

### Quality
Moderate.

### Strengths
- predefined physical stimulation
- internal ON/OFF comparison
- multiple physiological signals
- objective movement measurement
- synchronized environmental/intervention annotations.

### Limitations
- small sample
- single center
- no independent randomized control group
- opioid-exposed clinical population
- concurrent pharmacologic treatment
- short-term outcome
- movement activity is not equivalent to soothing or sleep quality.

## 11. Engineering implications

### REQ-CLIN-06
Human-study data acquisition must use a shared timestamp.

### REQ-CLIN-07
Caregiver interventions must be logged.

### REQ-CLIN-08
Ambient sound and light should be measurable or at least documented during physiological experiments.

### REQ-CLIN-09
Movement should be quantified objectively rather than relying only on observer ratings.

### REQ-CLIN-10
The actual mattress-surface vibration should be measured or independently verified during the experimental session.

## 12. Proposed MAJN research data schema

Minimum event record:

timestamp
stimulus_command
measured_vibration
measured_sound
light_level
movement_activity
heart_rate
respiratory_rate
SpO2
temperature
caregiver_event
feeding_event
medication_event
diapering/handling_event
technical_contamination_flag

This schema should be considered a research-design requirement rather than a product feature requirement.

## 13. Relationship to Smith 2015

Smith 2015:
- preterm infants
- randomized crossover
- respiratory/cardiorespiratory endpoint.

Zuzarte 2017:
- term opioid-exposed newborns
- within-subject ON/OFF
- movement + cardiorespiratory + environmental/event logging.

Together they demonstrate that the same general SVS platform has been studied using both physiological and behavioral/movement endpoints, but neither establishes ordinary infant soothing efficacy.

## 14. Relationship to 2023 RCT

The 2023 trial moves the evidence level upward for the narrow POE/NOWS clinical question because it uses parallel randomized allocation and a substantially larger sample.

However, its primary endpoints are pharmacologic treatment and hospital outcomes, not direct calming or sleep measures.

Therefore the three studies should remain separate evidence layers:

2009 → engineering + respiratory proof-of-concept
2015 → randomized physiological response
2017 → behavioral/physiological within-subject response
2023 → larger randomized clinical outcome.

## 15. Decision

E-001-C supports adding synchronized environmental and caregiver-event logging to the MAJN medical research architecture.

It does not support a general claim that vibration improves infant soothing or sleep.

## 16. Source traceability

Primary:
- PubMed PMID 28426726
- PMC PMCID PMC5398650
- DOI 10.1371/journal.pone.0175981

Key locations:
- Abstract: design, stimulation, outcomes
- Materials and Methods / Participants: eligibility and cohort
- Materials and Methods / Vibrotactile stimulation: mattress dimensions and 30–60 Hz, 10–12 μm RMS
- Materials and Methods / Data collection: movement, ECG, respiratory, SpO2, temperature
- Materials and Methods / Environmental monitoring: sound/light and timestamped comments
- Results: movement and cardiorespiratory findings
- Discussion: interpretation and limitations


## 11. Primary-source locator audit (updated 2026-10-13)

Primary source checked: publisher-hosted printable PDF and full-text PMC, DOI 10.1371/journal.pone.0175981. Printed page numbers below refer to the PDF's own “x / 15” pagination.

| Extracted claim | Exact printed locator | Value & unit | Denominator / Analysis set | Verification status / interpretation |
|---|---|---|---|---|
| Population & Cohort | PDF p.1 Abstract; pp.3–4 Table 1 | N=26 | 26 term opioid-exposed newborns on morphine | **Verified**: PCA 38.3–44.7 wks, all receiving morphine, 8 receiving phenobarbital |
| Physical Exposure | PDF p.1 Abstract; p.4 Methods | 30–60 Hz, 10–12 μm RMS | N=26 | **Verified**: continuous SVS in 30-min ON/OFF blocks |
| Condition duration & Caregiver intervention | PDF p.7 Results | OFF 28.7 min vs ON 28.8 min (P=.561); Caregiver OFF 58.1 s vs ON 54.5 s (P=.874) | 26 infants | **Verified**: No significant difference in baseline block time or caregiver disruption |
| Movement Period % (MP%) | PDF p.7 Results; p.9 Table 2; p.8 Fig 3 | 35% relative reduction (14% absolute reduction), P<.001 | 26 infants (23/26 reduced) | **Verified**: Valid non-movement time OFF 17.5 min vs ON 21.6 min (P<.001) |
| Movement burst skewness (Sigma) | PDF p.7 Results; p.9 Table 2 | OFF 1.7 (CI 1.6–1.8) vs ON 1.5 (CI 1.4–1.6), P=.002 | 26 infants | **Verified**: Fewer prolonged movement periods (>5 s, ≥30 s); brief MPs (≤5 s) unaffected |
| Respiratory rate & pattern | PDF p.7 Results; p.9 Table 2; p.6 Fig 2 | Mean RR ~6 bpm lower with SVS; eupneic breaths increased, tachypneic breaths decreased | 26 infants | **Verified**: IBI variance P=.303 (NS); Bradypnea unaffected; 4 apneas (>10 s) in 3 infants |
| Heart rate & intervals | PDF p.7 Results; p.9 Table 2 | Mean HR <3 bpm lower with SVS (P=.016); HR variance reduced (P=.001) | 26 infants | **Verified**: Tachycardic beats 36.6% relative reduction; Bradycardic beats unaffected |
| SaO2 & Skin Temperature | PDF p.7 Results; p.9 Table 2 | SaO2 ~99% (P=.544); Temp 36.8°C (P=.581) | 26 infants | **Verified**: Virtually no thermoregulation or desaturation issues during study |
| Sound & Light environment | PDF p.7 Results | Sound 52.2 dBA (P=.102); Light 97.1 lux (P=.632) | 26 infants | **Verified**: Background environmental conditions stable across ON/OFF |
| Adjusted regression models | PDF p.10 Table 3 | Adjusted movement -14.6%, HR -2.6 bpm, RR -5.6 bpm | 26 infants | **Verified**: Mixed-effects model adjusting for covariates; females had lower movement/HR |
| Adverse events statement | PDF p.11 Discussion, paragraph 3 | "There were no adverse effects associated with SVS in the current study" | 26 infants, 6–8 h session | **Verified**: Authors explicitly state further studies required to establish safety and efficacy |
| Anecdotal caregiver reports | PDF p.11 Discussion, paragraph 3 | Nurses/parents reported infants seemed “less irritable”, “calmer”, “slept better” | Anecdotal survey | **Verified**: Anecdotal feedback, explicitly distinguished from objective proof of sleep |

### 12. Discrepancy & Boundary Log
- **Discrepancy Check**: 이전 요약 문서의 35% 움직임 감소 및 14% 포인트 절대 감소는 Table 2 및 Results 텍스트와 정확히 일치함. 이전 기록에 누락되었던 Condition duration (OFF 28.7 min vs ON 28.8 min), Caregiver intervention duration (58.1 s vs 54.5 s), Sigma skewness (1.7 vs 1.5) 수치를 공식 원문과 완전 대조하여 추가함.
- **Safety Boundary**: 저자의 "No adverse effects" 보고는 본 26명 대상의 단기 6–8시간 입원 세션에 한정됨. 일반 영아 대상 장기/가정 사용 안전성 근거가 아님.
- **Efficacy Boundary**: 움직임 감소(Movement reduction)는 수면다원검사(PSG)로 확인된 수면 질 개선이나 영아 진정의 직접적 증거가 아님.
- **Reviewer Status**: 1차 원문 수치 및 인쇄 PDF(x/15) 대조 완료. 외부 독립 2차 검토는 미실시(Internal check only).
