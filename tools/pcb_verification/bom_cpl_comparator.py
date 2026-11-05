#!/usr/bin/env python3
"""
MAJN PCB Automated Verification Tool: BOM vs CPL vs JSON Comparator
Author: Antigravity (Google DeepMind pair programming assistant)
Purpose: Cross-verifies designators, LCSC part numbers, footprints, layers, and coordinates
         between manufacturing BOM, placement CPL, and structured JSON design baseline.
"""

import sys
import os
import csv
import json

def load_bom(bom_path):
    with open(bom_path, "r", encoding="utf-8") as f:
        reader = csv.reader(f)
        rows = list(reader)
    if not rows:
        raise ValueError(f"Empty BOM file: {bom_path}")
    bom_map = {}
    for r in rows[1:]:
        if not r or not any(r): continue
        comment, des_str, fp, lcsc = r[0].strip(), r[1].strip(), r[2].strip(), r[3].strip()
        for d in des_str.replace(" ", "").split(","):
            if d:
                bom_map[d] = {"comment": comment, "footprint": fp, "lcsc": lcsc}
    return bom_map

def load_cpl(cpl_path):
    with open(cpl_path, "r", encoding="utf-8") as f:
        reader = csv.reader(f)
        rows = list(reader)
    if not rows:
        raise ValueError(f"Empty CPL file: {cpl_path}")
    cpl_map = {}
    for r in rows[1:]:
        if not r or not any(r): continue
        d = r[0].strip()
        x = float(r[1].replace("mm", "").strip())
        y = float(r[2].replace("mm", "").strip())
        layer = r[3].strip()
        rot = float(r[4].strip())
        cpl_map[d] = {"x": x, "y": y, "layer": layer, "rot": rot}
    return cpl_map

def load_json(json_path):
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    json_map = {}
    for c in data.get("components", []):
        d = c["designator"].strip()
        json_map[d] = {
            "name": c.get("name", ""),
            "lcsc": c.get("lcsc_id", ""),
            "package": c.get("package", ""),
            "x": float(c.get("x", 0.0)),
            "y": float(c.get("y", 0.0)),
            "angle": float(c.get("angle", 0.0))
        }
    return json_map

def run_comparison(bom_path, cpl_path, json_path):
    bom = load_bom(bom_path)
    cpl = load_cpl(cpl_path)
    js = load_json(json_path)

    bom_set = set(bom.keys())
    cpl_set = set(cpl.keys())
    json_set = set(js.keys())

    print(f"[*] BOM Total Parts: {len(bom_set)}")
    print(f"[*] CPL Total Parts: {len(cpl_set)}")
    print(f"[*] JSON Total Parts: {len(json_set)}")

    # 1. Designator Set Equality
    diff_bom_cpl = bom_set ^ cpl_set
    diff_bom_json = bom_set ^ json_set
    if not diff_bom_cpl and not diff_bom_json:
        print("[PASS] Designator sets are 100% IDENTICAL across BOM, CPL, and JSON.")
    else:
        print(f"[FAIL] Designator mismatch! BOM vs CPL delta: {diff_bom_cpl}, BOM vs JSON delta: {diff_bom_json}")

    # 2. Layers
    layers = set(cpl[d]["layer"] for d in cpl)
    print(f"[*] SMT Layers present: {layers}")

    # 3. LCSC Part ID Differences
    lcsc_diffs = []
    for d in sorted(bom_set):
        b_lcsc = bom[d]["lcsc"]
        j_lcsc = js.get(d, {}).get("lcsc", "")
        if b_lcsc != j_lcsc:
            lcsc_diffs.append((d, b_lcsc, j_lcsc, bom[d]["comment"], js[d]["name"]))

    # 4. Footprint / Package Differences
    fp_diffs = []
    for d in sorted(bom_set):
        b_fp = bom[d]["footprint"]
        j_fp = js.get(d, {}).get("package", "")
        if b_fp.lower() != j_fp.lower():
            fp_diffs.append((d, b_fp, j_fp))

    # 5. Coordinates Differences (CPL vs JSON)
    coord_diffs = []
    for d in sorted(cpl_set):
        if d in js:
            cx, cy, crot = cpl[d]["x"], cpl[d]["y"], cpl[d]["rot"]
            jx, jy, jrot = js[d]["x"], js[d]["y"], js[d]["angle"]
            dx = abs(cx - jx)
            dy = abs(cy - jy)
            drot = abs(crot - jrot) % 360
            if dx > 0.05 or dy > 0.05 or (drot > 0.05 and drot < 359.95):
                coord_diffs.append((d, cx, cy, crot, jx, jy, jrot, dx, dy, drot))

    print(f"[*] LCSC Part # Diffs: {len(lcsc_diffs)} items")
    for d, b_l, j_l, b_c, j_n in lcsc_diffs:
        print(f"    - {d}: BOM={b_l} ({b_c}) vs JSON={j_l} ({j_n})")

    print(f"[*] Package / Footprint Diffs: {len(fp_diffs)} items")
    print(f"[*] Coordinate Significant Shifts (>0.05mm): {len(coord_diffs)} items")
    for d, cx, cy, cr, jx, jy, jr, dx, dy, dr in coord_diffs:
        print(f"    - {d}: CPL=({cx:.2f}, {cy:.2f}) vs JSON=({jx:.2f}, {jy:.2f}), delta=({dx:.2f}, {dy:.2f})mm, rot_delta={dr:.1f}deg")

    return {
        "bom_count": len(bom_set),
        "cpl_count": len(cpl_set),
        "json_count": len(json_set),
        "lcsc_diffs": lcsc_diffs,
        "fp_diffs": fp_diffs,
        "coord_diffs": coord_diffs,
        "layers": list(layers)
    }

if __name__ == "__main__":
    b_path = sys.argv[1] if len(sys.argv) > 1 else "인증준비/pcb/260708/BOM_PCB1_revB_2026-07-09.csv"
    c_path = sys.argv[2] if len(sys.argv) > 2 else "인증준비/pcb/260708/CPL_PCB1_revB_2026-07-09.csv"
    j_path = sys.argv[3] if len(sys.argv) > 3 else "monogpt_submission_package/01_설계데이터_후보/A_mcp_design_flow_v1.9.2_2026-07-08.json"
    run_comparison(b_path, c_path, j_path)
