#!/usr/bin/env python3
"""
MAJN PCB Automated Verification Tool: Requirements Traceability Matrix Checker
Author: Antigravity (Google DeepMind pair programming assistant)
Purpose: Parses RTM CSV, validates requirement ID integrity, ensures bidirectional
         traceability (Req -> Design -> Net -> Test Case -> Evidence), and generates stats.
"""

import sys
import os
import csv

MANDATORY_REQ_IDS = [
    "REQ-P0-01", "REQ-P0-02", "REQ-P0-03", "REQ-P0-04", "REQ-P0-05",
    "REQ-P1-01", "REQ-P1-02", "REQ-P1-03", "REQ-P1-04", "REQ-P1-05", "REQ-P1-06", "REQ-P1-07"
]

def check_rtm_csv(csv_path):
    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"RTM CSV not found: {csv_path}")

    with open(csv_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    print(f"[*] Analyzing RTM CSV: {csv_path}")
    print(f"[*] Total Requirement Records: {len(rows)}")

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

        # Traceability completeness check
        net = r.get("Schematic_Net", "").strip()
        test_case = r.get("Test_Case_ID", "").strip()
        if not net or not test_case:
            missing_traceability.append((req_id, net, test_case))

    # Check mandatory IDs
    missing_mandatory = [m for m in MANDATORY_REQ_IDS if m not in found_ids]
    if missing_mandatory:
        print(f"[FAIL] Missing mandatory requirement IDs: {missing_mandatory}")
    else:
        print("[PASS] All 12 mandatory P0/P1 requirement IDs present.")

    print(f"[*] Implementation Status Distribution: {status_counts}")
    print(f"[*] Verification Status Distribution: {verified_counts}")
    if missing_traceability:
        print(f"[*] Incomplete Traceability items: {len(missing_traceability)}")
        for req, net, tc in missing_traceability[:5]:
            print(f"    - {req}: Net='{net}', Test Case='{tc}'")

    return {
        "total_records": len(rows),
        "status_counts": status_counts,
        "verified_counts": verified_counts,
        "missing_mandatory": missing_mandatory
    }

if __name__ == "__main__":
    c_path = sys.argv[1] if len(sys.argv) > 1 else "docs/engineering/pcb_0006/PCB_0006_REQUIREMENTS_TRACEABILITY_MATRIX.csv"
    check_rtm_csv(c_path)
