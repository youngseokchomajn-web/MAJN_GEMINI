# Track E: PCB #0006 Engineering Design Input Specification
## Master Requirements, Circuit Block Rules, DFT/DFM Guidelines, and Component Architecture for Next-Generation Layout

- **Sprint**: Round 3.2 Integrated Engineering Development Sprint
- **Track**: Track E — PCB #0006 Design Input Package
- **Document Identifier**: `MAJN-R3.2-TRK-E-SPEC-001`
- **Revision**: v1.0
- **Lead Investigator**: Antigravity (Independent Technical Reviewer)
- **Status**: COMPLETE / READY FOR CAD LAYOUT ENGAGEMENT
- **Date**: 2026-11-06

---

## 1. Scope & Objective

This document forms the binding Engineering Design Input Package (EDIP) for the layout and manufacturing preparation of PCB #0006. It incorporates the complete failure history of Prototype #0005 (`PCB_0005_FAILURE_ANALYSIS_REPORT.md`), resolves the baseline schematic discrepancies (Track A), integrates hardened power delivery circuits (Track B), accounts for the new firmware hardware abstraction (Track C), and provides full testability (DFT) for production verification.

---

## 2. Reflection of PCB #0005 Failure Lessons

| Failure ID | Prototype #0005 Root Cause | PCB #0006 Mandatory Architectural Countermeasure |
| :--- | :--- | :--- |
| **MECH-01** | VBUS 5V voltage droop ($<4.0\text{V}$) due to boost peak currents exceeding 3.5A. | 1. Firmware hard power ceiling (-3.5dBFS / 0.50f scale).<br>2. VBUS inrush TVS clamp (SMAJ5.0A).<br>3. In-line current shunt pads for real-time current logging. |
| **MECH-02** | BTL inductive kickback ($V = -L di/dt$) from exciter voice coils causing TAS5805M OCP faults. | 1. Dual Schottky clamping diode array (`BAT54S` D4~D7) on all 4 BTL output pins.<br>2. RC snubber networks on output traces. |
| **MECH-03** | PVDD boost startup voltage overshoot ($>15\text{V}$) under light load, degrading 10V/25V MLCCs. | 1. Bleeder resistor $R_{\text{BLEED}}$ ($1.5\text{k}\Omega$ 1206) across PVDD.<br>2. Upgrade PVDD MLCCs (C8, C9) to 1210 22µF 35V/50V X7R. |
| **MECH-04** | Direct copper short between boost output and amplifier PVDD prevented modular bring-up. | Physical isolation jumper $R_{\text{ISO1}}$ (SMD 2512 0Ω pad, $\ge 5\text{A}$ rating) inserted between boost output and amp rail. |
| **MECH-05** | TAS5805M I2C bus lockup held SDA low indefinitely after communication glitches. | 1. Firmware 9-clock recovery routine on SCL.<br>2. Hardware I2C pull-up resistors verified at 5.1kΩ to 3.3V. |
| **MECH-06** | TAS5805M PDN tied to ESP32 MTDO (GPIO15) with 10kΩ pull-up, trapping bootloader in debug mode. | Reassigned `AMP_PDN` to **GPIO13 (Pin 16)** with a **10kΩ pull-down to GND** (R13). |

---

## 3. Block-by-Block Circuit Specifications

```
  ┌─────────────────────────────────────────────────────────────────────────────┐
  │                            MAJN PCB #0006 SYSTEM TOPOLOGY                   │
  └─────────────────────────────────────────────────────────────────────────────┘
   USB Type-C (5V) ──────► [TVS D1] ───┬──► [LDO U2: 3.3V] ──► ESP32 (U1) & IMU (U5)
                                       │
                                       └──► [Boost U3: 12V] ──► [R_BLEED]
                                                                     │
                                                                 [R_ISO1: 0Ω]
                                                                     │
                                                                     ▼
   ESP32 (GPIO13: PDN) ───────────────────────────────────► TAS5805M Amp (U4)
   ESP32 (GPIO35: FAULTz) ◄─── [R12: 4.7kΩ to 3.3V] ───────┤ (PVDD = 12.17V)
   ESP32 (I2S Clocks & Audio) ────────────────────────────►│
                                                            │
                                                     [BAT54S Clamps D4~D7]
                                                            │
                                                            ▼
                                                   2x TEAX14C02-8 (16Ω BTL)
```

### 3.1 Power Section
- **Boost Converter IC (U3)**: MPS MP3426DL (QFN-14).
- **Inductor (L1)**: Sunlord SWPA8040S4R7MT ($4.7\mu\text{H} \pm 20\%$, $I_{\text{sat}} \ge 5.0\text{A}$, $I_{\text{rms}} \ge 4.2\text{A}$, $\text{DCR} \le 18\text{m}\Omega$). Footprint accommodates both 6045 and 8040 packages.
- **Schottky Diode (D3)**: MDD SS34 (SMA, 3A 40V, low $V_f \le 0.45\text{V}$).
- **Feedback Network**: Upper resistor $R_1 = 143\text{k}\Omega \pm 1\%$ (0603), Lower resistor $R_2 = 16.0\text{k}\Omega \pm 1\%$ (0603). Yields nominal $V_{\text{out}} = 12.17\text{V}$.
- **Frequency Setting**: Resistor $R_9 = 82\text{k}\Omega \pm 1\%$ (0603), configuring $f_{\text{sw}} \approx 1.22\text{MHz}$.
- **Decoupling MLCCs**: Output filtering composed of $2\times 22\mu\text{F}$ 35V X7R 1210 capacitors (C8, C9) plus $1\times 100\text{nF}$ 0603 (C10) placed immediately adjacent to U4 PVDD pins.

