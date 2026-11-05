#!/usr/bin/env python3
"""
MAJN PCB Automated Verification Tool: Gerber Package Integrity Checker (v2.0)
Author: Antigravity (Google DeepMind pair programming assistant)
Purpose: Analyzes Gerber zip archives, verifies 4-layer copper files presence,
         checks drill files and keepout, and explicitly distinguishes
         between 'Gerber CAD Layer Presence' vs 'Physical Fab Stackup Confirmation'.
"""

import sys
import os
import zipfile
import hashlib

EXPECTED_REV_B_FILES = {
    "Gerber_TopLayer.GTL": "Top Copper Layer (Layer 1)",
    "Gerber_BottomLayer.GBL": "Bottom Copper Layer (Layer 4)",
    "Gerber_InnerLayer1.G1": "Inner 1 GND Plane (Layer 2)",
    "Gerber_InnerLayer2.G2": "Inner 2 VCC/Signals (Layer 3)",
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

    # 4-Layer CAD Presence Verification
    is_4_layer_cad = ("Gerber_InnerLayer1.G1" in file_map) and ("Gerber_InnerLayer2.G2" in file_map)
    if is_4_layer_cad and not missing_critical:
        print("[PASS] 4-Layer CAD Dataset VERIFIED (Top, G1 GND, G2 VCC, Bottom copper layers present).")
    else:
        print("[FAIL] Incomplete Gerber dataset.")

    # Engineering Boundary Note
    print("\n[*] Physical Stackup Verification Scope Boundary:")
    print("    [NOTE] Gerber CAD files verify layer presence and routing geometry.")
    print("    [PENDING] Physical Fab Stackup (Prepreg 7628 0.21mm, Core 1.065mm, 1.6mm total thickness,")
    print("             copper weight 1oz/1oz, and controlled impedance) requires JLCPCB fab invoice & cross-section validation.")

    return {
        "zip_path": zip_path,
        "zip_sha256": zip_sha256,
        "total_files": len(file_map),
        "is_4_layer_cad": is_4_layer_cad,
        "missing_critical": missing_critical,
        "fab_stackup_status": "PENDING_FAB_CONFIRMATION"
    }

if __name__ == "__main__":
    g_path = sys.argv[1] if len(sys.argv) > 1 else "인증준비/pcb/260708/Gerber_PCB1_revB_2026-07-09.zip"
    check_gerber_zip(g_path)
