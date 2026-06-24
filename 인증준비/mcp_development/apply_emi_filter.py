#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""v1.6.0: C20 VR_DIG→1µF + AMP_OUT 출력 EMI 필터(페라이트비드+캡) 추가."""
import json, io

P = "mcp_design_flow.json"
d = json.load(open(P, encoding="utf-8"))

# --- 1) C20 VR_DIG 100nF -> 1uF (TAS5805M Table8-3 C9/C10=1uF) ---
for c in d["components"]:
    if c["designator"] == "C20":
        c["name"] = "Amp VR_DIG Cap 1uF 25V"
        c["lcsc_id"] = "C106858"
        c["_note"] = "v1.6: 100nF->1uF (TAS5805M VR_DIG=내부1.5V LDO 출력, Table8-3 C9/C10=1uF)"

# --- 2) AMP_OUT EMI 출력필터: 레그별 페라이트비드(직렬) + 2.2nF→GND ---
# 레그: (출력넷, U4핀, 부트스트랩캡, 비드desig, 캡desig, SPK넷, 커넥터, 커넥터핀)
BEAD_LCSC = "C154119"   # Sunlord UPZ2012E221-3R0TF 220R@100MHz 3A 0805
CAP_LCSC  = "C16033"    # Samsung CL10B222KB8NNNC 2.2nF 50V X7R 0603
legs = [
    ("AMP_OUT_A+", "FB1", "C24", "SPK_A+", "J1", "1", 68.0, 18.0, 70.0, 19.0),
    ("AMP_OUT_A-", "FB2", "C25", "SPK_A-", "J1", "2", 68.0, 16.0, 70.0, 16.0),
    ("AMP_OUT_B+", "FB3", "C26", "SPK_B+", "J2", "1", 68.0, 14.0, 70.0, 14.0),
    ("AMP_OUT_B-", "FB4", "C27", "SPK_B-", "J2", "2", 68.0, 12.0, 70.0, 11.0),
]

comps = d["components"]
nets = d["nets"]
for outnet, bead, cap, spknet, conn, cpin, bx, by, cx, cy in legs:
    # 부품 추가: 페라이트비드(0805), 출력캡(0603)
    comps.append({"designator": bead, "name": "AMP Out Ferrite Bead 220R@100MHz 3A",
                  "lcsc_id": BEAD_LCSC, "package": "0805", "x": bx, "y": by, "angle": 90,
                  "_note": "v1.6: TAS5805M 출력 EMI 필터(filterless+2m케이블). TI UPZ2012E 권장"})
    comps.append({"designator": cap, "name": "AMP Out Filter Cap 2.2nF 50V",
                  "lcsc_id": CAP_LCSC, "package": "0603", "x": cx, "y": cy, "angle": 0,
                  "_note": "v1.6: 출력 EMI 필터 캡(TI Table8-3 2200pF)→GND"})
    # 출력넷: 커넥터를 떼고 비드 입력(pin1) 연결 (부트스트랩 캡은 U4쪽 유지)
    npl = []
    moved = False
    for ref, pin in nets[outnet]:
        if ref == conn and pin == cpin:
            moved = True
            continue  # 커넥터는 SPK넷으로 이동
        npl.append([ref, pin])
    npl.append([bead, "1"])      # 비드 입력 = U4 출력측
    assert moved, f"{conn}.{cpin} not found in {outnet}"
    nets[outnet] = npl
    # SPK넷(필터 후): 비드 출력 + 커넥터 + 캡
    nets[spknet] = [[bead, "2"], [conn, cpin], [cap, "1"]]
    # GND에 캡 추가
    nets["GND"].append([cap, "2"])

# --- version/note ---
d["version"] = "1.6.0"
note16 = ("v1.6.0 (2026-06-24): ★AMP_OUT 출력 EMI 필터 추가(TAS5805M filterless+2m케이블, KC EMC) — "
          "레그4개에 페라이트비드 FB1~4(C154119 Sunlord UPZ2012E221-3R0TF 220R@100MHz 3A 0805) "
          "직렬 + 캡 C24~27(C16033 2.2nF 50V, TI Table8-3 2200pF)→GND, SPK_A+/A-/B+/B- 넷 신설. "
          "부트스트랩캡(C12~15)은 U4쪽 유지. + C20 VR_DIG 100nF→1µF(C106858). "
          "★펌웨어: 비드필터 사용 시 Fsw=384kHz+Spread Spectrum 설정(TI 권고). | ")
d["_revision_note"] = note16 + d["_revision_note"]

json.dump(d, open(P, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
print("OK v1.6.0 | components", len(comps), "| nets", len(nets))
