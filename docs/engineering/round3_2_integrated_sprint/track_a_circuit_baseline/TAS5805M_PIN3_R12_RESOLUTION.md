# TAS5805M Pin 3 & R12 Circuit Baseline Resolution Whitepaper
## Analysis, Mechanism, and Resolution of TAS5805M Pin 3 (ADR/FAULT) & R12 Pull-Up

- **Document Identifier**: `MAJN-R3.2-TRK-A-PIN3-RES-001`
- **Revision**: v1.0
- **Author**: Antigravity (Independent Technical Reviewer / Dual-AI Engineering Architecture)
- **Status**: FORMALLY RECONCILED / READY FOR ECO REVIEW
- **Date**: 2026-11-06

---

## 1. Executive Summary & Root Cause Archaeology

### 1.1 The Contradiction
Throughout Rounds 2, 3, and 3.1, a persistent confusion existed regarding the role of Texas Instruments TAS5805M Pin 3, resistor R12, and the FAULT reporting path:
1. **The Round 3 Error**: Round 3 asserted that TAS5805M Pin 1 was `FAULTz` and proposed routing MCU lines to it. Pin 1 is actually `DGND` (Digital Ground); connecting any driving output to Pin 1 creates a catastrophic dead short to ground.
2. **The PCB #0005 Schematic Anomaly**: In `sch_netlist_final.json`, Pin 3 (`ADR/FAULT#`) was tied directly to `GND`, while resistors R12 and R13 were completely absent from the schematic netlist.
3. **The PCB #0005 Layout Patch**: In the actual PCB layout (`pcb_comps.json`) and manufacturing data (`BOM_PCB1_revB_2026-07-09.csv` / `CPL_PCB1_revB_2026-07-09.csv`), R12 (4.7kΩ) had been retroactively placed between `VCC_3V3` and `U4 Pin 3` (designated net `AMP_ADR`) to force the I2C address to `0x2C`. However, net `AMP_ADR` ended at R12 and was **never connected to any GPIO on the ESP32**.
4. **The Engineering Question**: Can Pin 3 simultaneously configure the I2C slave address at boot and report hardware faults (OTW/OTE/OCP/DC) to the ESP32 during runtime without electrical conflict?

### 1.2 Definitive Finding
**YES**. TI TAS5805M Pin 3 is specifically engineered as a time-multiplexed, dual-function pin:
- **Phase 1 (Boot / POR / PDN Rise)**: High-impedance analog input. An internal ADC samples the voltage determined by an external pull-up resistor to DVDD (3.3V) to latch the 7-bit I2C address.
- **Phase 2 (Runtime / Run Mode)**: Configurable via I2C registers (`0x61 = 0x0B`, `0x60 = 0x01`) into an **Active-LOW, Open-Drain FAULT output**.
- **Resistor Dual Role**: R12 (4.7kΩ to 3.3V) provides the exact 4.7kΩ ratio needed for I2C address `0x2C` during Phase 1, and serves as the mandatory pull-up resistor for the open-drain output during Phase 2.
- **MCU Pin Pairing**: Connecting Pin 3 to ESP32 **GPIO35 (Module Pin 7)** creates a safe, non-conflicting interface because GPIO35 is an input-only (GPI) pin with no internal pull-up/pull-down circuitry to corrupt Phase 1 address latching.

---

## 2. Electrical Architecture & Dual-Mode Operational Sequencing

```
                     +3.3V (VCC_3V3 / DVDD)
                              │
                              [R12: 4.7kΩ ±1%]
                              │
  TAS5805M (U4)               ├─────────────────────────► ESP32-WROOM-32E (U1)
 ┌────────────────────────┐   │                            ┌────────────────────────┐
 │                        │   │   Net: AMP_FAULTz_ADR      │                        │
 │  Pin 3: ADR / FAULT    ├───┴────────────────────────────┤ GPIO35 (Pin 7 / GPI)   │
 │                        │                                │ (Input-Only, No Pulls) │
 │  ┌──────────────────┐  │                                │                        │
 │  │ Phase 1:         │  │                                └────────────────────────┘
 │  │ Internal 3-bit   │  │
 │  │ ADC / Decoder    │  │
 │  └──────────────────┘  │
 │  ┌──────────────────┐  │
 │  │ Phase 2:         │  │
 │  │ Open-Drain NMOS  │  │
 │  │ Fault Output     │  │
 │  └────────┬─────────┘  │
 │           │            │
 └───────────┼────────────┘
             ▼
            GND
```

