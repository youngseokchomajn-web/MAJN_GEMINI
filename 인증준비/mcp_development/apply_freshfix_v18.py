#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""v1.8.0 fresh-eye 수정: U5 보조핀 GND종단 + USB-C 쉴드 GND + C17 EN캡 1uF."""
import json
d = json.load(open("mcp_design_flow.json", encoding="utf-8"))
nets = d["nets"]

def add_gnd(des, pin):
    if [des, pin] not in nets["GND"]:
        nets["GND"].append([des, pin])

# 1) U5(LSM6DSOX) 미사용 보조핀 → GND (ST 데이터시트 종단요구: SDX/SCX/OCS_AUX/SDO_AUX)
for p in ["2", "3", "10", "11"]:
    add_gnd("U5", p)
# 2) USB-C 쉴드/마운팅(EH, 패드 1~4) → GND (ESD/EMC)
for p in ["1", "2", "3", "4"]:
    add_gnd("USB_C", p)
# 3) C17 ESP32 EN RC 캡 100nF → 1uF (Espressif POR 기준)
for c in d["components"]:
    if c["designator"] == "C17":
        c["name"] = "ESP EN RC Cap 1uF"
        c["lcsc_id"] = "C106858"
        c["_note"] = "v1.8: 100nF->1uF (Espressif EN POR RC 10k+1uF 기준, 부팅안정)"

d["version"] = "1.8.0"
note = ("v1.8.0 (2026-06-24): ★fresh-eye Phase B 점검 반영 — "
        "①U5(LSM6DSOX) 미사용 보조핀 SDX(2)/SCX(3)/OCS_AUX(10)/SDO_AUX(11)→GND "
        "(ST 데이터시트 종단요구, 부유=노이즈) ②USB-C 쉴드/마운팅 EH(1~4)→GND(ESD/EMC) "
        "③C17 EN캡 100nF→1uF(C106858, Espressif POR). 검증: TAS5805M주소 FW0x2C=HW일치, "
        "전 서브시스템 연결 정확(라이브 심볼 기준). | ")
d["_revision_note"] = note + d["_revision_note"]
json.dump(d, open("mcp_design_flow.json", "w", encoding="utf-8"), ensure_ascii=False, indent=2)

# validate
from collections import defaultdict
pins = defaultdict(set); single = []
for nn, pl in d["nets"].items():
    if len(pl) < 2: single.append(nn)
    for r, p in pl: pins[r].add(str(p))
orph = [c["designator"] for c in d["components"] if c["designator"] not in pins]
print("v", d["version"], "| comps", len(d["components"]), "| nets", len(d["nets"]))
print("U5 in GND:", sorted([p for r, p in nets["GND"] if r == "U5"]))
print("USB_C in GND:", sorted([p for r, p in nets["GND"] if r == "USB_C"]))
print("C17:", [c["lcsc_id"] for c in d["components"] if c["designator"] == "C17"])
print("singletons:", single, "| orphans:", orph)
