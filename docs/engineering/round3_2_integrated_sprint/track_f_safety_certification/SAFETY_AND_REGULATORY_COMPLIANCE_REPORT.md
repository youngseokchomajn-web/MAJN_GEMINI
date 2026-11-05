# Track F: Safety & Regulatory Certification Readiness Report
## Compliance Framework, Hazard Analysis, Acoustic/Vibration Safety Criteria, and Accredited Testing Lab Strategy

- **Sprint**: Round 3.2 Integrated Engineering Development Sprint
- **Track**: Track F — Safety & Certification Readiness
- **Document Identifier**: `MAJN-R3.2-TRK-F-REPORT-001`
- **Revision**: v1.0
- **Lead Investigator**: Antigravity (Independent Technical Reviewer)
- **Status**: COMPLETE / CERTIFICATION ROADMAP & FMEA ESTABLISHED
- **Date**: 2026-11-06

---

## 1. Executive Summary

Track F establishes the regulatory compliance baseline, infant safety criteria, risk mitigation mechanisms, and external testing protocol required for commercial release of the MAJN Smart Bassinet. Because MAJN is an electronic soothing product designed for direct, prolonged contact with sleeping infants, safety compliance is not merely an EMC/RF formality—it governs every aspect of the electrical, mechanical, and thermal design:
1. **Infant Thermal Safety**: Under IEC 62368-1 Table 38 and KC Child Product Standards, touch surfaces accessible to an infant must remain $\le 35.0^\circ\text{C}$ for continuous contact and outer plastic chassis $\le 40.0^\circ\text{C}$.
2. **Acoustic Sound Pressure Ceiling**: Clarifying the Round 3 literature confusion, 50.0dBA is formally defined as an internal design target derived from the 1997 AAP Hospital Nursery noise recommendations (measured at 30cm). Continuous sound level is capped at $L_{\text{eq}} \le 50.0\text{dBA}$ with an absolute transient limit of $L_{\text{max}} \le 65.0\text{dBA}$. The obsolete 75.0dBA figure is permanently eliminated.
3. **Infant Vibration Limits**: Harmonic motion is bound by frequency (30Hz ~ 120Hz), displacement ($A \le 18\mu\text{m}$), and acceleration ($a_{\text{RMS}} \le 0.12\text{g}$) under 5kg infant dummy load. A hard 30-minute run-time cutoff is enforced by hardware/firmware supervisors.
4. **FMEA Risk Mitigation**: The comprehensive FMEA register (`MAJN_INFANT_SAFETY_FMEA_REGISTER.csv`) addresses 12 failure modes, reducing the maximum Risk Priority Number (RPN) from 210 down to 16.
5. **Testing Lab Strategy**: A 12-test protocol (`EXTERNAL_LAB_TEST_PROCEDURE_MATRIX.csv`) outlines execution across Korean accredited testing labs (KTC, KTL, KTR) and international partners (SGS, Intertek).

---

