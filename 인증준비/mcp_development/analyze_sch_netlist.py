#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""오프라인 엄밀 분석: netlist_sch_live.json(실제) ↔ mcp_design_flow.json(스펙).
모든 핀을 (designator, pinNumber) 정규형으로 환원해 net 집합 대조."""
import json, sys
from collections import defaultdict

def norm(s): return "".join(c for c in str(s or "") if c.isalnum()).lower()
def gpio_num(s):
    n = norm(s)
    if n.startswith("gpio"): return n[4:]
    if n.startswith("io"): return n[2:]
    return None

def name_eq(pinkey, number, name):
    """spec pinkey 가 actual 핀(number,name) 과 동일 핀인지."""
    pk = norm(pinkey); nu = norm(number); na = norm(name)
    if pk == nu or pk == na: return True
    tg = gpio_num(pinkey)
    if tg and (gpio_num(number) == tg or gpio_num(name) == tg): return True
    # rxd0↔rxd, txd0↔txd 등 접두/포함(이름끼리만, 번호는 정확 일치만)
    if pk and na and (na.startswith(pk) or pk.startswith(na)): return True
    return False

def main():
    spec = json.load(open("mcp_design_flow.json", encoding="utf-8"))
    nl = json.load(open("netlist_sch_live.json", encoding="utf-8"))
    spec_nets = spec["nets"]
    spec_des = {c["designator"] for c in spec["components"]}

    # actual: des -> {number: {"name":, "net":}}
    actual = defaultdict(dict)
    comp_props = {}
    for uid, c in nl.get("components", {}).items():
        des = c.get("props", {}).get("Designator")
        if not des: continue
        comp_props[des] = uid
        for pnum, pd in c.get("pinInfoMap", {}).items():
            actual[des][str(pnum)] = {"name": pd.get("name", ""), "net": (pd.get("net") or "").strip()}

    print("=== 1. 부품 존재/핀수 ===")
    print(f"스펙 부품 {len(spec_des)} / 실제 부품 {len(actual)}")
    miss_comp = sorted(spec_des - set(actual.keys()))
    extra_comp = sorted(set(actual.keys()) - spec_des)
    if miss_comp: print("  [누락] ", miss_comp)
    if extra_comp: print("  [여분] ", extra_comp)
    for d in ["U3","J1","J2","U4","U5","U1"]:
        print(f"  {d}: 실제 {len(actual.get(d,{}))}핀")

    # spec pinkey -> actual number 해석
    def resolve(des, pinkey):
        pins = actual.get(des, {})
        # 1) 번호 정확 일치
        if str(pinkey) in pins: return str(pinkey)
        # 2) 이름/alias
        for num, info in pins.items():
            if name_eq(pinkey, num, info["name"]): return num
        return None

    # 정규형 net 집합
    spec_net_members = defaultdict(set)   # net -> {(des,number)}
    unresolved = []
    for net, plist in spec_nets.items():
        for des, pinkey in plist:
            num = resolve(des, pinkey)
            if num is None:
                unresolved.append((net, des, pinkey))
            else:
                spec_net_members[net].add((des, num))

    actual_net_members = defaultdict(set) # net -> {(des,number)}
    for des, pins in actual.items():
        for num, info in pins.items():
            if info["net"]:
                actual_net_members[info["net"]].add((des, num))

    print("\n=== 2. 스펙 핀 해석 실패(심볼에 해당 핀 없음) ===")
    if unresolved:
        for net, des, pk in unresolved:
            print(f"  {des}.{pk} (net {net})  ← 실제 심볼에서 핀 못 찾음")
    else:
        print("  없음 (모든 스펙 핀이 실제 심볼 핀으로 해석됨)")

    print("\n=== 3. net 단위 멤버 대조 (스펙 38넷) ===")
    all_ok = True
    total_missing = total_extra = total_wrong = 0
    for net in spec_nets:
        s = spec_net_members.get(net, set())
        a = actual_net_members.get(net, set())
        missing = s - a   # 스펙엔 있는데 실제 net 에 없음 (floating 또는 다른 net 흡수)
        extra = a - s     # 실제 net 에 있는데 스펙엔 없음 (여분/오결선)
        if missing or extra:
            all_ok = False
            print(f"\n  ▼ {net}: 스펙{len(s)} 실제{len(a)}")
            for des, num in sorted(missing):
                # 이 핀이 실제로 어느 net 에 붙었는지
                an = actual.get(des, {}).get(num, {}).get("net", "")
                tag = f"실제 net='{an}'" if an else "floating(net 없음)"
                print(f"      [누락] {des}.{num} → {tag}")
                total_missing += 1
                if an and an != net: total_wrong += 1
            for des, num in sorted(extra):
                nm = actual.get(des, {}).get(num, {}).get("name", "")
                print(f"      [여분] {des}.{num}({nm}) 가 {net} 에 붙음(스펙엔 없음)")
                total_extra += 1
    if all_ok:
        print("  ✅ 38넷 전부 멤버 일치")

    print("\n=== 4. GND 흡수 정밀검사 ===")
    gnd_actual = actual_net_members.get("GND", set())
    gnd_spec = spec_net_members.get("GND", set())
    absorbed = gnd_actual - gnd_spec
    if absorbed:
        print(f"  ❌ GND 에 스펙 외 핀 {len(absorbed)}개 흡수:")
        for des, num in sorted(absorbed):
            nm = actual.get(des, {}).get(num, {}).get("name", "")
            print(f"      {des}.{num}({nm})")
    else:
        print(f"  ✅ GND 멤버 {len(gnd_actual)}개 = 스펙과 일치(흡수 없음)")

    print("\n=== 5. 실제 net 중 스펙에 아예 없는 net ===")
    extra_nets = set(actual_net_members) - set(spec_nets)
    if extra_nets:
        for n in sorted(extra_nets):
            print(f"  '{n}': {sorted(actual_net_members[n])}")
    else:
        print("  없음")

    print("\n=== 6. 핀 단위 floating(스펙=연결, 실제=net없음) 요약 ===")
    floating = []
    for net, plist in spec_nets.items():
        for des, pinkey in plist:
            num = resolve(des, pinkey)
            if num is None: continue
            an = actual.get(des, {}).get(num, {}).get("net", "")
            if not an: floating.append((net, des, pinkey, num))
    if floating:
        for net, des, pk, num in floating:
            print(f"  {des}.{pk}(#{num}) 스펙 net {net} → 실제 floating")
    else:
        print("  없음")

    print("\n================ 종합 ================")
    print(f"스펙 해석실패 {len(unresolved)} / net멤버 누락 {total_missing} (그중 다른net흡수 {total_wrong}) / 여분 {total_extra} / GND흡수 {len(absorbed)} / floating {len(floating)}")
    verdict = "PASS ✅" if (not unresolved and all_ok and not absorbed) else "FAIL ❌"
    print("판정:", verdict)

if __name__ == "__main__":
    main()
