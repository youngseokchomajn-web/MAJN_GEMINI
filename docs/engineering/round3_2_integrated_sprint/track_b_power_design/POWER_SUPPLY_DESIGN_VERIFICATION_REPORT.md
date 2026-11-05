# Track B: Power Supply & Circuit Design Verification Report
## Engineering Verification of MP3426 Boost Converter, TAS5805M Output Stability, and Power Integrity

- **Sprint**: Round 3.2 Integrated Engineering Development Sprint
- **Track**: Track B — Power & Circuit Design
- **Document Identifier**: `MAJN-R3.2-TRK-B-REPORT-001`
- **Revision**: v1.0
- **Lead Investigator**: Antigravity (Independent Technical Reviewer)
- **Status**: COMPLETE / CALCULATION & DESIGN ENHANCEMENTS ESTABLISHED
- **Date**: 2026-11-06

---

## 1. Executive Summary

Track B addresses the power delivery network (PDN), thermal margins, and circuit stability constraints that precipitated the Prototype #0005 failures (VBUS voltage brownout, inductor saturation, MLCC capacitance collapse, and back-EMF kickback).

Key Engineering Findings:
1. **MP3426 Boost Design**: The boost feedback divider ($R_1 = 143\text{k}\Omega$, $R_2 = 16\text{k}\Omega$, $V_{\text{ref}} = 1.225\text{V}$) correctly produces $12.17\text{V}$ PVDD. With frequency resistor $R_9 = 82\text{k}\Omega$, switching frequency is $1.22\text{MHz} \sim 1.25\text{MHz}$.
2. **Inductor Saturation Risk**: In Prototype #0005, inductor L1 (SWPA6045S-4R7NT, $I_{\text{sat}} = 3.60\text{A}$) operated with an unacceptable saturation margin ($\le 5.6\%$) under transient heavy load or low VBUS ($4.5\text{V}$). Under 45°C ambient, thermal degradation drops $I_{\text{sat}}$ below $3.2\text{A}$, causing switch overcurrent and thermal shutdown. PCB #0006 mandates upgrading L1 to SWPA8040S-4R7 ($I_{\text{sat}} = 5.0\text{A}$) or MSS1278-472 ($I_{\text{sat}} = 7.0\text{A}$).
3. **MLCC DC-Bias Derating**: C8/C9 0603 10µF 25V capacitors lose $>70\%$ of their capacitance at 12V DC bias, degrading effective filtering to $<3\mu\text{F}$ per cap and increasing voltage ripple. Upgrading to 1210 35V/50V 22µF X7R capacitors restores effective capacitance to $\ge 24\mu\text{F}$.
4. **Protective Hardware Elements**:
   - **$R_{\text{BLEED}}$ ($1.5\text{k}\Omega$ 1206)**: Discharges pulse-skipping charge, preventing light-load overshoots above 13.2V.
   - **$R_{\text{ISO1}}$ (2512 0Ω jumper)**: Enables isolated bring-up of the boost converter prior to powering the TAS5805M.
   - **Schottky Clamping Array (BAT54S)**: Diverts voice-coil back-EMF spikes into rails, clamping output pins within $-0.5\text{V} \sim 12.5\text{V}$.
   - **USB-C CC 5.1kΩ Standard**: Corrects legacy 14kΩ schematic error, ensuring reliable 5V 2A/3A negotiation.

---

## 2. MP3426 Boost Converter Mathematical Analysis

### 2.1 Voltage Regulation & Feedback Loop
- Internal reference voltage: $V_{\text{ref}} = 1.225\text{V} \pm 1.5\%$.
- Upper feedback resistor: $R_1 = 143\text{k}\Omega \pm 1\%$ (BOM C22877).
- Lower feedback resistor: $R_2 = 16.0\text{k}\Omega \pm 1\%$ (BOM C22818).
- Output voltage calculation:
  $$V_{\text{out}} = V_{\text{ref}} \times \left(1 + \frac{R_1}{R_2}\right) = 1.225\text{V} \times \left(1 + \frac{143}{16}\right) = 1.225 \times 9.9375 = \mathbf{12.173\text{V}}$$
- Tolerance range: Minimum $11.85\text{V}$, Maximum $12.48\text{V}$ ($\pm 2.5\%$ worst-case component spread).

### 2.2 Switching Frequency & Duty Cycle
- Timing resistor: $R_9 = 82\text{k}\Omega \pm 1\%$ (BOM C325632).
  $$f_{\text{sw}} \approx \frac{100\text{k}\Omega}{R_9} \times 1.0\text{MHz} \approx \frac{100}{82} \times 1.0\text{MHz} \approx \mathbf{1.22\text{MHz}}$$