### 3.2 Audio Amplifier Section
- **Amplifier IC (U4)**: TI TAS5805MPWPR (HTSSOP-28 with exposed thermal pad EP).
- **Pin 3 Interface (`AMP_FAULTz_ADR`)**:
  * Connected to $R_{12} = 4.7\text{k}\Omega \pm 1\%$ (0603) pull-up to `VCC_3V3`.
  * Routed directly to ESP32 **GPIO35 (Pin 7)**.
  * EasyEDA Net Name: `AMP_FAULTz_ADR`.
- **Pin 12 Interface (`AMP_PDN`)**:
  * Connected to $R_{13} = 10\text{k}\Omega \pm 1\%$ (0603) pull-down to `GND`.
  * Routed directly to ESP32 **GPIO13 (Pin 16)**.
  * EasyEDA Net Name: `AMP_PDN`.
- **BTL Clamping Array**: Four dual-series Schottky diodes (BAT54S, SOT-23) connected on `AMP_OUT_A+`, `AMP_OUT_A-`, `AMP_OUT_B+`, `AMP_OUT_B-`. Cathodes tied to `PVDD_12V_AMP`, anodes tied to `GND`.

### 3.3 MCU & Sensor Section
- **Microcontroller (U1)**: Espressif ESP32-WROOM-32E-N8 (or pin-compatible 32UE with external U.FL antenna).
- **LDO Regulator (U2)**: Diodes Inc AP2112K-3.3TRG1 (SOT-25-5, 600mA). Maximized copper thermal stitching on GND pins.
- **6-Axis IMU (U5)**: STMicroelectronics LSM6DSOXTR (LGA-14L, 2.5x3.0mm). Connected via SPI bus with dedicated CS on GPIO5.

---

## 4. Design for Testability (DFT) & Manufacturing (DFM) Rules

### 4.1 Test Point Infrastructure (DFT)
- All 15 defined test points (TP-01 through TP-15, see `PCB0006_TEST_POINT_AND_MEASUREMENT_PLAN.csv`) must be placed on the **Top copper layer** with minimum $1.0\text{mm}$ diameter circular surface pads.
- High-voltage switching nodes (SW, BST) must include an adjacent ground pad spaced exactly $2.54\text{mm}$ center-to-center to allow coaxial spring-clip probing.
- BTL differential output test points (`TP_OUT_A+` / `TP_OUT_A-` and `TP_OUT_B+` / `TP_OUT_B-`) must be silk-screened with the mandatory warning: **"DIFF PROBE ONLY / NO GND CLIP"**.

### 4.2 Single-Sided SMT Preference (DFM / Economic PCBA)
- In Prototype #0005, resistor R12 was placed on the Bottom layer, forcing expensive double-sided SMT processing.
- In PCB #0006, all passive components (R12, R13, decoupling caps) MUST be placed on the **Top layer**, allowing standard JLCPCB Economic PCBA processing and reducing manufacturing turn-around time.

### 4.3 Thermal Relief & Ground Planes
- Layer Stackup: 4-layer board (Top Signal/Power, Inner 1 Solid GND, Inner 2 Power/Signal, Bottom Signal/GND).
- Exposed Pads (U4 TAS5805M EP and U3 MP3426 EP) must include a $4\times 4$ thermal via array ($0.3\text{mm}$ drill, $0.6\text{mm}$ diameter) stitched directly into the solid Inner 1 ground plane.

---

## 5. Component Obsolescence & Alternate Sources

| Component | Primary MPN | LCSC C-ID | Alternate 1 (Drop-In) | Alternate 2 (Drop-In) | Risk Level |
| :--- | :--- | :---: | :--- | :--- | :---: |
| **Audio Amp** | TAS5805MPWPR | C478472 | TAS5825MPWPR (Pin-compatible) | TAS5806MDCPR (HTSSOP-28) | LOW |
| **Boost IC** | MP3426DL-LF-Z | C133224 | FP6296XR (SOP-8, layout diff) | TPS61088RHLR (QFN-20) | MEDIUM |
| **LDO 3.3V** | AP2112K-3.3TRG1| C51118 | RT9193-33GB (SOT-23-5, 300mA) | ME6211C33M5G (SOT-23-5, 500mA) | LOW |
| **Inductor** | SWPA8040S4R7MT | C38117 | Coilcraft MSS1278-472MLD | Sunlord SWPA6045S4R7NT | LOW |
| **Schottky** | SS34 (SMA) | C8678 | B340A-13-F (SMA) | SK34 (SMA) | LOW |
| **6-Axis IMU**| LSM6DSOXTR | C481766 | LSM6DS3TR-C (LGA-14) | BMI270 (LGA-14, SPI) | LOW |

---

## 6. Design Input Package Deliverables Summary

1. `PCB0006_DESIGN_INPUT_SPECIFICATION.md` (This document)
2. `PCB0006_SCHEMATIC_NETLIST_TARGET.json`: Machine-readable target netlist with verified pin connections.
3. `PCB0006_BILL_OF_MATERIALS_TARGET.csv`: Manufacturing-ready BOM with verified LCSC C-IDs and footprints.
4. `PCB0006_TEST_POINT_AND_MEASUREMENT_PLAN.csv`: Comprehensive 15-point bench measurement and probing plan.
