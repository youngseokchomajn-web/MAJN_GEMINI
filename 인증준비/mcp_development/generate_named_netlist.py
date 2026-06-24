#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""fresh-eye 점검용: design_flow 넷을 라이브 심볼 핀이름과 함께 출력 + IC 미연결핀."""
import json, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

d = json.load(open("mcp_design_flow.json", encoding="utf-8"))
sym = json.load(open("a1_symbol_verify.json", encoding="utf-8"))["pins_by_designator"]
symmap = {des: {str(n): str(nm) for n, nm in pins} for des, pins in sym.items()}
symnames = {des: [(str(n), str(nm)) for n, nm in pins] for des, pins in sym.items()}

def resolve(des, pinkey):
    """design_flow pinkey(번호 or 이름) -> (symbol_pinnum, symbol_pinname)"""
    m = symmap.get(des, {})
    pk = str(pinkey)
    if pk in m:  # 번호 직접
        return pk, m[pk]
    # 이름 기반 (U1 GPIOxx 등) — 별칭 매칭
    def norm(s): return "".join(c for c in s if c.isalnum()).lower()
    pkn = norm(pk)
    # gpio/io alias
    def gnum(s):
        n = norm(s)
        if n.startswith("gpio"): return n[4:]
        if n.startswith("io"): return n[2:]
        return None
    g = gnum(pk)
    for num, nm in symnames.get(des, []):
        if norm(nm) == pkn: return num, nm
        if g and gnum(nm) == g: return num, nm
        if pkn and (norm(nm).startswith(pkn) or pkn.startswith(norm(nm))): return num, nm
    return pk, "??"

# 1) 넷별 출력
print("="*70); print("NET LIST (with live symbol pin names)"); print("="*70)
connected = {}  # des -> set(symbol pinnum)
for net in sorted(d["nets"].keys()):
    parts = []
    for des, pin in d["nets"][net]:
        num, nm = resolve(des, pin)
        connected.setdefault(des, set()).add(num)
        parts.append(f"{des}.{num}({nm})")
    print(f"\n[{net}]  ({len(parts)} pins)")
    print("   " + " · ".join(parts))

# 2) IC 미연결(부유) 핀
print("\n"+"="*70); print("IC FLOATING PINS (미연결 = ERC 경고/NC 후보)"); print("="*70)
for des in ["U1","U2","U3","U4","U5","USB_C"]:
    allpins = symnames.get(des, [])
    conn = connected.get(des, set())
    floating = [(n,nm) for n,nm in allpins if n not in conn]
    if floating:
        print(f"\n{des}: {len(floating)} floating")
        print("   " + ", ".join(f"{n}={nm}" for n,nm in floating))