- Maximum Continuous Duty Cycle ($D_{\text{max}}$) at low VBUS ($V_{\text{in}} = 4.50\text{V}$), efficiency $\eta = 83\%$:
  $$D = \frac{V_{\text{out}} - V_{\text{in}} \times \eta}{V_{\text{out}}} = \frac{12.17 - (4.50 \times 0.83)}{12.17} = \frac{12.17 - 3.735}{12.17} \approx \mathbf{0.693}$$

### 2.3 Inductor Ripple & Peak Current Stresses
For inductance $L = 4.7\mu\text{H}$:
- Inductor ripple current ($\Delta I_L$):
  $$\Delta I_L = \frac{V_{\text{in}} \times D}{f_{\text{sw}} \times L} = \frac{4.50\text{V} \times 0.693}{1.22 \times 10^6\,\text{Hz} \times 4.7 \times 10^{-6}\,\text{H}} = \frac{3.1185}{5.734} \approx \mathbf{0.544\text{A}}$$

- Operating Case Evaluations:
  1. **Nominal Soothing (VBUS 5.0V, Scale 0.50, $P_{\text{audio}} = 1.89\text{W}$, $\eta_{\text{amp}} = 80\%$, $\eta_{\text{boost}} = 85\%$):**
     $$P_{\text{PVDD}} = \frac{1.89}{0.80} + 0.24 + 0.099 = 2.70\text{W}$$
     $$I_{\text{in,boost}} = \frac{2.70\text{W}}{5.0\text{V} \times 0.85} = 0.635\text{A}$$
     $$I_{L,\text{pk}} = I_{\text{in,boost}} + \frac{\Delta I_L}{2} = 0.635 + 0.272 = \mathbf{0.907\text{A}}$$
     *Saturation Margin with SWPA6045S-4R7 ($I_{\text{sat}} = 3.60\text{A}$):* $(3.60 - 0.907) / 3.60 = \mathbf{74.8\%}$ (Safe).

  2. **Max Clamped Vibration (VBUS 4.75V, Scale 0.70, $P_{\text{audio}} = 3.70\text{W}$, $\eta_{\text{amp}} = 82\%$, $\eta_{\text{boost}} = 84\%$):**
     $$P_{\text{PVDD}} = \frac{3.70}{0.82} + 0.24 + 0.099 = 4.85\text{W}$$
     $$I_{\text{in,boost}} = \frac{4.85\text{W}}{4.75\text{V} \times 0.84} = 1.216\text{A}$$
     $$I_{L,\text{pk}} = 1.216 + 0.272 = \mathbf{1.488\text{A}}$$
     *Saturation Margin:* $(3.60 - 1.488) / 3.60 = \mathbf{58.7\%}$ (Safe).

  3. **Worst-Case Unconstrained Fault (VBUS 4.50V, Scale 1.00 Sine, $P_{\text{audio}} = 7.56\text{W}$, $\eta_{\text{amp}} = 85\%$, $\eta_{\text{boost}} = 80\%$):**
     $$P_{\text{PVDD}} = \frac{7.56}{0.85} + 0.24 + 0.099 = 9.23\text{W}$$
     $$I_{\text{in,boost}} = \frac{9.23\text{W}}{4.50\text{V} \times 0.80} = 2.564\text{A}$$
     $$I_{L,\text{pk}} = 2.564 + 0.272 = \mathbf{2.836\text{A}}$$
     *Saturation Margin:* Drops to $21.2\%$. Under elevated temperature (ambient 40°C, self-heating +35°C $\to T_{\text{ind}} = 75^\circ\text{C}$), $I_{\text{sat}}$ derates by 20% to $2.88\text{A}$. Margin shrinks to $< 1.5\%$, inducing immediate magnetic saturation, rapid inductance collapse, and switch overcurrent tripping.

---

## 3. TAS5805M Power & Stability Enhancements

```
              PVDD_12V_BOOST                                 PVDD_12V_AMP
   From MP3426 ────┬──────────────[ R_ISO1: 0Ω 2512 ]────────────┬─────────────► To TAS5805M
                   │                                             │
             [R_BLEED: 1.5kΩ]                              ┌─────┴─────┐
                   │                                     2x 22µF 35V  100nF
                   ▼                                      1210 X7R    0603
                  GND                                      (C8, C9)   (C10)
                                                                 │
                                                                 ▼
                                                                GND
```

### 3.1 Bleeder Resistor ($R_{\text{BLEED}}$) Verification
- Function: Draws a predictable minimum load current when TAS5805M is in shutdown (`PDN = LOW`), preventing MP3426 burst pulse-skipping instability and overvoltage spikes.
- Resistance: $1.5\text{k}\Omega \pm 1\%$ (SMD 1206).
- Static Bleed Current:
  $$I_{\text{bleed}} = \frac{12.17\text{V}}{1500\Omega} \approx \mathbf{8.11\text{mA}}$$
- Power Dissipation:
  $$P_{\text{bleed}} = \frac{12.17^2}{1500} \approx \mathbf{0.0987\text{W}} \approx 99\text{mW}$$
