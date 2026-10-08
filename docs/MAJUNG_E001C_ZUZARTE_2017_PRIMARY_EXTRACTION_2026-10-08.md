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
