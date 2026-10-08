# MAJUNG Vibration Evidence Matrix — Primary Sources

작성일: 2026-10-08

## 1. 목적

Prapela/SR 계열의 원문을 하나의 efficacy 근거로 묶지 않고, 각 source가 실제로 제공하는 evidence를 분리한다.

핵심 구조:

Source → Evidence Type → Quality → Directness → Gap → Decision → Requirement → Experiment

## 2. Primary evidence matrix

| ID | Source | Population | Main question | Physical stimulus | Main outcome | Evidence role | MAJUNG soothing directness |
|---|---|---|---|---|---|---|---|
| E001-B | Bloch-Salisbury 2009 | 10 preterm infants | respiratory stabilization / physical exposure | 30–60 Hz, 0.021 mm RMS, 0.090 mm max | respiratory pattern / arousal | Engineering + physiological proof-of-concept | Low |
| E001-A | Smith 2015 | 36 preterm infants | apnea/desaturation/bradycardia | 30–60 Hz, 10–20 μm surface displacement | cardiorespiratory events | Randomized crossover physiological evidence | Low |
| E001-C | Zuzarte 2017 | 26 opioid-exposed newborns >37 wk | movement/cardiorespiratory response | 30–60 Hz, 10–12 μm RMS | movement, HR, RR, SpO2 | Within-subject clinical physiological evidence | Low–Moderate |
| E001-D | FDA Prapela 2025 | NOWS newborns + device verification | narrow therapeutic indication / safety | device-specific | morphine/LOS + risk controls | Regulatory + engineering evidence | Low–Moderate |
| E001-E | Bloch-Salisbury 2023 | 208 randomized; 181 analyzed POE newborns | pharmacologic treatment for NOWS | low-level stochastic vibrotactile stimulation, 3 h ON/OFF cycle | morphine treatment, dose, LOS | Randomized clinical efficacy evidence for narrow population | Low |
| E002-A | NCT05711927 / SNOO | 20 preterm infants, 11 SNOO / 9 control | sleep organization | rocking + white noise + swaddling | quiet sleep, active sleep, awake/cry | Multimodal bassinet sleep evidence | Moderate for endpoint design; low for vibration-only efficacy |

## 3. What each source actually establishes

### E001-B — Bloch-Salisbury 2009

Establishes a reproducible engineering methodology:
- define stimulus at mattress surface
- verify 30–60 Hz spectrum
- quantify RMS and maximum displacement
- verify spatial uniformity
- measure acoustic output
- simulate infant/bedding load
- evaluate behavioral arousal boundary.

Does not establish ordinary infant soothing.

### E001-A — Smith 2015

Establishes:
- randomized crossover exposure design
- 30-minute ON/OFF alternation
- within-infant comparison
- physiological response can be quantified under defined stimulation.

Does not establish ordinary infant soothing or sleep benefit.

### E001-C — Zuzarte 2017

Establishes:
- whole-body stochastic vibrotactile stimulation can be studied in a clinical newborn population
- movement and cardiorespiratory variables can be synchronized to stimulation periods
- caregiver/clinical interventions and environmental conditions can be time-stamped.

Limitations:
- small sample
- opioid-exposed newborn population
- within-subject design without independent randomized control group
- concurrent pharmacologic treatment.

Does not establish general infant soothing.

### E001-D — FDA Prapela 2025

Establishes:
- regulatory classification for therapeutic vibrational mattress pad
- narrow clinical indication
- device-risk framework
- need for vibration output, sound, weight effect, uniformity and other verification/validation.

Does not establish general infant efficacy.

### E001-E — Bloch-Salisbury 2023

Establishes:
- randomized clinical evidence in term newborns with prenatal opioid exposure
- predefined clinical endpoints
- treatment exposure logging
- a clinically meaningful signal among morphine-treated responders.

Important null result:
- overall pharmacotherapy administration was not significantly different between TAU and SVS groups.

Therefore the paper must not be summarized as “vibration significantly reduced treatment” without preserving the population, primary result, and responder/subgroup qualification.

Does not establish ordinary infant soothing or sleep improvement.

### E002-A — NCT05711927 / SNOO

Establishes a useful sleep-endpoint precedent:
- randomized comparison of active SNOO versus powered-off bassinet
- continuous behavioral-state coding
- quiet sleep / active sleep / awake / cry
- HR and oxygen-related measurements
- EEG/NIRS planned/used in the protocol.

The intervention is multimodal:
rocking + white noise + swaddling.

Therefore it is not vibration-only evidence.

## 4. Directness classification

### High directness

Only evidence that:
- studies MAJUNG-like physical vibration,
- in the target population,
- with the target endpoint,
- under a controlled comparator,
- with actual physical exposure characterized.

Current state: none.

### Moderate directness

Evidence that:
- uses a related bassinet intervention,
- measures relevant soothing/sleep endpoints,
- but includes multiple sensory components or a different population.

Examples:
- SNOO sleep studies.

### Low directness

Evidence that:
- uses vibrotactile stimulation but studies different populations/endpoints,
- or establishes engineering/safety rather than soothing efficacy.

Examples:
- 2009, 2015, 2017, Prapela FDA, 2023 NOWS RCT.

## 5. Consolidated engineering requirements

### REQ-VIB-01
Measure vibration at actual mattress contact surface.

