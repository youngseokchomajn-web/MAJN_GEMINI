#!/usr/bin/env python3
"""
MAJN Hardware Review Package Consistency & Logical DRC Verifier (v2.0)
======================================================================
SCOPE & LIMITATIONS NOTICE:
- This script performs strict AUTOMATED LOGICAL & ELECTRICAL NETLIST / BOM VERIFICATION.
- It verifies component counts, Espressif official GPIO-to-pad mappings, USB-C Type-C Rd compliance,
  I2S digital audio bus completeness, 0-ohm net isolation, and snubber serialization.
- It DOES NOT perform physical layout DRC (e.g. geometric copper clearance, annular rings, trace thermal limits).
  Physical layout DRC must be cross-verified via EasyEDA Pro internal DRC engine.
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
    print("=" * 78)
    print("MAJN HARDWARE REVIEW SUITE - LOGICAL & ELECTRICAL VERIFICATION (v2.0)")
    print("=" * 78)
    print("NOTICE: Checking Logical Netlist, BOM, Espressif Pad Map, and USB-C Specs.\n")
    
    passed = 0
    total = 0

    # 1. Check epro2 SHA distinctness
    total += 1
    orig_epro2 = os.path.join(HW_DIR, "PCB_0005_original", "Original.epro2")
    revc_epro2 = os.path.join(HW_DIR, "PCB_Rev_C", "Rev_C.epro2")
    orig_sha = get_sha256(orig_epro2)
    revc_sha = get_sha256(revc_epro2)
    print(f"[TEST 1] epro2 Binary SHA-256 Differentiation:")
    print(f"  - Original.epro2 SHA: {orig_sha[:16]}...")
    print(f"  - Rev_C.epro2    SHA: {revc_sha[:16]}...")
    if orig_sha != revc_sha:
        print("  => PASS: Rev-C project binary is distinct from Original baseline.")
        passed += 1
    else:
        print("  => FAIL: Rev-C project binary has IDENTICAL SHA with Original baseline!")

    # 2. Check PCB_0005 Original BOM vs Netlist
    total += 1
    orig_bom = parse_bom(os.path.join(HW_DIR, "PCB_0005_original", "BOM.csv"))
    orig_nets, orig_p2n, orig_comps = parse_netlist(os.path.join(HW_DIR, "PCB_0005_original", "Netlist.net"))
    print(f"\n[TEST 2] PCB #0005 Original Component Parity:")
    print(f"  - BOM component count: {len(orig_bom)} | Netlist: {len(orig_comps)}")
    if len(orig_bom) == 37 and len(orig_comps) == 37 and set(orig_bom.keys()) == orig_comps:
        print("  => PASS: 100% 1-to-1 match between Original BOM and Netlist (37 parts).")
        passed += 1
    else:
        print("  => FAIL: Component count or designator mismatch in PCB #0005.")

    # 3. Check PCB_Rev_C BOM vs Netlist
    total += 1
    revc_bom = parse_bom(os.path.join(HW_DIR, "PCB_Rev_C", "BOM.csv"))
    revc_nets, revc_p2n, revc_comps = parse_netlist(os.path.join(HW_DIR, "PCB_Rev_C", "Netlist.net"))
    print(f"\n[TEST 3] PCB Rev-C Component Parity:")
    print(f"  - BOM component count: {len(revc_bom)} | Netlist: {len(revc_comps)}")
    if len(revc_bom) == 55 and len(revc_comps) == 55 and set(revc_bom.keys()) == revc_comps:
        print("  => PASS: 100% 1-to-1 match between Rev-C BOM and Netlist (55 parts).")
        passed += 1
    else:
        diff = set(revc_bom.keys()).symmetric_difference(revc_comps)
        print(f"  => FAIL: Mismatch in Rev-C components: {diff}")

    # 4. Check ESP32 Official Physical Pad to GPIO Mapping
    total += 1
    print(f"\n[TEST 4] ESP32-WROOM-32E Official Physical Pad to Net Mapping Check:")
    expected_pads = {
        "U1.4": ("Pad 4 (SENSOR_VP / GPIO36, ADC1_CH0)", "NET_BCG_MCU_P"),
        "U1.5": ("Pad 5 (SENSOR_VN / GPIO39, ADC1_CH3)", "NET_BCG_MCU_N"),
        "U1.6": ("Pad 6 (VDET_1 / GPIO34, Input Only)", "SENSOR_INT1"),
        "U1.7": ("Pad 7 (VDET_2 / GPIO35, Input Only)", "NET_MIC_MCU_DIN"),
        "U1.10": ("Pad 10 (DAC_1 / GPIO25, I2S_WS)", "I2S_LRCLK"),
        "U1.11": ("Pad 11 (DAC_2 / GPIO26, I2S_BCLK)", "I2S_BCLK"),
        "U1.12": ("Pad 12 (IO27 / GPIO27, I2C_SCL)", "AMP_I2C_SCL"),
        "U1.27": ("Pad 27 (IO16 / GPIO16, UART2_RX)", "NET_RADAR_MCU_RX"),
        "U1.28": ("Pad 28 (IO17 / GPIO17, UART2_TX)", "NET_RADAR_MCU_TX"),
        "U1.33": ("Pad 33 (IO21 / GPIO21, I2C_SDA)", "AMP_I2C_SDA"),
    }
    pads_ok = True
    for pad_id, (desc, exp_net) in expected_pads.items():
        actual_net = revc_p2n.get(pad_id)
        if actual_net == exp_net:
            print(f"  - {pad_id} [{desc}]: '{actual_net}' [MATCH]")
        else:
            print(f"  => FAIL: {pad_id} [{desc}]: Expected '{exp_net}', got '{actual_net}'")
            pads_ok = False
            
    # Check Strapping Pin GPIO12 (Pad 14) is NOT connected
    pad14_net = revc_p2n.get("U1.14")
    if not pad14_net:
        print(f"  - U1.14 [Pad 14 (MTDI / GPIO12, Boot Strap)]: UNCONNECTED / NC [SAFE]")
    else:
        print(f"  => FAIL: U1.14 (Boot Strap GPIO12) connected to '{pad14_net}'! Risk of boot failure.")
        pads_ok = False
        
    if pads_ok:
        print("  => PASS: All ESP32 physical pads strictly adhere to Espressif datasheet specs.")
        passed += 1
    else:
        print("  => FAIL: ESP32 pad-to-net mapping discrepancies detected!")

    # 5. Check USB-C Type-C Standard Rd & CC Mapping
    total += 1
    print(f"\n[TEST 5] USB Type-C Standard Compliance Check (CC1/CC2 & 5.1k Rd):")
    r3_val = revc_bom.get("R3", {}).get("Comment/Value", "")
    r4_val = revc_bom.get("R4", {}).get("Comment/Value", "")
    cc1_net = revc_p2n.get("USB_C.A5")
    cc2_net = revc_p2n.get("USB_C.B5")
    sbu2_net = revc_p2n.get("USB_C.B8")
    
    usbc_ok = True
    print(f"  - R3 Value (CC1 Rd): '{r3_val}' (Expected: 5.1kΩ)")
    print(f"  - R4 Value (CC2 Rd): '{r4_val}' (Expected: 5.1kΩ)")
    print(f"  - USB_C.A5 (CC1 Pad): '{cc1_net}'")
    print(f"  - USB_C.B5 (CC2 Pad): '{cc2_net}'")
    print(f"  - USB_C.B8 (SBU2 Pad): '{sbu2_net}' (Expected: None/NC)")
    
    if "5.1k" in r3_val and "5.1k" in r4_val and cc1_net == "USB_CC1" and cc2_net == "USB_CC2" and not sbu2_net:
        print("  => PASS: USB-C CC1/CC2 correctly routed with standard 5.1kΩ Rd pull-downs (B5 corrected).")
        passed += 1
    else:
        print("  => FAIL: USB-C non-standard CC configuration or pin mapping error!")

    # 6. Check INMP441 Digital Microphone Interface Completeness
    total += 1
    print(f"\n[TEST 6] INMP441 Digital I2S Microphone Signal Completeness Check:")
    j_env_pins = {
        "J_ENV_MIC.1": revc_p2n.get("J_ENV_MIC.1"), # 3.3V
        "J_ENV_MIC.2": revc_p2n.get("J_ENV_MIC.2"), # GND
        "J_ENV_MIC.3": revc_p2n.get("J_ENV_MIC.3"), # SDA
        "J_ENV_MIC.4": revc_p2n.get("J_ENV_MIC.4"), # SCL
        "J_ENV_MIC.5": revc_p2n.get("J_ENV_MIC.5"), # BCLK
        "J_ENV_MIC.6": revc_p2n.get("J_ENV_MIC.6"), # WS
        "J_ENV_MIC.7": revc_p2n.get("J_ENV_MIC.7"), # DIN
    }
    mic_ok = True
    print(f"  - Pin 5 (I2S_BCLK): {j_env_pins['J_ENV_MIC.5']}")
    print(f"  - Pin 6 (I2S_WS)  : {j_env_pins['J_ENV_MIC.6']}")
    print(f"  - Pin 7 (MIC_DIN) : {j_env_pins['J_ENV_MIC.7']}")
    if (j_env_pins["J_ENV_MIC.5"] == "I2S_BCLK" and
        j_env_pins["J_ENV_MIC.6"] == "NET_MIC_CONN_WS" and
        j_env_pins["J_ENV_MIC.7"] == "NET_MIC_CONN_DIN"):
        print("  => PASS: All 3 mandatory I2S signals (BCLK, WS, DIN) fully present on J_ENV_MIC.")
        passed += 1
    else:
        print("  => FAIL: Incomplete I2S microphone interface on J_ENV_MIC!")

    # 7. Check 0-Ohm Links isolation in Rev-C (R_L1 ~ R_L8)
    total += 1
    print(f"\n[TEST 7] 0-Ohm Links Electrical Isolation Check (R_L1 ~ R_L8):")
    links_ok = True
    for i in range(1, 9):
        des = f"R_L{i}"
        net1 = revc_p2n.get(f"{des}.1")
        net2 = revc_p2n.get(f"{des}.2")
        if not net1 or not net2 or net1 == net2:
            print(f"  => FAIL: {des} pin 1 ({net1}) and pin 2 ({net2}) error")
            links_ok = False
        else:
            print(f"  - {des}: '{net1}' <-> '{net2}' [ISOLATED OK]")
    if links_ok:
        print("  => PASS: All 8 0-Ohm isolation links provide independent net bridging.")
        passed += 1
    else:
        print("  => FAIL: 0-Ohm link isolation failure!")

    # 8. Check RC Snubber serialization in Rev-C
    total += 1
    print(f"\n[TEST 8] MP3426 SW RC Snubber Serialization Check:")
    c_p1_net = revc_p2n.get("C_SNUB.1")
    c_p2_net = revc_p2n.get("C_SNUB.2")
    r_p1_net = revc_p2n.get("R_SNUB.1")
    r_p2_net = revc_p2n.get("R_SNUB.2")
    if c_p1_net == "BOOST_SW" and c_p2_net == "NET_SNUB_MID" and r_p1_net == "NET_SNUB_MID" and r_p2_net == "GND":
        print(f"  - BOOST_SW -> C_SNUB ({c_p1_net}..{c_p2_net}) -> R_SNUB ({r_p1_net}..{r_p2_net}) -> GND")
        print("  => PASS: Snubber correctly wired in series: BOOST_SW -> C_SNUB -> R_SNUB -> GND.")
        passed += 1
    else:
        print("  => FAIL: Snubber wiring error or short circuit detected!")

    # 9. Check PPTC Fuse F1 insertion
    total += 1
    print(f"\n[TEST 9] PPTC Fuse F1 USB Protection Check:")
    f1_p1_net = revc_p2n.get("F1.1")
    f1_p2_net = revc_p2n.get("F1.2")
    if f1_p1_net == "NET_VBUS_RAW" and f1_p2_net == "VBUS_5V":
        print("  => PASS: PPTC Fuse F1 safely isolates USB raw power from internal 5V rail.")
        passed += 1
    else:
        print("  => FAIL: F1 wiring error!")

    # 10. Check Power Rails & GND Short-circuit check
    total += 1
    print(f"\n[TEST 10] Global Power Rail Short-Circuit Check:")
    gnd_pins = set(revc_nets.get("GND", []))
    vbus_pins = set(revc_nets.get("VBUS_5V", []))
    vcc_pins = set(revc_nets.get("VCC_3V3", []))
    pvdd_pins = set(revc_nets.get("PVDD_12V", []))
    shorts = []
    if gnd_pins & vbus_pins: shorts.append("GND <-> VBUS_5V")
    if gnd_pins & vcc_pins: shorts.append("GND <-> VCC_3V3")
    if gnd_pins & pvdd_pins: shorts.append("GND <-> PVDD_12V")
    if vbus_pins & vcc_pins: shorts.append("VBUS_5V <-> VCC_3V3")
    if not shorts:
        print("  => PASS: Zero electrical shorts between Power Rails and Ground.")
        passed += 1
    else:
        print(f"  => FAIL: Detected power rail shorts: {shorts}")

    print("\n" + "=" * 78)
    print(f"VERIFICATION SUMMARY: {passed} / {total} LOGICAL RULES PASSED ({passed/total*100:.1f}%)")
    print("=" * 78)
    
    return passed == total

if __name__ == "__main__":
    success = run_verification()
    sys.exit(0 if success else 1)
