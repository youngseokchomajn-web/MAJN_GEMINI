# E001-A/B/C — 핵심 수치별 1차 원문 locator audit
작성일: 2026-10-12

이 문서는 기존 추출 문서의 수치를 원문 섹션·표·그림에 연결하는 보조 감사 기록이다. 표·그림 번호는 각 논문 내 번호이며, 페이지는 저널 인쇄본 기준을 별도로 확인하지 않은 경우 임의로 기입하지 않는다.

## E001-A — Smith et al. 2015

**원문:** Smith VC, et al. *Stochastic Resonance Effects on Apnea, Bradycardia, and Oxygenation: A Randomized Controlled Trial.* Pediatrics. 2015;136(6):e1561–e1568. DOI: 10.1542/peds.2015-1334. PMID 26598451; PMCID PMC4657600.  
URL: https://pmc.ncbi.nlm.nih.gov/articles/PMC4657600/

| Claim | Exact locator | Result / data to retain | Interpretation boundary |
|---|---|---|---|
| Design, n=36, preterm population | Abstract; Methods; Figures 2–3 participant flow | Randomized crossover; each infant served as own control; alternating 30-minute SR-ON/OFF intervals | This is a preterm respiratory physiology study, not a soothing/sleep trial |
| Physical exposure | Methods, “SR Stimulation” | Mattress surface displacement, 30–60 Hz; 10–20 μm; two mattress configurations described | Study-specific exposure; not a MAJUNG safety target |
| Oxygen desaturation | Results, “Oxygen Desaturation”; Table 2 | 709 total events; 315 ON vs 394 OFF. Number of events reduced 18% (95% CI 5%–29%, P=.01); event duration reduced 35% (95% CI 33%–37%, P<.0001); intensity reduced 21% (95% CI 20%–22%, P<.0001) | Keep event count, duration and intensity distinct |
| Apnea | Results, “Apnea”; Table 2 | 39 total events; 13 ON vs 26 OFF; reported 50% reduction in apnea events | Event definition differs from other studies; do not pool raw counts across papers |
| Bradycardia | Results, “Bradycardia”; Table 2 | 73 total events; 38 ON vs 35 OFF; no meaningful change in event count, but intensity reduced 18% (95% CI 15%–22%, P<.0001) | Do not summarize as all cardiorespiratory endpoints improving |
| Adverse events | Results, paragraph after Figures 2–3 / discussion | Authors state no adverse events, adverse device effects or unanticipated problems were encountered | Bounded to n=36, this protocol and observation window; not proof of general/long-term safety |

**Key reading rule:** Figure 2/3 are participant flow; Table 2 is the event-level outcome table. Abstract percentages should be checked against the outcome-specific Results subsections, because event count, duration and intensity use different denominators/statistical models.

## E001-B — Bloch-Salisbury et al. 2009

**원문:** Bloch-Salisbury E, Indic P, Bednarek F, Paydarfar D. *Stabilizing immature breathing patterns of preterm infants using stochastic mechanosensory stimulation.* J Appl Physiol. 2009;107(4):1017–1027. DOI: 10.1152/japplphysiol.00058.2009. PMID 19608934; PMCID PMC2763836.  
URL: https://pmc.ncbi.nlm.nih.gov/articles/PMC2763836/

| Claim | Exact locator | Result / data to retain | Interpretation boundary |
|---|---|---|---|
| Population and design | Abstract; Methods, “Human Subjects” and “Experimental Protocol”; Table 1 | n=10 preterm infants; repeated 10-minute ON/OFF intervals; repeated-measures/test-retest design | Very small physiological study; not general infant soothing efficacy |
| Physical output | Abstract; Methods, “Vibrotactile Stimulation” | 30–60 Hz; 0.021 mm RMS displacement; 0.090 mm maximum displacement | RMS and maximum are different metrics; do not interchange |
| Surface uniformity | Methods, “Vibrotactile Stimulation” | Near-uniform surface displacement ±2% measured with a linear displacement transducer | Engineering method precedent, not a universal allowable tolerance |
| IBI variance | Results, “Variance of IBIs Was Reduced During Stimulation”; Figure 2; Table 2 | ON 0.46 s² vs OFF 0.91 s²; approximately 50% reduction, P=.003 | Respiratory physiology endpoint, not calming or sleep improvement |
| Prolonged interbreath intervals | Results, “Incidence of Prolonged IBIs Was Reduced During Stimulation”; Table 2 / Figure 6 summary | IBI >5 s incidence 18.6/h ON vs 37.1/h OFF | This definition differs from apnea definitions in other studies |
| Oxygen desaturation time | Abstract; Table 2; Figure 6 summary | O₂ desaturation time 0.68% of total time ON vs 1.92% OFF; abstract reports approximately 65% reduction, P=.04 | Do not interpret as evidence of general infant respiratory or sleep safety |
| Sleep/wake state | Results, “Sleep state and EEG frequency content at stimulation transition”; Table 2 | Sleep/wake state did not significantly change at ON/OFF transitions; Table 2 reports quiet sleep 61.1% OFF vs 60.1% ON | Study assessed physiological stability in preterm infants; not a test of infant settling |
| Adverse-event status | Full-text Results/Discussion | No separately standardized adverse-event summary is identified in the extracted sections; do not code “none” based only on absence of a highlighted event | Status remains “not clearly reported in the extracted source” until a complete source check establishes otherwise |

