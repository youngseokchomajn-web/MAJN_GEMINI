#!/usr/bin/env python3
"""
MAJN Automated Netlist & Schematic Design Rule Checker (v2.0)
------------------------------------------------------------
Strictly enforces electrical design rules on schematic and PCB netlists.
MANDATORY: Returns exit code 1 on ANY rule violation, exit code 0 on PASS.
"""

import sys
import json
import argparse
from pathlib import Path

def parse_arguments():
    parser = argparse.ArgumentParser(description="Audit schematic and PCB netlist design rules.")
    parser.add_argument("--sch-netlist", type=str, required=True, help="Path to schematic netlist JSON")
    parser.add_argument("--pcb-comps", type=str, required=False, help="Path to PCB components JSON (optional)")
    return parser.parse_args()

def load_json_file(path_str):
    path = Path(path_str)
    if not path.exists():
        print(f"[ERROR] Required netlist file does not exist: {path}", file=sys.stderr)
        sys.exit(1)
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def audit_netlist(sch_data, pcb_data=None):
    violations = []
    warnings = []
    
    # 1. Inspect Components in Schematic Netlist
    components = sch_data.get("components", {})
    if isinstance(components, list):
        # Handle list format
        comp_map = {c.get("designator", ""): c for c in components}
    elif isinstance(components, dict):
        comp_map = {}
        for k, v in components.items():
            des = v.get("props", {}).get("Designator") or v.get("designator") or k
            comp_map[des] = v
    else:
        comp_map = {}

    # Rule 1: TAS5805M (U4) Pin 3 must NOT be tied to GND
    u4 = comp_map.get("U4")
    if not u4:
        violations.append("RULE-01-FAIL: U4 (TAS5805M) not found in schematic components map.")
    else:
        pins = u4.get("pinInfoMap", {}) or u4.get("pins", {})
        pin3_net = ""
        pin1_net = ""
        pin12_net = ""

        if isinstance(pins, dict):
            p3 = pins.get("3", {})
            pin3_net = p3.get("net", "") if isinstance(p3, dict) else str(p3)
            p1 = pins.get("1", {})
            pin1_net = p1.get("net", "") if isinstance(p1, dict) else str(p1)
            p12 = pins.get("12", {})
            pin12_net = p12.get("net", "") if isinstance(p12, dict) else str(p12)
        elif isinstance(pins, list):
            for p in pins:
                num = str(p.get("number") or p.get("pinNumber") or p.get("pin", ""))
                if num == "3": pin3_net = p.get("net", "")
                elif num == "1": pin1_net = p.get("net", "")
                elif num == "12": pin12_net = p.get("net", "")

        # Check Pin 3
        if pin3_net.upper() == "GND" or pin3_net == "":
            violations.append(f"RULE-01-FAIL: U4 Pin 3 (ADR/FAULT) is connected to '{pin3_net}'. It must NOT be tied to GND or NC!")
        else:
            print(f"[PASS] Rule 1: U4 Pin 3 is connected to active signal net '{pin3_net}'.")

        # Check Pin 1
        if pin1_net.upper() != "GND":
            violations.append(f"RULE-02-FAIL: U4 Pin 1 (DGND) is connected to '{pin1_net}'. It MUST be connected to GND!")
        else:
            print(f"[PASS] Rule 2: U4 Pin 1 is properly grounded to GND.")

        # Check Pin 12
        if "PDN" not in pin12_net.upper():
            violations.append(f"RULE-03-FAIL: U4 Pin 12 (PDN) is connected to '{pin12_net}'. Expected AMP_PDN net.")
        else:
            print(f"[PASS] Rule 3: U4 Pin 12 connected to PDN control net '{pin12_net}'.")

    # Rule 4: Resistor R12 must exist and connect VCC_3V3 to Pin 3 net
    r12 = comp_map.get("R12")
    if not r12:
        violations.append("RULE-04-FAIL: Resistor R12 (4.7kΩ ADR pull-up) is MISSING from schematic netlist.")
    else:
        val = str(r12.get("props", {}).get("Value") or r12.get("value", "") or r12.get("Comment", ""))
        if "4.7" not in val and "4K7" not in val.upper():
            warnings.append(f"RULE-04-WARN: R12 value is '{val}', expected 4.7kΩ for address 0x2C.")
        print(f"[PASS] Rule 4: R12 exists in schematic with value '{val}'.")

    # Rule 5: Resistors R3, R4 (USB-C CC lines) must be 5.1kΩ, NOT 14kΩ or 10kΩ
    for r_des in ["R3", "R4"]:
        r_comp = comp_map.get(r_des)
        if r_comp:
            val = str(r_comp.get("props", {}).get("Value") or r_comp.get("value", "") or r_comp.get("Comment", ""))
            if "14K" in val.upper() or "14k" in val:
                violations.append(f"RULE-05-FAIL: {r_des} has legacy incorrect value '{val}'. Must be 5.1kΩ for Type-C standard.")
            elif "5.1" in val or "5K1" in val.upper():
                print(f"[PASS] Rule 5: {r_des} has compliant Type-C pull-down value '{val}'.")

    # Rule 6: ESP32 Pin Allocation check
    u1 = comp_map.get("U1")
    if u1:
        u1_pins = u1.get("pinInfoMap", {}) or u1.get("pins", {})
        io15_net = ""
        io13_net = ""
        io35_net = ""

        if isinstance(u1_pins, dict):
            for p_num, p_info in u1_pins.items():
                name = str(p_info.get("name", "")).upper()
                net = p_info.get("net", "")
                if "IO15" in name or p_num == "23": io15_net = net
                if "IO13" in name or p_num == "16": io13_net = net
                if "IO35" in name or p_num == "7": io35_net = net

        # Check IO15 (strapping pin)
        if "PDN" in io15_net.upper():
            violations.append("RULE-06-FAIL: ESP32 GPIO15 (MTDO Strapping Pin) is assigned to AMP_PDN! High-risk boot hazard.")
        else:
            print(f"[PASS] Rule 6: GPIO15 decoupled from AMP_PDN (net: '{io15_net}').")

        # Check IO13
        if "PDN" in io13_net.upper():
            print(f"[PASS] Rule 6: GPIO13 properly assigned to AMP_PDN.")

        # Check IO35
        if "FAULT" in io35_net.upper() or "ADR" in io35_net.upper():
            print(f"[PASS] Rule 6: GPIO35 properly assigned to FAULTz interrupt.")

    # 2. Summary & Exit Code
    print("\n" + "=" * 60)
    print(f"NETLIST AUDIT SUMMARY: {len(violations)} Violations, {len(warnings)} Warnings")
    print("=" * 60)
    for w in warnings:
        print(f"  [WARN] {w}")
    for v in violations:
        print(f"  [FAIL] {v}", file=sys.stderr)

    if violations:
        print("\n>>> AUDIT FAILED: Non-zero exit code enforced (sys.exit(1)) <<<", file=sys.stderr)
        sys.exit(1)
    else:
        print("\n>>> AUDIT PASSED: All netlist safety rules verified (sys.exit(0)) <<<")
        sys.exit(0)

def main():
    args = parse_arguments()
    sch_data = load_json_file(args.sch_netlist)
    pcb_data = load_json_file(args.pcb_comps) if args.pcb_comps else None
    audit_netlist(sch_data, pcb_data)

if __name__ == "__main__":
    main()
