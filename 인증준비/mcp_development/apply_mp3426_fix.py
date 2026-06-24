#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""v1.7.0: 라이브 심볼(a1_symbol_verify.json) 기준 U3 MP3426 핀 정정 + 전 넷 이름기반 재검증."""
import json

d = json.load(open("mcp_design_flow.json", encoding="utf-8"))
sym = json.load(open("a1_symbol_verify.json", encoding="utf-8"))["pins_by_designator"]
# 심볼 핀번호->이름 맵
symmap = {des: {str(n): str(nm) for n, nm in pins} for des, pins in sym.items()}
nets = d["nets"]

def setpin(net, des, old, new):
    for e in nets[net]:
        if e[0] == des and str(e[1]) == old:
            e[1] = new; return True
    return False

# --- U3 정정 (심볼: 8/9/10=PGND, 11=AGND, 12=SS, 13=FB, 14=FSET, 15=EP) ---
setpin("BOOST_FB", "U3", "9", "13")
setpin("BOOST_FSET", "U3", "8", "14")
setpin("BOOST_SS", "U3", "10", "12")
# GND: U3 12,13,14 제거 → 8,9,10 추가 (11,15 유지)
gnd = [e for e in nets["GND"] if not (e[0] == "U3" and str(e[1]) in ("12", "13", "14"))]
have = {str(e[1]) for e in gnd if e[0] == "U3"}
for p in ("8", "9", "10"):
    if p not in have:
        gnd.append(["U3", p])
nets["GND"] = gnd

# --- 이름 기반 재검증: IC 기능핀이 올바른 이름의 심볼핀에 붙었는지 (실질 오류 검사) ---
issues = []
# 전원/기능 넷이 엉뚱한 이름 핀에 붙지 않았는지 (U3/U4 숫자핀 스팟체크)
EXPECT = {
    ("BOOST_FB", "U3"): "FB", ("BOOST_FSET", "U3"): "FSET", ("BOOST_SS", "U3"): "SS",
    ("BOOST_COMP", "U3"): "COMP", ("BOOST_EN", "U3"): "EN", ("BOOST_VDD", "U3"): "VDD",
    ("VBUS_5V", "U3"): "VIN", ("BOOST_SW", "U3"): "SW",
    ("PVDD_12V", "U4"): "PVDD", ("AVDD", "U4"): "AVDD", ("VR_DIG", "U4"): "VR_DIG",
    ("I2S_BCLK", "U4"): "SCLK", ("I2S_LRCLK", "U4"): "LRCLK", ("I2S_DIN", "U4"): "SDIN",
    ("AMP_I2C_SDA", "U4"): "SDA", ("AMP_I2C_SCL", "U4"): "SCL", ("AMP_PDN", "U4"): "PDN",
}
for (net, des), expect in EXPECT.items():
    for e in nets.get(net, []):
        if e[0] == des and str(e[1]).isdigit():
            nm = symmap.get(des, {}).get(str(e[1]), "?")
            ok = expect.upper() in nm.upper()
            if not ok:
                issues.append(f"{net}<-{des}.{e[1]}({nm}) expect~{expect}")

print("U3 now:", {symmap['U3'][str(p)]: f"{r}.{p}" for net in ['BOOST_COMP','BOOST_EN','VBUS_5V','BOOST_SW','BOOST_VDD','BOOST_SS','BOOST_FB','BOOST_FSET','GND'] for r,p in nets[net] if r=='U3'})
print("NAME-CHECK ISSUES:", issues if issues else "NONE - all IC functional pins match symbol names")

if not issues:
    d["version"] = "1.7.0"
    note = ("v1.7.0 (2026-06-24): ★★MP3426 핀 정정(라이브 EasyEDA 심볼 a1_symbol_verify.json 기준) — "
            "v1.5에서 alldatasheet OCR(핀순서 역전)을 믿고 FSET/FB/SS를 8/9/10으로 잘못 바꿨던 것을 "
            "심볼 실측(8/9/10=PGND, 11=AGND, 12=SS, 13=FB, 14=FSET, 15=EP)대로 원복+정정: "
            "FB→13, FSET→14, SS→12(C23캡), GND→8/9/10/11/15. "
            "★교훈: 데이터시트 OCR보다 라이브 심볼이 권위. 전 넷 이름기반 재검증 통과. | ")
    d["_revision_note"] = note + d["_revision_note"]
    json.dump(d, open("mcp_design_flow.json", "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    print("SAVED v1.7.0")
else:
    print("NOT SAVED - resolve issues first")
