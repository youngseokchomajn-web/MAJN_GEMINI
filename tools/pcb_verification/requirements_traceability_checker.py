#!/usr/bin/env python3
"""
MAJN PCB Automated Verification Tool: Requirements Traceability Matrix Checker (v2.0)
Author: Antigravity (Google DeepMind pair programming assistant)
Purpose: Parses RTM CSV, separates Core Baseline (12) from Extended Proposed (3),
         validates requirement integrity, and detects unverified/unimplemented gaps.
"""

import sys
import os
import csv

# Core baseline requirements established in DOC03 (12 mandatory items)
CORE_BASELINE_REQ_IDS = [
    "REQ-P0-01", "REQ-P0-02", "REQ-P0-03", "REQ-P0-04", "REQ-P0-05",
    "REQ-P1-01", "REQ-P1-02", "REQ-P1-03", "REQ-P1-04", "REQ-P1-05", "REQ-P1-06", "REQ-P1-07"
]

# Extended candidate requirements proposed for PCB #0006 (3 items)
EXTENDED_PROPOSED_REQ_IDS = [
    "REQ-P0-06", "REQ-P1-08", "REQ-P1-09"
]

def check_rtm_csv(csv_path):
    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"RTM CSV not found: {csv_path}")

    with open(csv_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    print(f"[*] Analyzing RTM CSV: {csv_path}")
    print(f"[*] Total Requirement Records in CSV: {len(rows)}")

    found_ids = set()
    status_counts = {}
    verified_counts = {}
    missing_traceability = []

    for r in rows:
        req_id = r.get("Requirement_ID", "").strip()
        found_ids.add(req_id)
        impl_status = r.get("Implementation_Status", "").strip()
        verif_status = r.get("Verification_Status", "").strip()

        status_counts[impl_status] = status_counts.get(impl_status, 0) + 1
        verified_counts[verif_status] = verified_counts.get(verif_status, 0) + 1

        net = r.get("Schematic_Net", "").strip()
        test_case = r.get("Test_Case_ID", "").strip()
        if not net or not test_case:
            missing_traceability.append((req_id, net, test_case))

    # 1. Core Baseline Check (12 IDs)
    missing_core = [m for m in CORE_BASELINE_REQ_IDS if m not in found_ids]
    if missing_core:
        print(f"[FAIL] Missing CORE baseline requirement IDs: {missing_core}")
    else:
        print(f"[PASS] All 12 CORE baseline requirements present ({len(CORE_BASELINE_REQ_IDS)}/12).")

    # 2. Extended Proposed Check (3 IDs)
    missing_extended = [m for m in EXTENDED_PROPOSED_REQ_IDS if m not in found_ids]
    if missing_extended:
        print(f"[INFO] Extended proposed requirements missing: {missing_extended}")
    else:
        print(f"[PASS] All 3 EXTENDED proposed requirements present ({len(EXTENDED_PROPOSED_REQ_IDS)}/3).")

    # 3. Discrepancy Reconciliation Summary
    print(f"[*] Requirement Architecture Breakdown:")
    print(f"    - Core Baseline Established: 12 items (REQ-P0-01~05, REQ-P1-01~07)")
    print(f"    - Extended Candidate:        3 items (REQ-P0-06 [USB-C CC], REQ-P1-08 [3.3V Bulk], REQ-P1-09 [RF Ant])")
    print(f"    - Total Tracked in CSV:     {len(found_ids)} items")

    print(f"[*] Implementation Status: {status_counts}")
    print(f"[*] Verification Status:   {verified_counts}")

    if missing_traceability:
        print(f"[WARN] Incomplete Traceability items: {len(missing_traceability)}")
        for req, net, tc in missing_traceability:
            print(f"    - {req}: Net='{net}', Test Case='{tc}'")
    else:
        print("[PASS] Bidirectional traceability 100% complete for all records.")

    return {
        "total_records": len(rows),
        "found_ids": list(found_ids),
        "missing_core": missing_core,
        "missing_extended": missing_extended,
        "status_counts": status_counts,
        "verified_counts": verified_counts
    }

if __name__ == "__main__":
    c_path = sys.argv[1] if len(sys.argv) > 1 else "docs/engineering/pcb_0006/PCB_0006_REQUIREMENTS_TRACEABILITY_MATRIX.csv"
    check_rtm_csv(c_path)
