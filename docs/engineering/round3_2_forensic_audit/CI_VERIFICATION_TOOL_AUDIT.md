# Forensic Audit Report: CI & Automated Verification Tool Suite
## Independent Technical Evaluation of Track D CI Engines, Test Coverage, and False-Pass Vulnerabilities

- **Document Identifier**: `MAJN-R3.2-CI-TOOL-AUDIT-001`
- **Revision**: v1.0
- **Lead Auditor**: Antigravity (Independent Technical Reviewer / Dual-AI Architecture)
- **Target Suite**: `docs/engineering/round3_2_integrated_sprint/track_d_ci_automation/`
- **Evaluation Date**: 2026-11-06
- **Status**: FORMALLY AUDITED / MULTIPLE CRITICAL VULNERABILITIES IDENTIFIED

---

## 1. Executive Summary

Round 3.2 claimed that Track D had fully hardened the MAJN automated verification suite by enforcing `sys.exit(1)` on defect detection and authoring a negative test harness (`test_ci_negative_cases.py`), reporting **"100% Deterministic CI PASS with zero false-pass risk."**

This forensic audit executed a deep static and dynamic evaluation of all five Python verifiers and the negative test harness. Our findings demonstrate that while the introduction of non-zero exit codes is a positive improvement over legacy warnings, **the verification suite contains fundamental architectural flaws, header parsing bugs, and superficial check logic that permitted severe false-pass conclusions to bypass review:**

1. **`verify_gpio_conflicts.py` Complete Verification Bypass**: The CSV loader failed to match headers without the exact substring `"GPIO"` (e.g. `Pin_Number`, `Pin_Name`). It fell back to numeric indices, resulting in the pin numbers (`'1'`, `'2'`, `'3'`) being audited instead of GPIO names (`"GPIO15"`). Because `'1'` was never in `STRAPPING_PINS`, **the script audited 0 strapping pins and reported a 100% false pass on `ESP32_GPIO_FULL_ALLOCATION_MATRIX.csv`!**
2. **`verify_power_calculations.py` Zero-Calculation Architecture**: The script performs zero physical or electrical recalculations. It does not calculate switching frequency, duty cycle, inductor ripple, or MLCC derating. It merely reads pre-filled CSV values, explicitly skips rows containing `"Fault"` or `"Unconstrained"`, and checks if remaining numbers are `< 10.0W`.
3. **`verify_requirements_traceability.py` False-Pass on Plaintext**: The tool uses regex to check if a Markdown table column contains the Korean word `"확정"` (Confirmed). Because the author typed `"확정"` into DOC03, the tool declared physical hardware requirements (such as PVDD isolation jumpers and clamp diodes) as "verified and closed" even though no hardware has been manufactured!
4. **`verify_netlist_rules.py` Target Snippet Bypass**: The tool passes only because it was pointed at a hand-crafted 15-component snippet (`PCB0006_SCHEMATIC_NETLIST_TARGET.json`). When executed against the actual schematic baseline (`sch_netlist_final.json`), it fails immediately with 5 critical errors.
5. **`verify_bom_cpl_pcb.py` Positional Index Fragility**: Column assignments are hardcoded to fixed array indices (`r[0]`, `r[1]`, `r[2]`, `r[3]`), rendering it incapable of parsing standard EDA CSV exports with reordered or renamed headers.

---

## 2. Tool-by-Tool Forensic Analysis

### 2.1 `verify_gpio_conflicts.py`

#### Purpose & Claimed Coverage
Audits ESP32 pin assignments against boot strapping hazards (GPIO0, 2, 5, 12, 15), input-only GPI limits (GPIO34-39), and peripheral bus conflicts (I2C, I2S, SPI).

#### Code Flaw Discovered (Lines 56-87)
```python
# In load_gpio_allocation(csv_path):
for idx, col in enumerate(header_upper):
    if "GPIO" in col: header_map["gpio"] = idx
    elif "PIN_NUM" in col or col == "PIN": header_map["pin"] = idx
    # ...
```
When evaluating `docs/engineering/pcb_0006/ESP32_GPIO_FULL_ALLOCATION_MATRIX.csv`, the headers are:
`Pin_Number, Pin_Name, Primary_Function, Allocated_Net, Strapping_Pin, Reset_Default_State, IO_Type, ...`

None of these headers contain the literal substring `"GPIO"`. Consequently:
- `header_map` does not contain `"gpio"`.
- `if header_map and "gpio" in header_map:` evaluates to **`False`**.
- Execution falls back to:
  ```python
  else:
      gpio_name = row[0].strip().upper()  # row[0] is Pin_Number: '1', '2', '3', '4'...
  ```
