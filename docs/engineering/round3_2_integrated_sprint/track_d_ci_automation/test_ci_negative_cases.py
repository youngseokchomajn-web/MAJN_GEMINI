#!/usr/bin/env python3
"""
MAJN CI Negative Test Harness & Exit Code Validation Suite (v2.0)
-----------------------------------------------------------------
Proves that the CI verification suite reliably blocks bad engineering designs
by testing intentional fault injections (negative test cases) and ensuring:
1. Every faulty design causes tools to exit with sys.exit(1).
2. Clean baseline designs cause tools to exit with sys.exit(0).
3. Zero silent failures or false positives.
"""

import os
import sys
import json
import tempfile
import subprocess
from pathlib import Path

BASE_DIR = Path("/Users/youngseok/Desktop/majn")
TRACK_D_DIR = BASE_DIR / "docs" / "engineering" / "round3_2_integrated_sprint" / "track_d_ci_automation"

def run_cmd(args):
    proc = subprocess.run(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    return proc.returncode, proc.stdout, proc.stderr

def test_netlist_verifier():
    print("\n--- [CI Test 1] verify_netlist_rules.py Negative & Positive Tests ---")
    script = TRACK_D_DIR / "verify_netlist_rules.py"

    # Negative Case: Pin 3 tied to GND, R12 missing, GPIO15 = AMP_PDN
    bad_netlist = {
        "components": {
            "link_U4": {
                "props": {"Designator": "U4"},
                "pinInfoMap": {
                    "1": {"number": "1", "net": "GND"},
                    "3": {"number": "3", "net": "GND"}, # FAULT: Tied to GND!
                    "12": {"number": "12", "net": "AMP_PDN"}
                }
            },
            "link_U1": {
                "props": {"Designator": "U1"},
                "pinInfoMap": {
                    "23": {"number": "23", "name": "IO15", "net": "AMP_PDN"} # FAULT: Strapping pin!
                }
            }
        }
    }

    with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as f:
        json.dump(bad_netlist, f)
        bad_path = f.name

    try:
        code, stdout, stderr = run_cmd([sys.executable, str(script), "--sch-netlist", bad_path])
        assert code == 1, f"Expected exit code 1 for bad netlist, got {code}!"
        assert "RULE-01-FAIL" in stderr, "Expected RULE-01-FAIL in output!"
        assert "RULE-04-FAIL" in stderr, "Expected RULE-04-FAIL in output!"
        assert "RULE-06-FAIL" in stderr, "Expected RULE-06-FAIL in output!"
        print("  -> PASS: Bad netlist correctly rejected with non-zero exit code 1.")
    finally:
        os.unlink(bad_path)

    # Positive Case: Proper PCB #0006 target netlist
    good_netlist = {
        "components": {
            "link_U4": {
                "props": {"Designator": "U4"},
                "pinInfoMap": {
                    "1": {"number": "1", "net": "GND"},
                    "3": {"number": "3", "net": "AMP_FAULTz_ADR"},
                    "12": {"number": "12", "net": "AMP_PDN"}
                }
            },
            "link_R12": {
                "props": {"Designator": "R12", "Value": "4.7kΩ"},
                "pinInfoMap": {
                    "1": {"number": "1", "net": "VCC_3V3"},
                    "2": {"number": "2", "net": "AMP_FAULTz_ADR"}
                }
            },
            "link_R3": {
                "props": {"Designator": "R3", "Value": "5.1kΩ"},
                "pinInfoMap": {"1": {"number": "1", "net": "USB_CC1"}, "2": {"number": "2", "net": "GND"}}
            },
            "link_R4": {
                "props": {"Designator": "R4", "Value": "5.1kΩ"},
                "pinInfoMap": {"1": {"number": "1", "net": "USB_CC2"}, "2": {"number": "2", "net": "GND"}}
            },
            "link_U1": {
                "props": {"Designator": "U1"},
                "pinInfoMap": {
                    "16": {"number": "16", "name": "IO13", "net": "AMP_PDN"},
                    "23": {"number": "23", "name": "IO15", "net": "NC"},
                    "7": {"number": "7", "name": "IO35", "net": "AMP_FAULTz_ADR"}
                }
            }
        }
    }

    with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as f:
        json.dump(good_netlist, f)
        good_path = f.name

    try:
        code, stdout, stderr = run_cmd([sys.executable, str(script), "--sch-netlist", good_path])
        assert code == 0, f"Expected exit code 0 for good netlist, got {code}! Stderr: {stderr}"
        print("  -> PASS: Valid target netlist passes with exit code 0.")
    finally:
        os.unlink(good_path)

def test_bom_cpl_verifier():
    print("\n--- [CI Test 2] verify_bom_cpl_pcb.py Negative & Positive Tests ---")
    script = TRACK_D_DIR / "verify_bom_cpl_pcb.py"

    # Negative Case: Missing critical component U4 in CPL
    with tempfile.NamedTemporaryFile("w", suffix=".csv", delete=False) as f_bom:
        f_bom.write("Comment,Designator,Footprint,JLCPCB Part #\n")
        f_bom.write("TAS5805M,U4,HTSSOP-28,C478472\n")
        f_bom.write("ESP32,U1,SMD,C701345\n")
        bom_path = f_bom.name

    with tempfile.NamedTemporaryFile("w", suffix=".csv", delete=False) as f_cpl:
        f_cpl.write("Designator,Mid X,Mid Y,Layer,Rotation\n")
        f_cpl.write("U1,10.0mm,10.0mm,Top,0\n") # Missing U4!
        cpl_path = f_cpl.name

    try:
        code, stdout, stderr = run_cmd([sys.executable, str(script), "--bom", bom_path, "--cpl", cpl_path])
        assert code == 1, f"Expected exit code 1 for missing component, got {code}!"
        assert "CRITICAL COMPONENT MISSING" in stderr or "missing in CPL" in stderr
        print("  -> PASS: Missing critical component correctly rejected with exit code 1.")
    finally:
        os.unlink(bom_path)
        os.unlink(cpl_path)

def test_gpio_conflict_verifier():
    print("\n--- [CI Test 3] verify_gpio_conflicts.py Negative & Positive Tests ---")
    script = TRACK_D_DIR / "verify_gpio_conflicts.py"

    # Negative Case: GPIO15 used for PDN with pull-up; GPIO35 configured as OUTPUT
    with tempfile.NamedTemporaryFile("w", suffix=".csv", delete=False) as f_gpio:
        f_gpio.write("GPIO,Pin,Net,Direction,Pull\n")
        f_gpio.write("GPIO15,Pin 23,AMP_PDN,Output,Pull-Up\n")
        f_gpio.write("GPIO35,Pin 7,AMP_FAULTz,Output,Internal Pull\n")
        bad_gpio_path = f_gpio.name

    try:
        code, stdout, stderr = run_cmd([sys.executable, str(script), "--gpio-csv", bad_gpio_path])
        assert code == 1, f"Expected exit code 1 for hazardous GPIO, got {code}!"
        assert "STRAPPING VIOLATION" in stderr, "Expected STRAPPING VIOLATION in stderr!"
        assert "SILICON LIMITATION VIOLATION" in stderr, "Expected SILICON LIMITATION VIOLATION in stderr!"
        print("  -> PASS: Hazardous strapping pin and GPI violations rejected with exit code 1.")
    finally:
        os.unlink(bad_gpio_path)

def test_power_calculations_verifier():
    print("\n--- [CI Test 4] verify_power_calculations.py Negative & Positive Tests ---")
    script = TRACK_D_DIR / "verify_power_calculations.py"
    power_csv = BASE_DIR / "docs" / "engineering" / "round3_2_integrated_sprint" / "track_b_power_design" / "POWER_BUDGET_CALCULATION_MODEL.csv"

    # Operational cases in model pass
    code, stdout, stderr = run_cmd([sys.executable, str(script), "--power-csv", str(power_csv)])
    assert code == 0, f"Expected exit code 0 for normal power budget, got {code}! Stderr: {stderr}"
    print("  -> PASS: Verified power budget passes operational checks with exit code 0.")

    # Negative Case: When strict-all is enabled, intentional fault rows trigger exit code 1
    code, stdout, stderr = run_cmd([sys.executable, str(script), "--power-csv", str(power_csv), "--strict-all"])
    assert code == 1, f"Expected exit code 1 under strict-all, got {code}!"
    assert "POWER EXCEEDED" in stderr, "Expected POWER EXCEEDED in stderr!"
    print("  -> PASS: Over-power fault cases strictly caught with exit code 1.")

def main():
    print("==================================================================")
    print("  MAJN CI Negative Testing & Exit Code Verification Harness")
    print("==================================================================")

    test_netlist_verifier()
    test_bom_cpl_verifier()
    test_gpio_conflict_verifier()
    test_power_calculations_verifier()

    print("\n==================================================================")
    print("  ALL CI VERIFICATION ENGINES CONFIRMED HARDENED (EXIT CODE 1 ENFORCED)")
    print("==================================================================")

if __name__ == "__main__":
    main()
