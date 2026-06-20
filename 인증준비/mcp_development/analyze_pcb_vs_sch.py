#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""오프라인: PCB2 넷리스트 ↔ 회로도 넷리스트 (부품,핀번호) 단위 대조.
회로도는 이미 스펙과 일치 검증됨 → PCB==회로도이면 PCB==스펙.
풋프린트 정합(U3=15, J1/J2=2)과 GND 흡수도 점검."""
import json
from collections import defaultdict

def _iter_objs(text):
    """연결된 다중 JSON(JLCEDA 멀티페이지) 파싱."""
    dec = json.JSONDecoder()
    i, n = 0, len(text)
    while i < n:
        while i < n and text[i] in " \t\r\n":
            i += 1
        if i >= n: break
        obj, end = dec.raw_decode(text, i)
        yield obj
        i = end

def load(fn):
    text = open(fn, encoding="utf-8").read()
    pinmap = defaultdict(dict)
    for nl in _iter_objs(text):
        comps = nl.get("components", nl) if isinstance(nl, dict) else {}
        for uid, c in comps.items():
            if not isinstance(c, dict): continue
            des = c.get("props", {}).get("Designator")
            if not des: continue
            for num, pd in c.get("pinInfoMap", {}).items():
                pinmap[des][str(num)] = (pd.get("net") or "").strip()
    return pinmap

def main():
    sch = load("netlist_sch_live.json")
    pcb = load("netlist_pcb2.json")

    print("=== 1. 부품/핀수 정합 ===")
    print(f"회로도 부품 {len(sch)} / PCB 부품 {len(pcb)}")
    miss = sorted(set(sch) - set(pcb)); extra = sorted(set(pcb) - set(sch))
    if miss: print("  [PCB 누락]", miss)
    if extra: print("  [PCB 여분]", extra)
    for d in ["U3","J1","J2","U4","U5","U1"]:
        print(f"  {d}: 회로도 {len(sch.get(d,{}))}핀 / PCB {len(pcb.get(d,{}))}핀")

    print("\n=== 2. 핀별 net 대조 (부품,핀번호) ===")
    mism = []
    only_sch = []   # 회로도엔 net, PCB엔 다름/없음
    common_des = set(sch) & set(pcb)
    total = ok = 0
    for des in sorted(common_des):
        nums = set(sch[des]) | set(pcb[des])
        for num in nums:
            sn = sch[des].get(num, "<없음>")
            pn = pcb[des].get(num, "<없음>")
            total += 1
            if sn == pn:
                ok += 1
            else:
                mism.append((des, num, sn, pn))
    print(f"  비교 핀 {total} / 일치 {ok} / 불일치 {len(mism)}")
    for des, num, sn, pn in mism[:80]:
        print(f"    {des}.{num}: 회로도='{sn}'  PCB='{pn}'")
    if len(mism) > 80: print(f"    ... 외 {len(mism)-80}건")

    print("\n=== 3. GND 멤버 대조 ===")
    def gnd_members(pm): return {(d, n) for d, pins in pm.items() for n, net in pins.items() if net == "GND"}
    gs, gp = gnd_members(sch), gnd_members(pcb)
    print(f"  회로도 GND {len(gs)} / PCB GND {len(gp)}")
    only_pcb_gnd = gp - gs
    only_sch_gnd = gs - gp
    if only_pcb_gnd: print("  [PCB에만 GND] ", sorted(only_pcb_gnd))
    if only_sch_gnd: print("  [회로도에만 GND]", sorted(only_sch_gnd))
    if not only_pcb_gnd and not only_sch_gnd: print("  ✅ GND 멤버 동일(흡수/누락 없음)")

    print("\n=== 4. net 집합 비교 ===")
    def nets_of(pm):
        s = defaultdict(set)
        for d, pins in pm.items():
            for n, net in pins.items():
                if net: s[net].add((d, n))
        return s
    sn_, pn_ = nets_of(sch), nets_of(pcb)
    print(f"  회로도 net {len(sn_)} / PCB net {len(pn_)}")
    only_s = set(sn_) - set(pn_); only_p = set(pn_) - set(sn_)
    if only_s: print("  [PCB에 없는 net]", sorted(only_s))
    if only_p: print("  [회로도에 없는 net]", sorted(only_p))

    fp_ok = (len(pcb.get("U3",{}))==15 and len(pcb.get("J1",{}))==2 and len(pcb.get("J2",{}))==2)
    verdict = "PASS ✅" if (not miss and not extra and not mism and not only_pcb_gnd and not only_sch_gnd and fp_ok) else "FAIL ❌"
    print(f"\n================ Phase4 PCB 검증: {verdict} ================")
    print(f"  부품정합:{not miss and not extra} · 핀net일치:{not mism} · GND동일:{not only_pcb_gnd and not only_sch_gnd} · 풋프린트(U3=15,J1/J2=2):{fp_ok}")

if __name__ == "__main__":
    main()
