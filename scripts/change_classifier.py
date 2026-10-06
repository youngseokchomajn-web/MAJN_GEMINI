#!/usr/bin/env python3
"""Read-only Phase 0 changed-path classifier."""

from __future__ import annotations
import fnmatch
import sys

RULES = {
    "cert": ["인증준비/**"],
    "pcb": ["**/*.epro2", "**/*pcb*", "**/*PCB*"],
    "firmware": ["**/firmware/**", "**/*.ino", "**/*.cpp", "**/*.h"],
    "ai_ops": [".gem/**", "scripts/**", ".github/**"],
}

def classify(path: str) -> set[str]:
    p = path.replace("\\", "/").lstrip("./")
    hits = set()
    for track, patterns in RULES.items():
        if any(fnmatch.fnmatch(p, pattern) for pattern in patterns):
            hits.add(track)
    return hits or {"general"}

def main() -> int:
    for raw in sys.stdin:
        path = raw.strip()
        if not path:
            continue
        print(f"{','.join(sorted(classify(path)))}\t{path}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
