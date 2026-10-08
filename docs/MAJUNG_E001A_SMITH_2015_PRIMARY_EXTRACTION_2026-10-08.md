# E-001-A Smith 2015 — Primary Source Extraction

- Citation: Smith VC, Kelty-Stephen D, Qureshi Ahmad M, et al. Stochastic Resonance Effects on Apnea, Bradycardia, and Oxygenation: A Randomized Controlled Trial. Pediatrics. 2015;136(6):e1561-e1568.
- DOI: 10.1542/peds.2015-1334
- PMID: 26598451
- PMCID: PMC4657600
- Trial: NCT01643057
- Evidence Type: Clinical efficacy / physiological response / engineering exposure characterization
- Population: preterm infants
- Directness to MAJN soothing/sleep question: Low
- Directness to infant vibrotactile research design: High

## 1. Research question

The study asks whether stochastic resonance (SR) stimulation changes clinically significant apnea, oxygen desaturation, and bradycardia events in preterm infants.

This is not a study of soothing, crying, sleep duration, or ordinary-term infant settling.

## 2. Study design

Randomized crossover design.

Each infant served as their own control.

Intervention structure:
- up to two 3- or 4-hour intervention periods
- 30-minute alternating SR-ON and SR-OFF intervals
- first intervention period began ON or OFF according to random assignment
- second intervention period began in the opposite state

This is an important design feature for MAJN because the intervention is repeatedly switched within the same subject, allowing short-timescale physiological response comparison.

## 3. Population

36 preterm infants.

Mean gestational age: 30.5 ± 3 weeks.
Mean birth weight: 1409 ± 450 g.

Eligibility:
- gestational age <36 weeks
- postmenstrual age <45 weeks
- at least one clinically documented apnea, bradycardia and/or oxygen desaturation event before enrollment
- no mechanical ventilation or CPAP at the time of study
- no birth-weight restriction

Clinical treatment decisions, including caffeine and supplemental oxygen, remained at the treating clinician's discretion.

## 4. Actual stimulation

The intervention was delivered through a custom-built SR mattress.

Reported surface stimulation:
- frequency bandwidth: 30–60 Hz
- displacement: 10–20 μm
- gentle, low-amplitude surface displacement

Two mattress systems were used:
1. TheraSound mattress with Balance Engineering signal generator in 13 infants.
2. Wyss Institute-developed signal generator/mattress in 23 infants, with an isolation unit that significantly dampened vibration in the rostral third.

The paper states that the two systems otherwise provided identical stimulation.

This matters: the clinical study did not simply establish “vibration ON.” It specified an actual physical stimulation envelope at the mattress surface.

## 5. Protocol figure

Figure 1 is a schematic of the common protocol sequence.

The important experimental logic is:

randomized initial state
→ 30 min ON/OFF alternation
→ repeated within-subject comparison.

For a future MAJN study, an analogous timestamped intervention protocol could be used, but the clinical endpoint would need to be chosen separately.

## 6. Outcomes

Primary physiological event categories:
- apnea
- oxygen desaturation
- bradycardia

The paper reports:
- apnea event count decreased by 50%
- oxygen desaturation event number, duration, and intensity decreased by approximately 20–35%
- bradycardia intensity decreased by nearly 20%
- bradycardia event number and duration did not change

The conclusion is explicitly framed as a potential supplementary treatment for apnea, oxygen desaturation and some aspects of bradycardia in premature infants.

## 7. Important interpretation boundary

The result cannot be generalized to:
- healthy term infants
- ordinary infant sleep improvement
- calming/crying reduction
- consumer bassinet soothing
- long-term developmental benefit

The study population was clinically selected preterm infants with documented cardiorespiratory events.

Therefore:

Smith 2015 → evidence that a defined vibrotactile stimulus can alter physiological respiratory/cardiorespiratory outcomes in selected preterm infants.

NOT:

Smith 2015 → evidence that vibration makes ordinary babies sleep better.

## 8. Engineering-relevant measurement logic

