#!/usr/bin/env python3
"""
MAJN PCB Automated Verification Tool: Gerber Package Integrity Checker
Author: Antigravity (Google DeepMind pair programming assistant)
Purpose: Analyzes Gerber zip archives, verifies 4-layer stackup presence,
         checks drill files, board outline, and outputs file table with SHA-256.
"""

import sys
import os
import zipfile
import hashlib

EXPECTED_REV_B_FILES = {
    "Gerber_TopLayer.GTL": "Top Copper Layer",
    "Gerber_BottomLayer.GBL": "Bottom Copper Layer",
    "Gerber_InnerLayer1.G1": "Inner 1 (GND Plane)",
    "Gerber_InnerLayer2.G2": "Inner 2 (Power/Signals)",
    "Gerber_TopSilkscreenLayer.GTO": "Top Silkscreen",
    "Gerber_BottomSilkscreenLayer.GBO": "Bottom Silkscreen",
    "Gerber_TopSolderMaskLayer.GTS": "Top Solder Mask",
    "Gerber_BottomSolderMaskLayer.GBS": "Bottom Solder Mask",
    "Gerber_TopPasteMaskLayer.GTP": "Top Solder Paste",
    "Gerber_BoardOutlineLayer.GKO": "Board Outline / Keepout",
    "Drill_PTH_Through.DRL": "Plated Through Hole Drills",
    "Drill_NPTH_Through.DRL": "Non-Plated Drills (Mounting Holes)",
    "Drill_PTH_Through_Via.DRL": "Via Drills",
}

def check_gerber_zip(zip_path):
    if not os.path.exists(zip_path):
        raise FileNotFoundError(f"Gerber archive not found: {zip_path}")

    with open(zip_path, "rb") as f:
        zip_sha256 = hashlib.sha256(f.read()).hexdigest()

    print(f"[*] Analyzing Gerber Archive: {zip_path}")
    print(f"[*] Archive SHA-256: {zip_sha256}")

    with zipfile.ZipFile(zip_path, "r") as z:
        infolist = z.infolist()
        file_map = {item.filename: item for item in infolist}

    print(f"[*] Total Files in Archive: {len(file_map)}")

    missing_critical = []
    for exp_file, desc in EXPECTED_REV_B_FILES.items():
        if exp_file in file_map:
            sz = file_map[exp_file].file_size
            print(f"    [OK] {exp_file:32s} ({desc}): {sz:8d} bytes")
        else:
            print(f"    [MISSING] {exp_file:32s} ({desc})")
            missing_critical.append(exp_file)

    # 4-Layer Verification
    is_4_layer = ("Gerber_InnerLayer1.G1" in file_map) and ("Gerber_InnerLayer2.G2" in file_map)
    if is_4_layer:
        print("[PASS] 4-Layer Stackup VERIFIED (G1 GND and G2 VCC inner layers present).")
    else:
        print("[FAIL] Not a verified 4-layer board (inner layer files missing).")

    return {
        "zip_path": zip_path,
        "zip_sha256": zip_sha256,
        "total_files": len(file_map),
        "is_4_layer": is_4_layer,
        "missing_critical": missing_critical
    }

if __name__ == "__main__":
    g_path = sys.argv[1] if len(sys.argv) > 1 else "인증준비/pcb/260708/Gerber_PCB1_revB_2026-07-09.zip"
    check_gerber_zip(g_path)