**Key reading rule:** Table 1 = subject characteristics; Table 2 = respiratory, cardiac, behavioral and EEG measurements; Figures 1–2 = protocol/IBI examples and variance; Figure 6 = summary. Exact numerical results above are located at the named Results subsections and table/figure, not inferred from figure appearance.

## E001-C — Zuzarte et al. 2017

**원문:** Zuzarte I, Indic P, Barton B, Paydarfar D, Bednarek F, Bloch-Salisbury E. *Vibrotactile stimulation: A non-pharmacological intervention for opioid-exposed newborns.* PLOS ONE. 2017;12(4):e0175981. DOI: 10.1371/journal.pone.0175981. PMID 28426726; PMCID PMC5398650.  
URL: https://pmc.ncbi.nlm.nih.gov/articles/PMC5398650/

| Claim | Exact locator | Result / data to retain | Interpretation boundary |
|---|---|---|---|
| Population and design | Abstract; Methods, “Study Design” / “Clinical Characteristics”; Table 1 | 26 opioid-exposed newborns (>37 weeks), single-center prospective within-subject study; all receiving morphine for withdrawal | Not a healthy-infant or ordinary sleep/soothing study |
| Physical exposure | Abstract; Methods, mattress/stimulation characterization | 30–60 Hz; 10–12 μm RMS surface displacement; alternating 30-minute ON/OFF intervals over a 6–8 h session | Specific platform and clinical context; not a general safety range |
| Sample characteristics and concomitant treatment | Table 1 | Table reports gestational/post-conceptual age, weights, morphine/phenobarbital exposure, feeding, Finnegan scores and paired trials | Clinical treatment and time-varying care must remain in interpretation |
| Movement activity | Abstract; Results, “Condition and movement periods”; Table 2; Figure 3 | Mean absolute movement 40% OFF (CI 36–45) vs 26% ON (CI 23–30), P<.001; reported as 35% relative reduction / 14 percentage-point absolute reduction | Movement reduction is not synonymous with subjective calming, crying reduction or sleep improvement |
| Longer movement periods | Results, “Condition and movement periods”; Table 2; Figure 3 | Movement periods >30 s: 13 OFF vs 9 ON, P=.003; movement reduced in 23/26 subjects per Figure 3 caption | Keep duration-category results separate from total movement percentage |
| Respiratory and cardiac measures | Results, “Physiological measurements”; Table 2 | Mean respiratory rate 74 OFF vs 68 ON bpm (P=.023); tachypneic breaths 2669 vs 2184 (P=.024); eupneic breaths 1184 vs 1392 (P=.028); mean HR 137 vs 134 bpm (P=.016); HR variance P=.001 | These are physiologic state measures in a specific clinical population, not direct infant soothing outcomes |
| Oxygenation and temperature | Results, “Cardiac and blood-oxygenation saturation” and “Skin temperature” | No effect on SaO₂ (P=.544), average about 99%; mean axillary temperature about 36.8°C, P=.581 | “No change detected” is not proof of universal or long-term safety |
| Adverse events | Results / discussion; FDA De Novo Summary printed p.7 cross-check | FDA summary states no adverse events were reported and notes temperature/oxygen levels were maintained; primary paper's safety reporting must remain bounded to the studied cohort and period | FDA specifically says these endpoints were not appropriate to establish effectiveness for the intended indication, while they contributed to safety support |

**Key reading rule:** Table 1 = cohort characteristics; Table 2 = movement and cardiorespiratory measures; Figure 3 = subject-level movement change. The 35% movement reduction is not a validated settling endpoint.

## Cross-paper constraints

1. E001-A and E001-B are preterm physiological studies; E001-C is a small study of opioid-exposed newborns receiving pharmacologic treatment.
2. Frequency bandwidth, RMS displacement, maximum displacement, and measured surface uniformity must not be treated as interchangeable measures or universal safe values.
3. None of these three studies directly establishes that MAJUNG reduces crying, improves settling, or improves sleep in healthy infants.
4. An absent or limited adverse-event discussion must not be recoded as “no adverse events” or “safe”.
5. This audit identifies source locations but does not replace full methodological risk-of-bias review or journal-PDF page normalization.
