#!/usr/bin/env python3
"""
MAJN Requirements Traceability & Gate Readiness Checker (v2.0)
--------------------------------------------------------------
Audits all P0, P1, and P2 engineering requirements against verification status.
MANDATORY: Returns sys.exit(1) if any Critical P0 requirement is missing or failing.
"""

import sys
import re
import argparse
from pathlib import Path

def parse_markdown_requirements(doc_path):
    p = Path(doc_path)
    if not p.exists():
        print(f"[ERROR] Requirements document not found: {p}", file=sys.stderr)
        sys.exit(1)
        
    reqs = {}
    with open(p, "r", encoding="utf-8") as f:
        lines = f.readlines()

    # Regex to parse Markdown table row: | REQ-ID | Priority | Name | ... | Status | ...
    row_pattern = re.compile(r"^\|\s*\*\*(REQ-[A-Z0-9_-]+)\*\*\s*\|\s*\*\*([A-Z0-9]+)\*\*\s*\|\s*([^|]+)\|\s*([^|]+)\|\s*([^|]+)\|\s*([^|]+)\|\s*([^|]+)\|\s*([^|]+)\|")

    for line in lines:
        m = row_pattern.match(line.strip())
        if m:
            req_id = m.group(1).strip()
            prio = m.group(2).strip()
            name = m.group(3).strip()
            circuit = m.group(5).strip()
            criteria = m.group(7).strip()
            status = m.group(8).strip()
            reqs[req_id] = {
                "priority": prio,
                "name": name,
                "circuit": circuit,
                "criteria": criteria,
                "status": status
            }
    return reqs

def audit_requirements(reqs):
    violations = []
    warnings = []
    p0_count = 0
    p1_count = 0
    p2_count = 0

    if not reqs:
        print("[ERROR] No requirements parsed from specification file!", file=sys.stderr)
        sys.exit(1)

    for req_id, data in reqs.items():
        prio = data["priority"]
        status = data["status"]
        name = data["name"]

        if prio == "P0":
            p0_count += 1
            if "확정" not in status and "PASS" not in status and "VERIFIED" not in status:
                violations.append(f"P0 REQUIREMENT NOT CLOSED: {req_id} ('{name}') has status '{status}'")
            else:
                print(f"[PASS] P0 Requirement {req_id}: '{name}' is verified/closed.")
        elif prio == "P1":
            p1_count += 1
            if "확정" not in status and "PASS" not in status and "VERIFIED" not in status:
                warnings.append(f"P1 Requirement pending: {req_id} ('{name}') has status '{status}'")
            else:
                print(f"[PASS] P1 Requirement {req_id}: '{name}' verified.")
        else:
            p2_count += 1

    print("\n" + "=" * 60)
    print(f"REQUIREMENTS TRACEABILITY AUDIT: {len(reqs)} items total (P0={p0_count}, P1={p1_count}, P2={p2_count})")
    print(f"Violations: {len(violations)}, Warnings: {len(warnings)}")
    print("=" * 60)

    for w in warnings:
        print(f"  [WARN] {w}")
    for v in violations:
        print(f"  [FAIL] {v}", file=sys.stderr)

    if violations:
        print("\n>>> AUDIT FAILED: Unresolved Critical P0 requirements remain (sys.exit(1)) <<<", file=sys.stderr)
        sys.exit(1)
    else:
        print("\n>>> AUDIT PASSED: All Critical P0 requirements verified (sys.exit(0)) <<<")
        sys.exit(0)

def main():
    parser = argparse.ArgumentParser(description="Audit requirements traceability matrix.")
    parser.add_argument("--req-doc", type=str, required=True, help="Path to DOC03 requirements Markdown file")
    args = parser.parse_args()
    reqs = parse_markdown_requirements(args.req_doc)
    audit_requirements(reqs)

if __name__ == "__main__":
    main()
