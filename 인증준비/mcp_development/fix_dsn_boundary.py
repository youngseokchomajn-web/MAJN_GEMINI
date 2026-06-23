#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""majn_pcb2.dsn(전체가 'u1'로 병합된 EasyEDA export)의 깨진 boundary를
실제 핀 bounding box로 교체 → FreeRouting이 먹을 수 있는 DSN 생성.
핀 ID(패드 UUID)는 그대로 두어 SES 재가져오기 호환 유지."""
import re, sys

SRC = "majn_pcb2.dsn"
OUT = "majn_pcb2_fixed.dsn"
MARGIN = 100.0  # mil

def main():
    txt = open(SRC, encoding="utf-8").read()
    # 모든 (pin padstack pinid X Y) 좌표 추출
    pins = re.findall(r"\(pin\s+\S+\s+\S+\s+(-?\d+\.?\d*)\s+(-?\d+\.?\d*)\)", txt)
    if not pins:
        print("[ERR] no pins found"); sys.exit(1)
    xs = [float(x) for x, y in pins]
    ys = [float(y) for x, y in pins]
    x1, x2 = min(xs) - MARGIN, max(xs) + MARGIN
    y1, y2 = min(ys) - MARGIN, max(ys) + MARGIN
    print(f"pins={len(pins)}  x:[{min(xs):.1f},{max(xs):.1f}]  y:[{min(ys):.1f},{max(ys):.1f}]")
    print(f"x-span={(max(xs)-min(xs))/39.3701:.1f}mm  y-span={(max(ys)-min(ys))/39.3701:.1f}mm")
    print(f"new boundary mil: ({x1:.1f},{y1:.1f})-({x2:.1f},{y2:.1f})")

    # 넷/클래스 sanity
    nets = re.findall(r"\(net\s+([^\s()]+)\s*\n\s*\(pins", txt)
    print(f"nets in network: {len(nets)}")

    # boundary 교체: 닫힌 사각형 path
    newb = (f"(boundary(path signal 0 "
            f"{x1:.2f} {y1:.2f} {x2:.2f} {y1:.2f} {x2:.2f} {y2:.2f} {x1:.2f} {y2:.2f} {x1:.2f} {y1:.2f} )\n    )")
    txt2 = re.sub(r"\(boundary\(path signal[^\n]*\n\s*\)", newb, txt, count=1)
    if txt2 == txt:
        print("[WARN] boundary not replaced — pattern mismatch")
    open(OUT, "w", encoding="utf-8").write(txt2)
    print(f"[OK] wrote {OUT} ({len(txt2)} bytes)")
    # 확인
    bm = re.search(r"\(boundary.*", txt2)
    print("boundary now:", bm.group(0)[:120] if bm else "??")

if __name__ == "__main__":
    main()