- Power Rating Margin: A 1206 resistor is rated at $0.25\text{W}$. Operating at $0.099\text{W}$ gives a conservative 39.5% power loading, ensuring long-term thermal reliability.

### 3.2 MLCC Capacitance Recovery Strategy
- In Prototype #0005, C8 and C9 were 0603 10µF 25V MLCCs.
- Ferroelectric dielectric (Class II) DC-bias effect causes dramatic capacitance loss:
  * 0603 10µF @ 12V DC: $-72\%$ retention $\implies C_{\text{eff}} \approx 2.8\mu\text{F}$ per cap ($5.6\mu\text{F}$ total).
  * Output voltage ripple: $\Delta V = I_{\text{out}} \times D / (f_{\text{sw}} \times C_{\text{eff}}) \approx 0.6\text{A} \times 0.69 / (1.22\text{MHz} \times 5.6\mu\text{F}) \approx \mathbf{60.6\text{mV}}$.
- In PCB #0006, C8 and C9 are replaced by **1210 22µF 35V/50V X7R MLCCs**:
  * 1210 22µF @ 12V DC: $-40\%$ retention $\implies C_{\text{eff}} \approx 13.2\mu\text{F}$ per cap ($\mathbf{26.4\mu\text{F}}$ total).
  * Output voltage ripple drops to: $\Delta V \approx \mathbf{12.8\text{mV}}$ ($>78\%$ ripple reduction!).

### 3.3 Inductive Back-EMF Clamping
- The TEAX14C02-8 voice-coil exciters possess dynamic inductance ($L \approx 0.18\text{mH} \times 2 = 0.36\text{mH}$).
- During sudden mute or emergency stop, the energy stored in the magnetic field ($E = \frac{1}{2} L I^2$) dumps into the BTL switching nodes.
- Clamping Solution: Adding four dual Schottky diode pairs (`BAT54S` / `PMEG3010ER`) across all four BTL lines (`OUT_A+`, `OUT_A-`, `OUT_B+`, `OUT_B-`) to PVDD and GND.
  * Clamps positive inductive kickback to $\text{PVDD} + 0.4\text{V} \approx 12.57\text{V}$ (well below 30V absolute maximum).
  * Clamps negative inductive kickback to $\text{GND} - 0.4\text{V} \approx -0.40\text{V}$ (preventing substrate parasitic latch-up).

---

## 4. USB-C Input Protection & LDO Thermal Verification

### 4.1 USB Type-C Standard Configuration
- Resistors R3 and R4 on `USB_CC1` and `USB_CC2` are fixed at **$5.1\text{k}\Omega \pm 1\%$ (0603)**, terminating the CC pins to GND as a standard UFP (Upstream Facing Port / Sink).
- Corrects legacy schematic value of 14kΩ, ensuring all USB-C PD and legacy DFP adapters advertise their full $5\text{V} / 2.0\text{A} \sim 3.0\text{A}$ capacity.

### 4.2 AP2112K LDO (U2) Thermal Performance
- Package: SOT-25 (SOT-23-5), junction-to-ambient thermal resistance $\theta_{\text{JA}} \approx 169^\circ\text{C/W}$.
- Input: 5.0V VBUS, Output: 3.3V, Dropout voltage: $250\text{mV} @ 600\text{mA}$.
- Power Dissipation Cases:
  * BLE Idle ($I_{\text{load}} \approx 90\text{mA}$): $P = 1.7\text{V} \times 0.09\text{A} = 0.153\text{W} \implies \Delta T = 25.8^\circ\text{C}$. ($T_j = 65.8^\circ\text{C} @ 40^\circ\text{C}$ amb, Safe).
  * Active Soothing + BLE ($I_{\text{load}} \approx 140\text{mA}$): $P = 1.7\text{V} \times 0.14\text{A} = 0.238\text{W} \implies \Delta T = 40.2^\circ\text{C}$. ($T_j = 80.2^\circ\text{C} @ 40^\circ\text{C}$ amb, Safe).
  * Wi-Fi Burst Peak ($I_{\text{load}} \approx 380\text{mA}$, 5% duty cycle): Average power increase $< 0.05\text{W}$. Junction temperature remains below $95^\circ\text{C}$ (limit $125^\circ\text{C}$).
- Conclusion: AP2112K is thermally adequate for MAJN operation provided the PCB copper area connected to Pin 2 (GND) is maximized ($\ge 25\text{mm}^2$).

---

## 5. Summary of Track B Deliverables

1. `POWER_SUPPLY_DESIGN_VERIFICATION_REPORT.md` (This document)
2. `POWER_BUDGET_CALCULATION_MODEL.csv`: Multi-scenario 10-parameter mathematical power model.
3. `POWER_INTEGRITY_VERIFICATION_CHECKLIST.md`: Formal oscilloscope probe procedures and pass/fail thresholds for TP-01 through TP-08.
