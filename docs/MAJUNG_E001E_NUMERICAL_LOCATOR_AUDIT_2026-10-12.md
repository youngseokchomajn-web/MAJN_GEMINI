# E001-E Bloch-Salisbury 2023 RCT — Numerical Source Locator Audit
Date: 2026-10-12

## Primary source
Bloch-Salisbury E, Wilson JD, Rodriguez N, et al. *Efficacy of a Vibrating Crib Mattress to Reduce Pharmacologic Treatment in Opioid-Exposed Newborns: A Randomized Clinical Trial.* JAMA Pediatrics. 2023;177(7):665–674. DOI: 10.1001/jamapediatrics.2023.1077. PMID: 37184872. PMCID: PMC10186209.

- Publisher full text: https://jamanetwork.com/journals/jamapediatrics/fullarticle/2804943
- PMC full text: https://pmc.ncbi.nlm.nih.gov/articles/PMC10186209/
- Locator convention: article section/table/figure labels are primary locators here. The publisher HTML’s text line ranges below are a secondary machine-readable locator, not journal page numbers.

## Quantitative claims and locators

| Claim | Exact value | Primary locator | Publisher HTML locator | Interpretation boundary |
|---|---|---|---|---|
| Enrolled / randomized | 208 dyads; 104 TAU and 104 SVS | Abstract; Methods; Figure 1 participant flow | Abstract around lines 220–225; Figure 1 at lines 99–106 | Do not confuse randomized/enrolled with analyzed |
| Analyzed cohort | 181 total: TAU 87, SVS 94 | Abstract; Results; Figure 1; Table 1 | Table 1 at lines 116–128; Results participant flow near lines 295–315 | 27 did not complete hospitalization at study sites; analyzed cohort differs from full randomized cohort |
| Prespecified primary outcomes | Morphine treatment administration (AMT), cumulative morphine dose (CMD), hospital length of stay | Abstract “Main Outcomes and Measures”; Methods “Outcomes” | Lines 223–224 and 258–265 | These are not crying, settling, sleep or comfort endpoints |
| Overall morphine treatment rate | TAU 31/87 (35.6%); SVS 29/94 (30.9%); P=.60 | Results; Table 2, row “Administration of morphine treatment” | Table 2 lines 329–340; abstract/results around line 225 | Overall randomized-group difference is not statistically significant |
| Exposure-duration association with AMT | Adjusted OR 0.88 per additional hour/day; 95% CI 0.81–0.93 | Results; Table 3, AMT (n=181), “Time SVS on (h/d)” | Lines 347–362 | Dose/exposure association is distinct from randomized assignment effect; observational exposure duration may be affected by use patterns |
| Treated cohort outcomes | 60 infants received morphine; adjusted CMD and LOT analyses showed no significant differences between conditions in the treated cohort | Results, “Infants Treated With Morphine”; Table 3 | Lines 385–386 | Keep the full treated cohort result distinct from responder subgroup |
| Responder subgroup | 32 infants completed treatment within 21 days: 17 SVS, 15 TAU; HR 1.96 (95% CI 1.01–3.81); 3.18 fewer treatment days; 1.76 mg/kg less cumulative morphine (95% CI −3.02 to −0.50) | Results; Figure 2B; eTable 3 in Supplement 2 | Lines 387–389; Figure 2 description at 390–398 | Conditional/post-hoc subgroup result; not a positive overall primary result |
| Nonresponder subgroup | No significant difference in CMD or LOT among infants treated for more than 21 days | Results; eTable 4 in Supplement 2 | Line 389 | Explicitly bounds the responder finding |
| SVS discontinuation observation | Among 105 infants who received SVS, 58 had it turned off 12–24 h before anticipated discharge; 6/58 (10.3%) met criteria for pharmacotherapy within 24 h | Methods safety protocol; Results paragraph immediately before Table 2 | Protocol at line 252; results at lines 327–328 | Observation under a protocol, not proof of rebound or causality |
| Sample-size caveat | Sample size was not recalculated post hoc after the primary outcomes shifted away from Finnegan score | Methods, “Sample Size Calculation” | Lines 263–265 | Do not imply the study was prospectively powered for every secondary/subgroup analysis |

## Adverse-event and safety coding

- **Study-specific observation:** The paper describes a planned pre-discharge SVS-off observation period and reports 6/58 infants meeting pharmacotherapy criteria within 24 hours after shutdown.
- **Not established:** That observation alone does not establish rebound, withdrawal caused by stopping SVS, or device-related harm.
- **Do not encode:** “No adverse events” or “safe for healthy infants” unless a separately defined adverse-event analysis and population-specific evidence support that exact statement.
- **FDA cross-check:** FDA’s De Novo Summary, printed p.7, notes that the 2017 study’s endpoints were not suitable to establish effectiveness for the intended indication, while adverse-event, thermoregulation and oxygen-desaturation information contributed to safety support. This supports keeping safety and effectiveness evidence streams separate.

## Audit conclusion

The primary result, exposure-duration analysis, treated-cohort analysis, responder subgroup, nonresponder subgroup and shutdown observation now have separate traceable locations. This audit does not make the subgroup findings confirmatory and does not establish MAJUNG efficacy or safety for general infants.