## 2. Applicable Standards & Regulatory Scope

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                        MAJN PRODUCT REGULATORY & COMPLIANCE STACK                      │
├───────────────────────────────┬───────────────────────────────┬────────────────────────┤
│     Infant Physical Safety    │      Electrical & Thermal     │     Wireless & EMC     │
├───────────────────────────────┼───────────────────────────────┼────────────────────────┤
│ • ASTM F2194-22e1 (Bassinet)  │ • IEC / KC 62368-1 (Safety)   │ • KC KN 301 489 / KN32 │
│ • CPSC 16 CFR Part 1218       │ • KC Child Product Safety     │ • FCC Part 15B Class B │
│ • AAP Infant Sleep Guidelines │ • IEC 61000-4-2 (ESD ±8kV)    │ • FCC Part 15.247(BLE) │
│ • ISO 2631-1 (Vibration)      │ • USB-IF Type-C Standard      │ • KC KN 35 (Immunity)  │
└───────────────────────────────┴───────────────────────────────┴────────────────────────┘
```

### 2.1 ASTM F2194 & CPSC 16 CFR Part 1218
- **Scope**: Mandatory federal safety specification for bassinets and cradles.
- **Key Requirements**:
  * Mechanical stability (no tip-over under 20° tilt).
  * Mattress firmness and flat sleep surface ($<10^\circ$ incline).
  * Corner post and sidewall height to prevent entrapment or falling.
  * Absence of sharp edges or pinch points created by exciter vibration mechanisms.

### 2.2 KC Child Product Common Safety Standard (어린이제품 공통안전기준)
- **Scope**: South Korean statutory safety standard for products used by infants under 36 months.
- **Key Requirements**:
  * Hazardous substance prohibition (RoHS / REACH compliance for plastics and solder).
  * Battery safety and low-voltage protection ($< 24\text{V}$ SELV circuit).
  * Thermal contact restrictions: Sleep surface temperature must not exceed body temperature ($36.5^\circ\text{C}$).

---

## 3. Acoustic & Vibration Safety Protocol

### 3.1 Acoustic Sound Pressure Level (SPL) Limits
As proven in Round 3.1, the American Academy of Pediatrics (AAP) does not publish a statutory decibel cap for commercial white noise machines, but recommended in 1997 that hospital nursery and NICU ambient background sound levels not exceed 50dBA to protect developing auditory hair cells.
- **Engineering Specification**:
  * Continuous Equivalent Sound Level: $L_{\text{eq}} \le \mathbf{50.0\text{dBA}}$ measured at $30\text{cm}$ (infant ear distance).
  * Peak Maximum Transient Sound Level: $L_{\text{max}} \le \mathbf{65.0\text{dBA}}$ at $30\text{cm}$.
  * The historical 75.0dBA limit is permanently rejected due to sensorineural hearing fatigue risks.
- **Hardware & Firmware Enforcement**:
  * Master volume register clamped at `-3.5dBFS` (`0x37`).
  * Digital high-frequency cutoff filter ($f_{\text{c}} = 8.0\text{kHz}$) in I2S audio stream.

### 3.2 Vibration Acceleration & Displacement Protocol
Reconciling Kimura et al. (2017) and human biodynamic vibration standards (ISO 2631-1):
- **Distinction between Macro-Rocking and Acoustic Micro-Vibration**:
  * 0.5Hz rocking (Kimura 2017) involves millimeter-scale mechanical swaying ($2.4\sim 7.5\text{mm}$).
  * 45Hz acoustic soothing utilizes micro-vibrations ($10\sim 18\mu\text{m}$) to stimulate somatic mechanoreceptors without shaking the infant's brain or cervical spine.
- **Harmonic Formulation**:
  $$a_{\text{peak}} = (2\pi f)^2 A, \quad a_{\text{RMS}} = \frac{a_{\text{peak}}}{\sqrt{2}}$$
  * At $f = 45.0\text{Hz}$, $A = 15.0\mu\text{m} \implies a_{\text{peak}} = 1.20\text{m/s}^2 \approx \mathbf{0.122\text{g}_{\text{peak}}}$, $a_{\text{RMS}} \approx \mathbf{0.086\text{g}_{\text{RMS}}}$.
  * Upper Safety Threshold: $a_{\text{RMS}} \le \mathbf{0.12\text{g}}$ under a calibrated 5kg infant anthropomorphic dummy load.
- **Automatic 30-Minute Run-Time Limit**:
  * Continuous vibration terminates automatically after 30 minutes, preventing habituation or sensory overstimulation.

---

## 4. Failure Mode and Effects Analysis (FMEA) Summary

The comprehensive FMEA register (`MAJN_INFANT_SAFETY_FMEA_REGISTER.csv`) systematically reviews 12 failure modes across Power, Audio, Control, Mechanical, and Thermal domains.

```
========================================================================================
[FMEA RISK REDUCTION SUMMARY]
  - Total Failure Modes Evaluated: 12
  - Maximum Initial RPN:           210 (FMEA-02: MLCC collapse / FMEA-03: Back-EMF)
  - Average Initial RPN:           158
  - Maximum Mitigated Final RPN:   16  (FMEA-01: Inductor stress / FMEA-09: LDO heat)
  - Average Mitigated Final RPN:   7.5
  - Risk Reduction Ratio:          > 95% RPN elimination across all critical modes
========================================================================================
```

Key Mitigations Incorporated into PCB #0006 Baseline:
1. **FMEA-01 (Inductor Saturation)**: Upgraded L1 to $I_{\text{sat}} = 5.0\text{A}$ (SWPA8040S); firmware volume clamped at -3.5dBFS.
2. **FMEA-03 (BTL Back-EMF Surge)**: BAT54S dual Schottky clamp diode array (D4~D7) clamps inductive kickback to PVDD and GND.
3. **FMEA-05 (Bootloader Trap & Loud Pop)**: Relocated PDN to non-strapping GPIO13 with 10kΩ pull-down to GND.
4. **FMEA-06 (Amplifier Over-Temperature)**: Real-time GPIO35 hardware ISR clamps Boost and Amp within $<5\mu\text{s}$.

---

## 5. Accredited Testing Lab Strategy & Certification Roadmap

### 5.1 Domestic & International Test Lab Allocation
- **Electrical Safety & KC Certification (KC 62368-1)**: Korea Testing Certification (KTC) or Korea Testing Laboratory (KTL).
- **Child Product Common Safety (ASTM F2194 / KC Child)**: Korea Conformity Laboratories (KCL) or FITI Testing & Research Institute.
- **Wireless RF & EMC (KC KN 301 489 / FCC Part 15B/15.247)**: SGS Korea, KTL, or Intertek.

### 5.2 Mandatory Firmware Test Modes Required for Testing
To support external laboratory certification, the firmware includes three dedicated, non-volatile test modes selectable over the UART header:
1. **Mode 1: Continuous RF Radiated Emission Mode**: Transmits continuous BLE modulated carrier at maximum power (+20dBm) on low, mid, and high channels (2402MHz, 2440MHz, 2480MHz).
2. **Mode 2: Thermal Saturation Mode**: Drives continuous 45Hz vibration at maximum clamped amplitude (0.50f) for 4 hours inside a 40°C thermal chamber.
3. **Mode 3: Single-Fault Injection Mode**: Bypasses software retry loops to allow laboratory evaluation of hardware fuse, TVS, and thermal cutout behavior.

---

## 6. Summary of Track F Deliverables

1. `SAFETY_AND_REGULATORY_COMPLIANCE_REPORT.md` (This document)
2. `MAJN_INFANT_SAFETY_FMEA_REGISTER.csv`: 12-mode detailed quantitative FMEA register.
3. `EXTERNAL_LAB_TEST_PROCEDURE_MATRIX.csv`: Complete 12-test laboratory execution matrix with pass/fail criteria.
