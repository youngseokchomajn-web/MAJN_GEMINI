# E-001-B Bloch-Salisbury 2009 — Primary Source Extraction

- Citation: Bloch-Salisbury E, Indic P, Bednarek F, Paydarfar D. Stabilizing immature breathing patterns of preterm infants using stochastic mechanosensory stimulation. Journal of Applied Physiology. 2009;107(4):1017-1027.
- DOI: 10.1152/japplphysiol.00058.2009
- PMID: 19608934
- PMCID: PMC2763836
- Evidence Type: Engineering exposure characterization + physiological proof-of-concept
- Population: 10 preterm infants
- Directness to MAJN vibration engineering: Very High
- Directness to ordinary infant soothing/sleep efficacy: Low

## 1. Research question

The study investigates whether low-level stochastic mechanosensory stimulation delivered through the mattress can stabilize immature respiratory patterns in sleeping preterm infants.

The authors explicitly characterize the stimulus as subthreshold for behavioral arousal.

This is important because the paper simultaneously addresses:
1. physical stimulation definition,
2. stimulus uniformity,
3. load/bedding effects,
4. acoustic output,
5. physiological response.

## 2. Population

10 preterm infants.

Mean postconceptional age: 33.3 ± 1.7 weeks.

The study focuses on immature breathing patterns rather than ordinary infant sleep quality or soothing.

## 3. Mattress and actuator

The standard mattress was replaced with a specially constructed TheraSound mattress.

The mattress contained:
- an actuator
- a sounding board embedded within mattress foam
- Gaussian white-noise signal generator
- adjustable low-pass and high-pass filters.

The actuator generated mechanical displacement through the mattress structure.

## 4. Actual stimulation envelope

The paper directly measured mattress-surface displacement.

Reported stimulation:
- filtered white noise
- 30–60 Hz bandwidth
- 0.021 mm RMS displacement
- 0.090 mm maximum displacement

0.021 mm = 21 μm RMS.

The paper states that the 30–60 Hz band was confirmed by power analysis of the displacement signal measured at the mattress surface.

This is a critical precedent for MAJN:
the stimulation parameter is defined by the physical output at the mattress surface, not only by the electrical drive command.

## 5. Surface uniformity

A linear displacement transducer was used to measure the mattress surface.

The authors report near-uniform displacement across the mattress surface:
±2%.

This is one of the strongest engineering precedents found so far for MAJN.

It means that “the mattress vibrates” is not considered sufficient characterization. The spatial distribution of the vibration was explicitly measured.

## 6. Behavioral-arousal threshold

Before selecting the experimental intensity, the investigators performed preliminary observations in sleeping preterm infants.

They increased stimulation until behavioral awakening occurred, including eye opening and body movement.

They then selected 0.021 mm RMS / 0.090 mm maximum displacement because it was below the minimum threshold for behavioral arousal to wakefulness.

Formal polysomnography was used to confirm the absence of detectable behavioral-state disruption at the selected intensity.

Important interpretation:
this is evidence about a particular preterm-infant population and a particular stimulus configuration. It is not a universal safe threshold for infants.

## 7. Acoustic measurement

A sound meter was used to measure:
- sound frequency
- sound intensity in dB(A)

Sensor placement:
on top of the mattress bedding material, adjacent to the infant's cranium.

This is highly relevant to MAJN because mechanical vibration and audible acoustic output were treated as separate measurable quantities.

## 8. Load and bedding simulation

To simulate the effect of infant and bedding material on mattress vibration, the investigators placed:
- 1–1.5 kg saline-filled bags
- wrapped in a swaddle blanket
- on the mattress
- covered with a sheet.

Thin accelerometers were placed on the surface of the saline bags facing the mattress.

Result:
the bedding material and saline bag produced an undetectable (<1%) shift in the power spectrum of acceleration over the 30–60 Hz band.

This is a direct precedent for a MAJN dummy/load experiment.

## 9. Physiological measurement

The study used polysomnographic/physiological monitoring to evaluate respiratory behavior.

The stimulation was intended to affect respiratory rhythm without causing a behavioral-state transition.

The key methodological point for MAJN is the separation of:
- stimulus exposure
- physiological response
- behavioral state.

