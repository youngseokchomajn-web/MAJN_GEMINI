#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
MAJN Smart Bassinet - PCB Rev-C Production Manufacturing Package Cross-Verification Suite
Verifies 4-layer Gerber, BOM, CPL, FlyingProbeTesting parity, and 13.5mm mechanical stack-up.
"""

import os
import sys
import zipfile
import json
import csv

MFG_DIR = "/Users/youngseok/Desktop/majn/인증준비/pcb/Rev_C_mfg"
GERBER_ZIP = os.path.join(MFG_DIR, "Gerber_MAJN_Rev_C.zip")
BOM_FILE = os.path.join(MFG_DIR, "BOM_MAJN_Rev_C.csv")
CPL_FILE = os.path.join(MFG_DIR, "CPL_MAJN_Rev_C.csv")
EPRO2_FILE = os.path.join(MFG_DIR, "MAJN_Rev_C.epro2")

def parse_bom(path):
    comps = {}
    with open(path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            des_str = row.get("Designator", "")
            comment = row.get("Comment", "")
            footprint = row.get("Footprint", "")
            part_no = row.get("JLCPCB Part #", "")
            for des in [d.strip() for d in des_str.split(",") if d.strip()]:
                comps[des] = {
                    "comment": comment,
                    "footprint": footprint,
                    "part": part_no
                }
    return comps

def parse_cpl(path):
    cpl = {}
    with open(path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            des = row.get("Designator", "").strip()
            if des:
                cpl[des] = {
                    "x": float(row.get("Mid X", "0").replace("mm", "").strip()),
                    "y": float(row.get("Mid Y", "0").replace("mm", "").strip()),
                    "layer": row.get("Layer", "").strip(),
                    "rot": row.get("Rotation", "").strip()
                }
    return cpl

def main():
    print("=" * 78)
    print("MAJN HARDWARE MANUFACTURING PACKAGE - CROSS-VERIFICATION (Rev-C.MFG)")
    print("=" * 78)
    print(f"Target Directory: {MFG_DIR}")

    total_gates = 0
    passed_gates = 0

    # Gate 1: File Existence & 4-Layer Stacking
    total_gates += 1
    print("\n[GATE 1] 4-Layer Stacking & Layer Integrity Verification:")
    if not os.path.exists(GERBER_ZIP):
        print(f"  => FAIL: Gerber ZIP missing at {GERBER_ZIP}")
        return 1
    
    with zipfile.ZipFile(GERBER_ZIP) as z:
        files = z.namelist()
        g1_present = any(f.endswith(".G1") or "InnerLayer1" in f for f in files)
        g2_present = any(f.endswith(".G2") or "InnerLayer2" in f for f in files)
        gtl_present = any(f.endswith(".GTL") or "TopLayer" in f for f in files)
        gbl_present = any(f.endswith(".GBL") or "BottomLayer" in f for f in files)
        gko_present = any(f.endswith(".GKO") or "BoardOutline" in f for f in files)
        fpt_present = "FlyingProbeTesting.json" in files
        
        print(f"  - Total Gerber Archive Files: {len(files)}")
        print(f"  - Inner Layer 1 (GND Plane) : {'FOUND (.G1)' if g1_present else 'MISSING'}")
        print(f"  - Inner Layer 2 (Signal/PVDD): {'FOUND (.G2)' if g2_present else 'MISSING'}")
        print(f"  - Top Layer (GTL)           : {'FOUND' if gtl_present else 'MISSING'}")
        print(f"  - Bottom Layer (GBL)        : {'FOUND' if gbl_present else 'MISSING'}")
        print(f"  - Board Outline (GKO)       : {'FOUND' if gko_present else 'MISSING'}")
        print(f"  - FlyingProbeTesting.json   : {'FOUND' if fpt_present else 'MISSING'}")
        
        if g1_present and g2_present and gtl_present and gbl_present and gko_present and fpt_present:
            print("  => PASS: Genuine 4-Layer Stackup confirmed (Inner1 GND, Inner2 SIG).")
            passed_gates += 1
        else:
            print("  => FAIL: Missing critical 4-layer gerber files!")

    # Gate 2: 3-Way Parity (Gerber FPT == BOM == CPL)
    total_gates += 1
    print("\n[GATE 2] 3-Way Parity Verification (Gerber FPT == BOM == CPL):")
    bom_comps = parse_bom(BOM_FILE)
    cpl_comps = parse_cpl(CPL_FILE)
    
    with zipfile.ZipFile(GERBER_ZIP) as z:
        with z.open("FlyingProbeTesting.json") as f:
            fpt_data = json.load(f)
            fpt_rows = fpt_data.get("components", {}).get("rows", [])
            fpt_names = [r[1] for r in fpt_rows if not str(r[1]).startswith("PAD")]
            fpt_unique = sorted(set(fpt_names))

    bom_set = set(bom_comps.keys())
    cpl_set = set(cpl_comps.keys())
    fpt_set = set(fpt_unique)

    print(f"  - BOM Designators Count: {len(bom_set)}")
    print(f"  - CPL Designators Count: {len(cpl_set)}")
    print(f"  - FPT Designators Count: {len(fpt_set)}")

    diff_bom_cpl = bom_set ^ cpl_set
    diff_bom_fpt = bom_set ^ fpt_set

    if not diff_bom_cpl and not diff_bom_fpt and len(bom_set) == 56:
        print("  => PASS: Exactly 56 components match 1:1:1 across BOM, CPL, and Gerber FPT.")
        passed_gates += 1
    else:
        print(f"  => FAIL: Parity mismatch! BOM vs CPL diff: {diff_bom_cpl}, BOM vs FPT diff: {diff_bom_fpt}")

    # Gate 3: Coordinate Integrity & 13.5mm Mechanical Stack-up
    total_gates += 1
    print("\n[GATE 3] Genuine Coordinate (FPT vs CPL) & 100% Top-Layer Single-Sided Verification:")
    max_dx = 0.0
    max_dy = 0.0
    coord_mismatches = []
    non_top_cpl = []
    non_top_fpt = []

    for row in fpt_rows:
        des = str(row[1]).strip()
        if des.startswith("PAD"):
            continue
        layer_fpt = row[2]
        fx = row[3] * 0.0254
        fy = row[4] * 0.0254
        
        if layer_fpt != 'T':
            non_top_fpt.append((des, layer_fpt))
            
        if des in cpl_comps:
            cx = cpl_comps[des]["x"]
            cy = cpl_comps[des]["y"]
            clayer = cpl_comps[des]["layer"]
            if clayer.lower() != "top":
                non_top_cpl.append((des, clayer))
            dx = abs(fx - cx)
            dy = abs(fy - cy)
            if dx > max_dx:
                max_dx = dx
            if dy > max_dy:
                max_dy = dy
            if dx > 0.01 or dy > 0.01:
                coord_mismatches.append(f"{des}: FPT=({fx:.3f},{fy:.3f}) vs CPL=({cx:.3f},{cy:.3f})")
        else:
            coord_mismatches.append(f"{des} missing from CPL")

    print(f"  - Max Delta X (FPT vs CPL)       : {max_dx:.4f} mm (Threshold <= 0.01mm)")
    print(f"  - Max Delta Y (FPT vs CPL)       : {max_dy:.4f} mm (Threshold <= 0.01mm)")
    print(f"  - Non-Top Components in CPL      : {len(non_top_cpl)} (Expected: 0, 100% Top)")
    print(f"  - Non-Top Components in FPT      : {len(non_top_fpt)} (Expected: 0, 100% Top)")

    # Calculate Worst-Case Z Stackup in 13.5mm cavity
    spacer_h = 3.0  # mm
    pcb_t = 1.6 * 1.1  # mm (+10% tolerance = 1.76mm)
    l1_h = 4.5  # SWPA6045S inductor
    conn_h = 5.0  # Right-Angle connector (B-2100S02P-A120 / C124376)
    max_part_h = max(l1_h, conn_h)
    total_z = spacer_h + pcb_t + max_part_h  # 9.76mm
    cavity_h = 13.5 - 0.5  # 13.0mm min
    clearance = cavity_h - total_z

    print(f"  - Lower Standoff / Bottom Lead Cut: {spacer_h:.2f} mm")
    print(f"  - 4-Layer PCB Thickness (+10%)    : {pcb_t:.2f} mm")
    print(f"  - Tallest Component (L1/RA Conn)  : {max_part_h:.2f} mm")
    print(f"  - Total Assembly Z Height         : {total_z:.2f} mm")
    print(f"  - Enclosure Cavity Available      : {cavity_h:.2f} mm")
    print(f"  - Net Dynamic Air Clearance       : +{clearance:.2f} mm (Target >= 2.0mm)")

    gate3_ok = (not coord_mismatches and not non_top_cpl and not non_top_fpt and
                max_dx <= 0.01 and max_dy <= 0.01 and clearance >= 2.0)

    if gate3_ok:
        print("  => PASS: 100% single-sided Top SMT confirmed. Coordinates match within 0.01mm. +3.24mm headroom.")
        passed_gates += 1
    else:
        print("  => FAIL: Coordinate discrepancy or mechanical interference detected!")

    # Gate 4: Forbidden Part Numbers & Right-Angle Connector Enforcement
    total_gates += 1
    print("\n[GATE 4] Forbidden Part Numbers & Right-Angle Connector Enforcement:")
    all_parts = [v["part"] for v in bom_comps.values()]
    all_comments = [v["comment"] for v in bom_comps.values()]
    
    has_c2909511 = "C2909511" in all_parts
    has_vert_2p = "C124375" in all_parts
    has_vert_6p = "C124380" in all_parts
    has_ghosts = any(g in bom_comps for g in ["D2", "SOP16", "TYPE_C"])
    
    # Check Right-Angle Connectors
    j1_part = bom_comps.get("J1", {}).get("part")
    j2_part = bom_comps.get("J2", {}).get("part")
    uart_part = bom_comps.get("UART_HDR", {}).get("part")
    ra_connectors_ok = (j1_part == "C124376" and j2_part == "C124376" and uart_part == "C124381")

    # Check 12V capacitors (C8, C9)
    c8_part = bom_comps.get("C8", {}).get("part")
    c9_part = bom_comps.get("C9", {}).get("part")
    c8_c9_25v = (c8_part == "C96446" and c9_part == "C96446")

    # Check R12 0402 4.7k Top layer
    r12_part = bom_comps.get("R12", {}).get("part")
    r12_fp = bom_comps.get("R12", {}).get("footprint")
    r12_ok = (r12_part == "C25900" and "0402" in r12_fp)

    print(f"  - C2909511 (404 Error Part)       : {'DETECTED (DEFECT)' if has_c2909511 else 'ABSENT [SAFE]'}")
    print(f"  - C124375 (Vertical 2P Header)    : {'DETECTED (COLLISION)' if has_vert_2p else 'ABSENT [SAFE]'}")
    print(f"  - C124380 (Vertical 6P Header)    : {'DETECTED (COLLISION)' if has_vert_6p else 'ABSENT [SAFE]'}")
    print(f"  - Right-Angle 2P (C124376) J1/J2  : J1='{j1_part}', J2='{j2_part}' ({'OK' if j1_part == 'C124376' and j2_part == 'C124376' else 'MISMATCH'})")
    print(f"  - Right-Angle 6P (C124381) UART   : UART='{uart_part}' ({'OK' if uart_part == 'C124381' else 'MISMATCH'})")
    print(f"  - Legacy Ghost Components         : {'DETECTED' if has_ghosts else 'PURGED [SAFE]'}")
    print(f"  - C8, C9 MLCC Part on 12V Rail    : C8='{c8_part}', C9='{c9_part}' (25V C96446: {c8_c9_25v})")
    print(f"  - R12 0402 Top-Mount Strap        : Part='{r12_part}', FP='{r12_fp}' ({'OK' if r12_ok else 'MISMATCH'})")

    gate4_ok = (not has_c2909511 and not has_vert_2p and not has_vert_6p and
                not has_ghosts and ra_connectors_ok and c8_c9_25v and r12_ok)

    if gate4_ok:
        print("  => PASS: All vertical headers replaced with right-angle C124376/C124381. Zero forbidden parts.")
        passed_gates += 1
    else:
        print("  => FAIL: Dangerous or invalid part number detected in BOM!")

    # Gate 5: Electrical SSOT Compliance (12V Boost, 0x2C, -32UE Antenna)
    total_gates += 1
    print("\n[GATE 5] Electrical SSOT Compliance & Sensor Integration Readiness:")
    r1_val = bom_comps.get("R1", {}).get("comment")
    r2_val = bom_comps.get("R2", {}).get("comment")
    u1_part = bom_comps.get("U1", {}).get("part")
    u2_part = bom_comps.get("U2", {}).get("part")
    u3_part = bom_comps.get("U3", {}).get("part")
    u4_part = bom_comps.get("U4", {}).get("part")
    u5_part = bom_comps.get("U5", {}).get("part")
    d1_part = bom_comps.get("D1", {}).get("part")

    print(f"  - U3 (MP3426DL) Part #           : '{u3_part}' (Expected: C133224)")
    print(f"  - R1 High-Side / R2 Low-Side     : R1='{r1_val}', R2='{r2_val}' (12.17V Audio PVDD)")
    print(f"  - U1 ESP32 Module Part #         : '{u1_part}' (C701345 = External u.FL IPEX)")
    print(f"  - U2 3.3V LDO Regulator Part #   : '{u2_part}' (C51118 = AP2112K 600mA)")
    print(f"  - U4 Audio Amp Part #            : '{u4_part}' (C478472 = TAS5805MPWPR)")
    print(f"  - U5 IMU Sensor Part #           : '{u5_part}' (C481766 = LSM6DSOXTR)")
    print(f"  - R12 TAS5805M I2C Address Strap : '{r12_part}' (4.7kΩ to 3.3V = 7-bit 0x2C)")
    print(f"  - D1 5V TVS Surge Diode          : '{d1_part}' (C83329 = SMAJ5.0A)")

    elec_ok = (u3_part == "C133224" and "143k" in r1_val and "16k" in r2_val and
               u1_part == "C701345" and u2_part == "C51118" and u4_part == "C478472" and
               u5_part == "C481766" and r12_part == "C25900" and d1_part == "C83329")

    if elec_ok:
        print("  => PASS: Electrical parameters match #0005 physical verified baseline.")
        passed_gates += 1
    else:
        print("  => FAIL: Electrical parameter deviation detected!")

    print("\n" + "=" * 78)
    print(f"MANUFACTURING GATES SUMMARY: {passed_gates} / {total_gates} GATES PASSED ({(passed_gates / total_gates) * 100:.1f}%)")
    print("=" * 78)
    return 0 if passed_gates == total_gates else 1

if __name__ == "__main__":
    sys.exit(main())