- The loaded dictionary keys are numeric strings: `{'1': ..., '2': ..., '23': ...}` instead of `{'GPIO15': ...}`.
- In `audit_gpio()`:
  ```python
  if gpio in STRAPPING_PINS:  # gpio is '23', STRAPPING_PINS expects 'GPIO15'
      ...
  ```
- The condition evaluates to `False` for every single row. **Not a single strapping pin was audited!**

#### Execution Evidence
```bash
$ python3 -c '
from verify_gpio_conflicts import load_gpio_allocation
allocs = load_gpio_allocation("docs/engineering/pcb_0006/ESP32_GPIO_FULL_ALLOCATION_MATRIX.csv")
print("Loaded keys:", list(allocs.keys())[:5])
'
Loaded keys: ['1', '2', '3', '4', '5']  # AUDITING PIN NUMBERS, NOT GPIO STRINGS!
```
Despite GPIO15 having been historically pulled HIGH, this checker printed:
`>>> AUDIT PASSED: All GPIO assignments boot-safe and silicon-compliant (sys.exit(0)) <<<`
This represents a **catastrophic false-pass vulnerability** in the CI pipeline.

---

### 2.2 `verify_power_calculations.py`

#### Purpose & Claimed Coverage
Audits power dissipation, inductor saturation headroom, and thermal junction limits across operating modes.

#### Code Flaw Discovered (Lines 43-73)
The tool does not recompute power from voltage, current, switching frequency, or component physics. It merely acts as a CSV string inspector:
```python
is_intended_fault_case = "CRITICAL_VIOLATION" in status or "FATAL" in status or "Fault" in mode or "Unconstrained" in mode

if not is_intended_fault_case or enforce_all_modes_safe:
    # Compares pre-baked CSV strings against 10.0W and 3.6A
else:
    # SKIPS VIOLATION CHECK COMPLETELY!
    print(f"[TEST-CASE-CONFIRMED] Model correctly identifies {mode} as violating limits...")
```
- If a CSV row contains `"Fault"` in its name, the checker bypasses all assertions and issues an unconditional pass.
- The script completely missed the fact that Round 3.2 used a **fabricated formula** for the MP3426 switching frequency ($f_{\text{sw}} = 1.22\text{MHz}$ vs real $510\text{kHz}$), which doubled inductor ripple and tripled output ripple.
- A checker that cannot compute $P = V \times I$ or verify physical equations from component parameters is not a verification engine; it is a cosmetic report validator.

---

### 2.3 `verify_requirements_traceability.py`

#### Purpose & Claimed Coverage
Verifies that all Critical P0, P1, and P2 electrical design requirements in `DOC03` are verified and closed.

#### Code Flaw Discovered (Lines 61-66)
```python
if prio == "P0":
    p0_count += 1
    if "확정" not in status and "PASS" not in status and "VERIFIED" not in status:
        violations.append(...)
    else:
        print(f"[PASS] P0 Requirement {req_id}: '{name}' is verified/closed.")
```
- The checker performs a simple substring search for `"확정"`, `"PASS"`, or `"VERIFIED"` in the text of Markdown tables.
- In `DOC03_PCB0006_ELECTRICAL_DESIGN_REQUIREMENTS.md`:
  - `REQ-P0-02` (PVDD 12V Isolation Jumper): Status = `확정` $\implies$ **PASSED**
  - `REQ-P0-03` (Bleeder Resistor): Status = `확정` $\implies$ **PASSED**
  - `REQ-P0-04` (BTL Clamp Diode Array): Status = `확정` $\implies$ **PASSED**
- In physical reality, **none of these components exist on any fabricated PCB or even in the official schematic CAD files!**
- Granting automated CI "Pass" status based on self-declared Markdown text creates an illusion of design closure while hardware risks remain completely open.

---

### 2.4 `verify_netlist_rules.py`

#### Purpose & Claimed Coverage
Audits netlist files to ensure TAS5805M Pin 3 is not tied to GND, Pin 1 is tied to GND, Pin 12 is PDN, R12 exists, and USB CC resistors are 5.1kΩ.

#### Evaluation Against Baseline vs Target Netlists
- When run on `docs/engineering/round3_2_integrated_sprint/track_e_pcb0006_design_input/PCB0006_SCHEMATIC_NETLIST_TARGET.json`, it returns **EXIT CODE 0 (PASS)**.
- However, `PCB0006_SCHEMATIC_NETLIST_TARGET.json` is a **15-component dummy snippet** created during Round 3.2 that lacks all capacitors, sensors, connectors, and diodes.
- When run on the actual baseline schematic netlist (`인증준비/mcp_development/sch_netlist_final.json`), it halts with **EXIT CODE 1 (FAIL)** and 5 violations:
  ```
  [FAIL] RULE-01-FAIL: U4 Pin 3 (ADR/FAULT) is connected to 'GND'.
  [FAIL] RULE-04-FAIL: Resistor R12 (4.7kΩ ADR pull-up) is MISSING from schematic netlist.
  [FAIL] RULE-05-FAIL: R3 has legacy incorrect value '14kΩ'.
  [FAIL] RULE-05-FAIL: R4 has legacy incorrect value '14kΩ'.
  [FAIL] RULE-06-FAIL: ESP32 GPIO15 is assigned to AMP_PDN!
  ```