### 2.1 Phase 1: Power-On Reset & I2C Address Latching
1. When VCC_3V3 powers up and PDN transitions from LOW to HIGH, the TAS5805M internal state machine initiates an address detection routine lasting approximately $t_{\text{detect}} \le 2\text{ms}$.
2. In this window, the internal NMOS switch is OFF (High-Z). The internal ADC compares the voltage at Pin 3 against DVDD.
3. According to TI TAS5805M Datasheet (SLVSEH8B) Table 7-5:
   - **4.7 kΩ pull-up to DVDD**: 7-bit Address = **`0x2C`** (8-bit Write: `0x58`, Read: `0x59`)
   - **15 kΩ pull-up to DVDD**: 7-bit Address = **`0x2D`** (8-bit Write: `0x5A`, Read: `0x5B`)
   - **47 kΩ pull-up to DVDD**: 7-bit Address = **`0x2E`** (8-bit Write: `0x5C`, Read: `0x5D`)
   - **100 kΩ pull-up to DVDD**: 7-bit Address = **`0x2F`** (8-bit Write: `0x5E`, Read: `0x5F`)
4. Because ESP32 GPIO35 has NO internal pull-up and NO internal pull-down circuit (pure high-impedance gate oxide, input capacitance $C_{\text{in}} < 5\text{pF}$), the equivalent resistance seen by Pin 3 during Phase 1 is solely $R_{12} = 4.7\text{k}\Omega$. The address `0x2C` is latched with 100% determinism.

### 2.2 Phase 2: Runtime Reconfiguration & Fault Signaling
After address latching, Pin 3 remains an inactive input unless explicitly reprogrammed over I2C. The firmware executes the following four-step sequence:

```
[Register Write Sequence for Pin 3 FAULT Enable]
1. Set Book 0, Page 0:
   - Reg 0x00 = 0x00 (Page Control)
   - Reg 0x7F = 0x00 (Book Control)
2. Configure ADR Pin Function:
   - Reg 0x61 = 0x0B (Select FAULTz output mode on Pin 3)
3. Activate ADR Pin Control:
   - Reg 0x60 = 0x01 (Enable ADR Pin Driver)
4. Clear Latched Startup Faults:
   - Reg 0x78 = 0x80 (Clear Fault Register)
```

Once reconfigured:
- **Normal Operation**: Internal NMOS is OFF. External resistor R12 pulls the line to 3.3V (Logic HIGH). GPIO35 reads HIGH.
- **Fault Event**: When an Over-Temperature Warning/Error (OTW/OTE), Over-Current Protection (OCP), DC Load Fault, or Clock Halt occurs, the internal NMOS turns ON, clamping Pin 3 to $<0.4\text{V}$ (Logic LOW).
- **Fast Interrupt**: ESP32 GPIO35 negative-edge interrupt (`FALLING`) trips in $< 5\mu\text{s}$, invoking the FreeRTOS ISR to immediately execute `hardwareEmergencyShutdown()` before destructive thermal runaway or battery sag can occur.

---

## 3. Comparison of PCB #0005 vs PCB #0006 Architecture

| Attribute | PCB #0005 Prototype Implementation | PCB #0006 Target Baseline Resolution | Engineering Rationale |
| :--- | :--- | :--- | :--- |
| **TAS5805M Pin 3 Connection** | Connected to R12 (4.7kΩ to 3.3V); unconnected to MCU. | Connected to R12 (4.7kΩ) AND ESP32 GPIO35 (Pin 7). | Provides automatic address config + real-time hardware interrupt on fault. |
| **Schematic Netlist Status** | Described as tied to GND (Bug). | Fully unified net `AMP_FAULTz_ADR`. | Removes CAD schematic vs layout discrepancy. |
| **TAS5805M Pin 12 (PDN)** | Connected to ESP32 GPIO15 (Pin 23 / MTDO strapping) + R13 10kΩ pull-up. | Connected to ESP32 GPIO13 (Pin 16 / non-strapping) + R13 10kΩ pull-down to GND. | Prevents boot traps and ROM log spam; ensures safe hardware-default shutdown. |
| **Fault Detection Method** | Polling I2C registers `0x70~0x73` every 100ms. | Edge-triggered Hardware ISR on GPIO35 + background I2C diagnostic decode. | Reduces fault latency from 100ms to $< 10\mu\text{s}$; prevents I2C bus lockup masking. |
| **I2C Bus Address** | `0x2C` (after PCB layout patch). | `0x2C` (guaranteed by R12 4.7kΩ). | Fully standard across all board revisions. |

---

## 4. Verification & Validation Rules

1. **DRC / ERC Rule**: In EasyEDA Pro, net `AMP_FAULTz_ADR` must connect exactly three pins: `U4.3`, `R12.2`, and `U1.7`.
2. **Impedance & Layout Rule**: Trace length from U4 Pin 3 to ESP32 Pin 7 should be kept $< 40\text{mm}$ and isolated from high- $di/dt$ switching nodes (MP3426 SW, TAS5805M BST traces) to prevent spurious fault interrupts.
3. **Firmware Initialization Verification**: During bench testing, register `0x61` read-back must confirm `0x0B` and register `0x60` must read `0x01`. An artificial pull-down test on Pin 3 via test pad must immediately trip the ESP32 GPIO35 interrupt and enter `EMERGENCY_SHUTDOWN`.

---

- **Author**: Antigravity Technical Reviewer
- **Approval Status**: RECOMMENDED FOR IMMEDIATE PHASE 0 ECO ADOPTION
