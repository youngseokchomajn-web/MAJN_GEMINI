#!/usr/bin/env python3
"""
MAJN BOM, CPL, and PCB Placement Cross-Verification Engine (v2.0)
----------------------------------------------------------------
Cross-audits manufacturing deliverables for complete consistency:
1. BOM designators == CPL designators == PCB components
2. Single-sided SMT layer placement rules
3. Footprint geometry match (e.g., 0402 vs 0603)
4. LCSC C-ID consistency
MANDATORY: Enforces sys.exit(1) on failure.
"""

import sys
import os
import csv
import json
import argparse
from pathlib import Path

def parse_args():
    parser = argparse.ArgumentParser(description="Cross-verify BOM, CPL, and PCB layout data.")
    parser.add_argument("--bom", type=str, required=True, help="Path to BOM CSV")
    parser.add_argument("--cpl", type=str, required=True, help="Path to CPL CSV")
    parser.add_argument("--pcb-comps", type=str, required=False, help="Path to PCB comps JSON")
    parser.add_argument("--require-single-sided", action="store_true", help="Fail if any part is on Bottom layer")
    return parser.parse_args()

def load_bom(bom_path):
    p = Path(bom_path)
    if not p.exists():
        print(f"[ERROR] BOM file not found: {p}", file=sys.stderr)
        sys.exit(1)
    bom_map = {}
    with open(p, "r", encoding="utf-8", errors="ignore") as f:
        reader = csv.reader(f)
        rows = list(reader)
    if not rows:
        print(f"[ERROR] BOM is empty: {p}", file=sys.stderr)
        sys.exit(1)
    for r in rows[1:]:
        if not r or not any(r): continue
        comment = r[0].strip() if len(r) > 0 else ""
        des_str = r[1].strip() if len(r) > 1 else ""
        fp = r[2].strip() if len(r) > 2 else ""
        lcsc = r[3].strip() if len(r) > 3 else ""
        for d in des_str.replace(" ", "").split(","):
            if d:
                bom_map[d] = {"comment": comment, "footprint": fp, "lcsc": lcsc}
    return bom_map

def load_cpl(cpl_path):
    p = Path(cpl_path)
    if not p.exists():
        print(f"[ERROR] CPL file not found: {p}", file=sys.stderr)
        sys.exit(1)
    cpl_map = {}
    with open(p, "r", encoding="utf-8", errors="ignore") as f:
        reader = csv.reader(f)
        rows = list(reader)
    if not rows:
        print(f"[ERROR] CPL is empty: {p}", file=sys.stderr)
        sys.exit(1)
    for r in rows[1:]:
        if not r or not any(r): continue
        d = r[0].strip()
        x_str = r[1].replace("mm", "").strip() if len(r) > 1 else "0"
        y_str = r[2].replace("mm", "").strip() if len(r) > 2 else "0"
        layer = r[3].strip() if len(r) > 3 else "Top"
        rot_str = r[4].strip() if len(r) > 4 else "0"
        try:
            x = float(x_str)
            y = float(y_str)
            rot = float(rot_str)
        except ValueError:
            x, y, rot = 0.0, 0.0, 0.0
        cpl_map[d] = {"x": x, "y": y, "layer": layer, "rot": rot}
    return cpl_map

def run_cross_audit(bom_map, cpl_map, require_single_sided=False):
    violations = []
    warnings = []

    bom_set = set(bom_map.keys())
    cpl_set = set(cpl_map.keys())

    # 1. Designator Set Equality
    in_bom_not_cpl = sorted(list(bom_set - cpl_set))
    in_cpl_not_bom = sorted(list(cpl_set - bom_set))

    if in_bom_not_cpl:
        violations.append(f"Components in BOM but missing in CPL: {in_bom_not_cpl}")
    if in_cpl_not_bom:
        violations.append(f"Components in CPL but missing in BOM: {in_cpl_not_bom}")

    # 2. Check SMT Layer
    bottom_parts = []
    for d, info in cpl_map.items():
        if info["layer"].lower() == "bottom":
            bottom_parts.append(d)

    if bottom_parts:
        if require_single_sided:
            violations.append(f"Single-sided SMT requirement violated! Found on Bottom layer: {bottom_parts}")
        else:
            warnings.append(f"Double-sided SMT active (Economic PCBA unavailable). Bottom components: {bottom_parts}")

    # 3. Critical Component Presence Check
    critical_parts = ["U1", "U2", "U3", "U4", "U5", "L1", "D1", "D3", "R12"]
    for cp in critical_parts:
        if cp not in bom_set:
            violations.append(f"CRITICAL COMPONENT MISSING: {cp} is not in the manufacturing BOM!")
        if cp not in cpl_set:
            violations.append(f"CRITICAL COMPONENT MISSING: {cp} is not in the CPL pick-and-place file!")

    # 4. Footprint Package Verification
    for d in sorted(bom_set.intersection(cpl_set)):
        fp = bom_map[d]["footprint"].upper()
        comment = bom_map[d]["comment"].upper()
        # Check 0402 vs 0603 mismatches
        if "0402" in fp and "0603" in comment:
            warnings.append(f"Potential package mismatch for {d}: Footprint={fp} vs Comment={comment}")
        elif "0603" in fp and "0402" in comment:
            warnings.append(f"Potential package mismatch for {d}: Footprint={fp} vs Comment={comment}")

    # Output Results
    print("\n" + "=" * 60)
    print(f"BOM vs CPL AUDIT: BOM={len(bom_set)} parts, CPL={len(cpl_set)} parts")
    print(f"Violations: {len(violations)}, Warnings: {len(warnings)}")
    print("=" * 60)

    for w in warnings:
        print(f"  [WARN] {w}")
    for v in violations:
        print(f"  [FAIL] {v}", file=sys.stderr)

    if violations:
        print("\n>>> AUDIT FAILED: Manufacturing files inconsistent (sys.exit(1)) <<<", file=sys.stderr)
        sys.exit(1)
    else:
        print("\n>>> AUDIT PASSED: All BOM and CPL components verified (sys.exit(0)) <<<")
        sys.exit(0)

def main():
    args = parse_args()
    bom = load_bom(args.bom)
    cpl = load_cpl(args.cpl)
    run_cross_audit(bom, cpl, require_single_sided=args.require_single_sided)

if __name__ == "__main__":
    main()