### REQ-VIB-02
Record frequency spectrum and vibration magnitude.

### REQ-VIB-03
Quantify spatial uniformity.

### REQ-VIB-04
Evaluate load/bedding dependence.

### REQ-VIB-05
Measure acoustic output independently.

### REQ-VIB-06
Synchronize commanded stimulation and measured output.

### REQ-VIB-07
Version-lock the complete mechanical/electrical configuration.

### REQ-VIB-08
If human research is performed, define stimulation intensity before enrollment and monitor it throughout the study.

## 6. Consolidated clinical/research requirements

### REQ-CLIN-01
Human-study exposure must be represented by measured physical output, not only software command.

### REQ-CLIN-02
Behavioral/physiological observations must be timestamped to stimulation ON/OFF.

### REQ-CLIN-03
For immediate response questions, consider within-subject crossover/repeated-condition designs.

### REQ-CLIN-04
Separate vibration efficacy from soothing/sleep efficacy.

### REQ-CLIN-05
Freeze hardware, mattress, firmware and stimulation configuration before efficacy testing.

### REQ-CLIN-06
Use one shared time base across device and research data.

### REQ-CLIN-07
Record caregiver interventions separately.

### REQ-CLIN-08
Record ambient sound/light or document environmental control.

### REQ-CLIN-09
Use objective or blinded behavioral scoring where feasible.

### REQ-CLIN-10
Use actual mattress-surface vibration as the exposure variable.

### REQ-CLIN-11
Separate randomized assignment effects from exposure-duration associations.

### REQ-CLIN-12
Predefine primary outcomes.

### REQ-CLIN-13
Do not promote subgroup/secondary outcomes to primary claims.

### REQ-CLIN-14
If discontinuation/rebound is relevant, define a post-discontinuation observation window.

### REQ-CLIN-15
Attach population and indication to every efficacy statement.

## 7. Consolidated research questions

### RQ-VIB-01
Can MAJUNG produce a reproducible, measurable vibration stimulus at the infant contact surface?

### RQ-VIB-02
How do load, bedding, mattress structure and sensor position change the delivered stimulus?

### RQ-VIB-03
Does a predefined MAJUNG stimulation condition produce measurable short-timescale behavioral or physiological changes in infants?

### RQ-VIB-04
If an effect is observed, is it associated with a specific physical stimulation envelope rather than simply the presence of vibration?

### RQ-VIB-05
What safety-relevant acoustic, mechanical and thermal outputs accompany the stimulation?

### RQ-SOOTHE-01
Does predefined MAJUNG stimulation reduce time-to-settling or increase the probability of fussing resolution without caregiver intervention?

### RQ-SOOTHE-02
Does predefined MAJUNG stimulation alter behavioral sleep-state distribution, including quiet sleep versus active sleep?

### RQ-SOOTHE-03
Are observed behavioral effects accompanied by consistent physiological changes in HR, HRV, RR or SpO2?

### RQ-SOOTHE-04
Are any observed effects reproducible after controlling for feeding, diapering, handling, environment and other caregiver interventions?

Important:
RQ-VIB-03/04 and RQ-SOOTHE-01~04 must not be answered using Prapela/NOWS efficacy evidence alone.

## 8. Experiment sequence

### E-M001 — Basic output

Goal:
verify that the prototype produces measurable vibration.

### E-M002 — Engineering characterization

Measure:
- frequency spectrum
- RMS acceleration/displacement
- peak displacement
- spatial uniformity
- load dependence
- bedding effect
- acoustic output
- time stability.

### E-M003 — Surrogate/worst-case validation

Use representative dummy/load and defined worst-case configurations.

### E-M004 — Medical collaboration preparation

Freeze:
- hardware revision
- mattress revision
- stimulation protocol
- sensor configuration
- data schema
- outcome definitions
- adverse-event/safety monitoring.

### E-M005 — Human observational/clinical research

Only after the stimulation exposure has been physically characterized.

## 9. Decision rule

The project should not advance from engineering characterization to human research simply because “the motor works.”

Advance only when:
1. physical output is measurable,
2. output is reproducible,
3. load dependence is understood,
4. spatial variation is characterized,
5. acoustic output is characterized,
6. stimulation logging is synchronized.

## 10. Current conclusion

The current evidence does not justify the claim:

“Vibration improves sleep/soothing in ordinary infants.”

The current evidence does justify a stronger engineering/research statement:

“Prior neonatal vibrotactile research demonstrates a reproducible methodology for defining, measuring and experimentally testing low-level mattress-surface mechanical stimulation, including frequency, displacement, spatial uniformity, load effects, acoustic output and physiological response.”

A second, separate conclusion is now justified:

“Infant soothing/sleep research provides candidate measurable endpoints such as time-to-settling, fussing resolution, quiet-sleep proportion, longest sleep stretch and sleep efficiency, but current bassinet evidence is predominantly multimodal and therefore cannot be treated as vibration-only efficacy evidence.”

## 11. Evidence integrity rule

Every future source added to the registry must state:

- population
- intervention
- comparator
- physical stimulation parameters
- outcome
- study design
- sample size
- limitations
- source location
- evidence type
- evidence quality
- directness to the MAJUNG research question.

No source may be converted into a general “vibration is beneficial” statement without preserving its population and endpoint.