- This confirms that Round 3.2's claim of "100% Passing CI" was achieved solely by pointing the verification tool at an idealized target mock rather than the actual design files.

---

### 2.5 `verify_bom_cpl_pcb.py`

#### Purpose & Claimed Coverage
Cross-checks BOM designators against CPL pick-and-place files and PCB placement coordinates, checking single-sided SMT rules.

#### Vulnerabilities Discovered
1. **Positional Index Fragility**: It assumes fixed CSV columns:
   - Index 0: Comment
   - Index 1: Designator
   - Index 2: Footprint
   - Index 3: JLCPCB Part #
   If a BOM has headers like `Designator, Comment, Footprint`, the tool swaps designators and comments, failing with parsing errors.
2. **Missing CPL for Target BOM**: Round 3.2 created `PCB0006_BILL_OF_MATERIALS_TARGET.csv` (62 parts), but did NOT create a corresponding CPL file for PCB #0006. In `test_ci_negative_cases.py`, it was tested against legacy Prototype #0005 files with synthetic test cases rather than a unified PCB #0006 manufacturing release package.

---

## 3. Negative Error Injection Audit Summary

We evaluated whether deliberate errors injected into test inputs properly cause the verification suite to halt with non-zero exit codes:

| Injected Defect | Target Tool | Expected Behavior | Actual Behavior | Audit Verdict |
| :--- | :--- | :---: | :---: | :---: |
| TAS5805M Pin 3 tied to GND | `verify_netlist_rules.py` | Exit Code 1 | Exit Code 1 | **EFFECTIVE** |
| Resistor R12 missing from SCH | `verify_netlist_rules.py` | Exit Code 1 | Exit Code 1 | **EFFECTIVE** |
| GPIO15 assigned to PDN (Pull-up) | `verify_gpio_conflicts.py` (Clean input) | Exit Code 1 | Exit Code 1 | **EFFECTIVE** |
| GPIO Allocation with `Pin_Name` header | `verify_gpio_conflicts.py` | Exit Code 1 on strapping error | Exit Code 0 (Bypassed!) | **FAILED (PARSING BUG)** |
| Fabricated MP3426 Frequency Formula | `verify_power_calculations.py` | Exit Code 1 (Formula mismatch) | Ignored / Not Checked | **FAILED (NO CALCULATION)** |
| Under-rated BAT54S Diode on BTL lines | `verify_bom_cpl_pcb.py` | Exit Code 1 (Rating violation) | Ignored / Not Checked | **FAILED (NO RATING AUDIT)** |
| Incomplete Netlist (15 of 62 parts) | `verify_netlist_rules.py` | Exit Code 1 (Missing passives) | Exit Code 0 (PASS) | **FAILED (SNIPPET ACCEPTED)** |
| Unverified Requirement marked "확정" | `verify_requirements_traceability.py` | Exit Code 1 (Artifact missing) | Exit Code 0 (PASS) | **FAILED (STRING MATCH ONLY)** |

---

## 4. Mandatory CI Hardening Directives for Round 3.3

Prior to advancing past Gate G2, the CI verification suite must be overhauled according to the following rules:

1. **Robust Header Normalization**: Tools must parse CSV headers dynamically by name (supporting `Pin`, `Pin_Name`, `GPIO`, `Net`, `Designator`, `Val`), raising a fatal exception if required columns cannot be mapped unambiguously.
2. **True Equation-Level Recalculation**: `verify_power_calculations.py` must take raw component values ($R_1, R_2, R_9, L_1, C_8, C_9$) as input and evaluate the true MPS and TI mathematical equations, flagging any discrepancies between claimed and computed parameters.
3. **Evidence-Linked Requirements Traceability**: `verify_requirements_traceability.py` must NOT accept `"확정"` or `"PASS"` strings unless accompanied by an explicit, existing file path in the workspace (e.g. Gerber file, test log, lab certificate).
4. **Full Netlist Completeness Check**: `verify_netlist_rules.py` must verify that every component in the BOM is represented in the netlist with valid pin connections. Snippets must be rejected.
5. **Component Stress & Rating Checker**: Author a dedicated `verify_component_ratings.py` that validates diode $I_{\text{FSM}}$, capacitor $V_{\text{rating}}$, and resistor wattage against circuit operating conditions.