The paper's stimulation description is surface-based: frequency bandwidth and mattress-surface displacement are defined.

This supports a MAJN requirement that the stimulation condition must be measured at the actual mattress contact surface rather than inferred from motor command voltage/PWM.

The paper also references rigorous validation and maintenance checks for the stimulation equipment.

## 9. Statistical analysis

The study used Poisson-based modeling with mixed/random-effects terms to account for repeated observations within infant/session.

This is relevant for future MAJN research because a repeated ON/OFF or crossover design generates clustered observations rather than independent observations.

A future protocol should therefore predefine:
- unit of analysis
- subject-level repeated measures
- time-window definition
- baseline handling
- carryover/transition handling
- missing data handling

## 10. Safety / adverse effects

The authors report no adverse effects during this study and describe the findings as proof-of-concept.

However, “no adverse effects” in 36 selected preterm infants during short study periods is not equivalent to general infant safety evidence.

This distinction must remain explicit in the MAJN evidence registry.

## 11. Conflict / technology provenance

The paper discloses that David Paydarfar and John Osborne were coinventors of the Wyss Institute neonatal stochastic resonance delivery system, and that the technology had been licensed by Harvard University to SR-Bio, Inc.

This does not invalidate the study, but it belongs in the evidence-quality record because device provenance and intellectual-property relationships are part of transparent appraisal.

## 12. Evidence appraisal

### Evidence Type
Primary randomized clinical crossover study.

### Internal relevance
High for:
- physiological response to vibrotactile stimulation
- short-timescale ON/OFF experimental design
- exposure definition
- physiological outcome measurement

### Directness to MAJN
High for engineering/experimental methodology.
Low for ordinary infant soothing/sleep claims.

### Main limitation
Small, highly selected preterm clinical population and short intervention windows.

### Additional limitation
Two related mattress systems were used. Although the authors state that the stimulation was otherwise identical, this should be treated as a device-configuration variable rather than ignored.

## 13. MAJN design implications

### REQ-CLIN-01
The stimulation condition must be explicitly defined by measured physical output, not only by software command.

### REQ-CLIN-02
Clinical/behavioral observations should be timestamped against stimulation ON/OFF state.

### REQ-CLIN-03
A crossover or repeated-condition design should be considered if the research question concerns immediate physiological/behavioral response.

### REQ-CLIN-04
The research question must not combine “vibration efficacy” with “soothing/sleep efficacy.” They are separate evidence questions.

### REQ-CLIN-05
Device configuration must be frozen/versioned for each experimental run.

## 14. Proposed MAJN bridge experiment

Before involving infants:

MAJN prototype
→ contact-surface vibration measurement
→ dummy/load dependence
→ spatial uniformity
→ acoustic measurement
→ command/output synchronization
→ fixed stimulation protocol

Only after that:

defined stimulation
→ observational/clinical research
→ behavioral + physiological outcomes
→ safety monitoring.

## 15. Source traceability

Primary source:
- PubMed: PMID 26598451
- PMC: PMCID PMC4657600
- DOI: 10.1542/peds.2015-1334
- ClinicalTrials.gov: NCT01643057

Relevant source locations:
- Abstract: objective, design, population, principal results
- Methods / Study Design: randomized crossover and alternating 30-min intervals
- Methods / SR Stimulation: 30–60 Hz and 10–20 μm surface displacement; two mattress systems
- Results: event-level outcomes and effect estimates
- Figure 1: protocol sequence
- Figure 2: enrollment flow
- Figure 3: CONSORT flow diagram
- Discussion: comparison with prior SR mattress study and interpretation of findings
- Financial Disclosure: device-inventor/licensing relationship

## 16. Evidence-chain conclusion

Smith 2015 strengthens the MAJN evidence chain in a specific way:

defined physical stimulus
→ randomized within-subject exposure
→ timestamped physiological outcome
→ quantified response

It does not establish:

defined physical stimulus
→ ordinary infant calming/sleep benefit.

That latter question requires separate evidence and should become its own RQ rather than being inferred from Prapela/SR respiratory studies.
