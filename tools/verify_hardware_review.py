#!/usr/bin/env python3
"""
MAJN Hardware Review Package Consistency & DRC Verifier
Verifies SSOT integrity between EasyEDA epro2 binaries, BOMs, and Netlists.
"""

import os
import sys
import hashlib
import csv

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HW_DIR = os.path.join(BASE_DIR, "hardware_review")

def get_sha256(filepath):
    h = hashlib.sha256()
    with open(filepath, 'rb') as f:
        while chunk := f.read(8192):
            h.update(chunk)
    return h.hexdigest()

def parse_netlist(filepath):
    nets = {} # net_name -> list of pin_str (e.g. 'R1.1')
    pin_to_net = {} # pin_str -> net_name
    comps = set()
    with open(filepath, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            if line.startswith('NET '):
                parts = line.split()
                net_name = parts[1].strip('"')
                pins = parts[2:]
                nets[net_name] = pins
                for p in pins:
                    pin_to_net[p] = net_name
                    cname = p.split('.')[0]
                    comps.add(cname)
    return nets, pin_to_net, comps

def parse_bom(filepath):
    comps = {}
    with open(filepath, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for r in reader:
            des = r.get('Designator', '').strip()
            if des:
                comps[des] = r
    return comps

def run_verification():
    print("=" * 70)
    print("MAJN HARDWARE REVIEW SUITE - GROUND TRUTH VERIFICATION")
    print("=" * 70)
    
    passed = 0
    total = 0

    # 1. Check epro2 SHA distinctness
    total += 1
    orig_epro2 = os.path.join(HW_DIR, "PCB_0005_original", "Original.epro2")
    revc_epro2 = os.path.join(HW_DIR, "PCB_Rev_C", "Rev_C.epro2")
    
    orig_sha = get_sha256(orig_epro2)
    revc_sha = get_sha256(revc_epro2)
    print(f"[TEST 1] epro2 SHA-256 Differentiation Check:")
    print(f"  - Original.epro2 SHA: {orig_sha[:16]}...")
    print(f"  - Rev_C.epro2    SHA: {revc_sha[:16]}...")
    if orig_sha != revc_sha:
        print("  => PASS: Rev-C project binary is distinct from Original baseline.")
        passed += 1
    else:
        print("  => FAIL: Rev-C project binary has IDENTICAL SHA with Original baseline!")

    # 2. Check PCB_0005 Original BOM vs Netlist
    total += 1
    orig_bom_path = os.path.join(HW_DIR, "PCB_0005_original", "BOM.csv")
    orig_net_path = os.path.join(HW_DIR, "PCB_0005_original", "Netlist.net")
    orig_bom = parse_bom(orig_bom_path)
    orig_nets, orig_p2n, orig_comps = parse_netlist(orig_net_path)
    print(f"\n[TEST 2] PCB #0005 Original Component Parity:")
    print(f"  - BOM component count: {len(orig_bom)}")
    print(f"  - Netlist component count: {len(orig_comps)}")
    if len(orig_bom) == 37 and len(orig_comps) == 37 and set(orig_bom.keys()) == orig_comps:
        print("  => PASS: 100% 1-to-1 match between Original BOM and Netlist (37 parts).")
        passed += 1
    else:
        diff = set(orig_bom.keys()).symmetric_difference(orig_comps)
        print(f"  => FAIL: Mismatch in Original components: {diff}")

    # 3. Check PCB_Rev_C BOM vs Netlist
    total += 1
    revc_bom_path = os.path.join(HW_DIR, "PCB_Rev_C", "BOM.csv")
    revc_net_path = os.path.join(HW_DIR, "PCB_Rev_C", "Netlist.net")
    revc_bom = parse_bom(revc_bom_path)
    revc_nets, revc_p2n, revc_comps = parse_netlist(revc_net_path)
    print(f"\n[TEST 3] PCB Rev-C Component Parity:")
    print(f"  - BOM component count: {len(revc_bom)}")
    print(f"  - Netlist component count: {len(revc_comps)}")
    if len(revc_bom) == 54 and len(revc_comps) == 54 and set(revc_bom.keys()) == revc_comps:
        print("  => PASS: 100% 1-to-1 match between Rev-C BOM and Netlist (54 parts).")
        passed += 1
    else:
        diff = set(revc_bom.keys()).symmetric_difference(revc_comps)
        print(f"  => FAIL: Mismatch in Rev-C components: {diff}")

    # 4. Check 0-Ohm Links isolation in Rev-C
    total += 1
    print(f"\n[TEST 4] 0-Ohm Links Electrical Isolation Check (R_L1 ~ R_L7):")
    links_ok = True
    for i in range(1, 8):
        des = f"R_L{i}"
        net1 = revc_p2n.get(f"{des}.1")
        net2 = revc_p2n.get(f"{des}.2")
        if not net1 or not net2:
            print(f"  => FAIL: {des} has unmapped pin ({net1}, {net2})")
            links_ok = False
        elif net1 == net2:
            print(f"  => FAIL: {des} pin 1 and pin 2 are SHORTED to same net: '{net1}'")
            links_ok = False
        else:
            print(f"  - {des}: Pin 1 ('{net1}') <-> Pin 2 ('{net2}') [ISOLATED OK]")
    if links_ok:
        print("  => PASS: All 0-Ohm isolation links provide independent net bridging.")
        passed += 1

    # 5. Check RC Snubber serialization in Rev-C
    total += 1
    print(f"\n[TEST 5] MP3426 SW RC Snubber Serialization Check:")
    c_p1_net = revc_p2n.get("C_SNUB.1")
    c_p2_net = revc_p2n.get("C_SNUB.2")
    r_p1_net = revc_p2n.get("R_SNUB.1")
    r_p2_net = revc_p2n.get("R_SNUB.2")
    print(f"  - C_SNUB.1: {c_p1_net}")
    print(f"  - C_SNUB.2: {c_p2_net}")
    print(f"  - R_SNUB.1: {r_p1_net}")
    print(f"  - R_SNUB.2: {r_p2_net}")
    if c_p1_net == "BOOST_SW" and c_p2_net == "NET_SNUB_MID" and r_p1_net == "NET_SNUB_MID" and r_p2_net == "GND":
        print("  => PASS: Snubber correctly wired in series: BOOST_SW -> C_SNUB -> NET_SNUB_MID -> R_SNUB -> GND")
        passed += 1
    else:
        print("  => FAIL: Snubber wiring error or short circuit detected!")

    # 6. Check PPTC Fuse F1 insertion
    total += 1
    print(f"\n[TEST 6] PPTC Fuse F1 USB Protection Check:")
    f1_p1_net = revc_p2n.get("F1.1")
    f1_p2_net = revc_p2n.get("F1.2")
    print(f"  - F1.1 (USB-C In): {f1_p1_net}")
    print(f"  - F1.2 (Protected VBUS_5V): {f1_p2_net}")
    if f1_p1_net == "NET_VBUS_RAW" and f1_p2_net == "VBUS_5V":
        print("  => PASS: PPTC Fuse F1 safely isolates USB raw power from internal 5V rail.")
        passed += 1
    else:
        print("  => FAIL: F1 wiring error!")

    # 7. Check Power Rails & GND Short-circuit check
    total += 1
    print(f"\n[TEST 7] Global Short-Circuit Prevention Check:")
    gnd_pins = set(revc_nets.get("GND", []))
    vbus_pins = set(revc_nets.get("VBUS_5V", []))
    vcc_pins = set(revc_nets.get("VCC_3V3", []))
    pvdd_pins = set(revc_nets.get("PVDD_12V", []))
    
    shorts = []
    if gnd_pins & vbus_pins: shorts.append("GND <-> VBUS_5V")
    if gnd_pins & vcc_pins: shorts.append("GND <-> VCC_3V3")
    if gnd_pins & pvdd_pins: shorts.append("GND <-> PVDD_12V")
    if vbus_pins & vcc_pins: shorts.append("VBUS_5V <-> VCC_3V3")
    if vbus_pins & pvdd_pins: shorts.append("VBUS_5V <-> PVDD_12V")
    
    if not shorts:
        print("  => PASS: Zero electrical shorts between Power Rails and Ground.")
        passed += 1
    else:
        print(f"  => FAIL: Detected power rail shorts: {shorts}")

    print("\n" + "=" * 70)
    print(f"VERIFICATION SUMMARY: {passed} / {total} TESTS PASSED ({passed/total*100:.1f}%)")
    print("=" * 70)
    
    return passed == total

if __name__ == "__main__":
    success = run_verification()
    sys.exit(0 if success else 1)