## 10. Evidence appraisal

### Evidence Type
Primary experimental study with direct engineering characterization.

### Engineering relevance
Very High.

It provides a concrete method for:
- defining stimulus at the contact surface
- measuring spatial uniformity
- testing load/bedding influence
- measuring acoustic output
- identifying a behavioral-arousal boundary for the tested population.

### Clinical relevance
Moderate for neonatal respiratory physiology.

### Directness to MAJN soothing
Low.

The endpoint was respiratory stabilization, not calming, sleep duration, crying, or caregiver burden.

## 11. Main limitations

- only 10 infants
- preterm population
- specific mattress/actuator construction
- specific frequency band and displacement
- short experimental setting
- behavioral-arousal threshold cannot be generalized to all infants
- the study was not designed to test ordinary infant soothing.

## 12. MAJN engineering requirements derived from this source

### REQ-VIB-08 — Surface displacement measurement
Measure vibration at the mattress surface.

### REQ-VIB-09 — Spatial uniformity
Quantify spatial variation rather than reporting only a single sensor point.

A useful initial target for characterization is to report the measured coefficient/range across a predefined grid. The ±2% value from the 2009 system should be treated as a reference benchmark, not as an automatically applicable MAJN specification.

### REQ-VIB-10 — Load simulation
Repeat vibration measurements with representative dummy/load and bedding conditions.

### REQ-VIB-11 — Acoustic separation
Measure dB(A) at a defined location near the head region independently from mechanical vibration.

### REQ-VIB-12 — Behavioral-state boundary
If human research is eventually performed, stimulation intensity should be pre-specified and monitored rather than increased ad hoc during the experiment.

## 13. Proposed MAJN engineering test

### E-M002 — Contact-surface vibration characterization

Configuration:
- MAJN bassinet
- production-intent mattress
- sensor grid
- accelerometer/displacement measurement
- microphone
- representative load/dummy
- standard bedding configuration

Conditions:
1. no load
2. low representative load
3. nominal representative load
4. high/worst-case load
5. center position
6. peripheral positions
7. repeated runs

Record:
- frequency spectrum
- RMS acceleration
- displacement where measurable
- peak displacement
- spatial variation
- sound pressure level
- temperature of actuator/electronics if relevant
- firmware command and timestamp.

## 14. Important comparison with Smith 2015

The two studies should not be merged into one “Prapela vibration evidence” bucket.

### 2009
Strongest for:
physical stimulus definition
→ surface measurement
→ uniformity
→ load/bedding simulation
→ acoustic measurement
→ behavioral-arousal boundary

### 2015
Strongest for:
randomized crossover
→ repeated ON/OFF exposure
→ within-subject comparison
→ quantified physiological outcomes.

Therefore the MAJN research architecture should preserve both evidence streams.

## 15. Evidence-chain conclusion

The strongest engineering precedent currently identified is:

defined physical stimulus
→ measured at mattress surface
→ spatial uniformity verified
→ load/bedding effect tested
→ acoustic output measured
→ behavioral-state boundary assessed
→ physiological response evaluated.

This is much more useful for MAJN than simply citing Prapela as a successful commercial device.

## 16. Source traceability

Primary source:
- PubMed: PMID 19608934
- PMC: PMCID PMC2763836
- DOI: 10.1152/japplphysiol.00058.2009

Key source sections:
- Abstract: population, stimulus magnitude, respiratory outcome
- Vibrotactile Stimulation: mattress construction, 30–60 Hz, 0.021 mm RMS, 0.090 mm maximum
- same section: ±2% spatial uniformity
- same section: sound-meter method
- same section: 1–1.5 kg saline-bag load/bedding simulation
- Results: polysomnographic/respiratory response and behavioral-state observations
- Discussion: interpretation of mechanosensory stimulation and respiratory stabilization

## 17. Decision

E-001-B is promoted to a core engineering precedent for MAJN.

It should be cited when justifying:
- contact-surface measurement,
- spatial uniformity testing,
- dummy/load testing,
- acoustic measurement,
- and separation of mechanical stimulation from behavioral/physiological outcomes.

It should not be cited as evidence that a bassinet vibration system improves sleep or soothing in healthy term infants.
