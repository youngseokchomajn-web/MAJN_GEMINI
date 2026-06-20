#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
verify_sch_netlist.py — EasyEDA 회로도 실제 넷리스트와 mcp_design_flow.json 스펙 1:1 대조기
"""

import sys
import json
import os
from easyeda_mcp_client import EasyEDAMCPClient

def normalize_pin(pin_name):
    if not pin_name:
        return ""
    return str(pin_name).strip().lower()

def main():
    print("=========================================================")
    print("    EasyEDA 회로도 넷리스트 ↔ 스펙(JSON) 1:1 교차 검증    ")
    print("=========================================================\n")

    # 1. 스펙 데이터 로드
    flow_file = "mcp_design_flow.json"
    if not os.path.exists(flow_file):
        print(f"[ERROR] '{flow_file}' 파일을 찾을 수 없습니다.")
        sys.exit(1)
        
    with open(flow_file, "r", encoding="utf-8") as f:
        flow = json.load(f)
        
    spec_nets = flow["nets"]
    
    # 스펙 핀맵 매핑 구축: { designator: { pin_number: net_name } }
    spec_map = {}
    for net_name, pins in spec_nets.items():
        for des, pin_num in pins:
            des_key = des.strip()
            pin_key = normalize_pin(pin_num)
            if des_key not in spec_map:
                spec_map[des_key] = {}
            spec_map[des_key][pin_key] = net_name
            
    print(f"[SPEC] {len(spec_nets)}개 넷 정보 로드 완료.")

    # 2. 브릿지 클라이언트 초기화 및 연결
    client = EasyEDAMCPClient()
    if not client.connect():
        print("[ERROR] 브릿지 서버 및 에디터 연결 실패")
        sys.exit(1)
        
    js_extract = """
    try {
        const pages = await eda.dmt_Schematic.getAllSchematicPagesInfo();
        if (pages && pages.length > 0) {
            await eda.dmt_EditorControl.openDocument(pages[0].uuid);
            await new Promise(r => setTimeout(r, 1500));
            await eda.dmt_EditorControl.activateDocument(pages[0].uuid);
            await new Promise(r => setTimeout(r, 1500));
        } else {
            return { success: false, error: "회로도 페이지를 찾을 수 없습니다." };
        }
        
        // 저장을 먼저 실행하여 데이터 및 컴파일 캐시 강제 갱신
        await eda.sch_Document.save();
        await new Promise(r => setTimeout(r, 2000));
        
        const file = await eda.sch_ManufactureData.getNetlistFile("sch_net", "JLCEDA");
        if (!file) {
            return { success: false, error: "넷리스트 파일 생성 실패 (null)" };
        }
        
        const content = await file.text();
        return { success: true, content: content };
    } catch(e) {
        return { success: false, error: e.message };
    }
    """
    
    print("EasyEDA 에디터로부터 넷리스트 추출 중...")
    res = client.execute_js(js_extract)
    if not res or not res.get("success"):
        err = res.get("error") if res else "응답 없음"
        print(f"[ERROR] 넷리스트 추출 실패: {err}")
        sys.exit(1)
        
    netlist_str = res.get("content")
    try:
        netlist_data = json.loads(netlist_str)
    except Exception as e:
        print(f"[ERROR] 넷리스트 JSON 파싱 실패: {e}")
        sys.exit(1)
        
    # 4. 실제 회로도 핀맵 매핑 구축: { designator: [ { number, name, net } ] }
    actual_map = {}
    components = netlist_data.get("components", {})
    
    for unique_id, comp_info in components.items():
        props = comp_info.get("props", {})
        des = props.get("Designator")
        if not des:
            continue
            
        des_key = des.strip()
        pin_info = comp_info.get("pinInfoMap", {})
        
        for pin_id, pin_data in pin_info.items():
            p_num = normalize_pin(pin_data.get("number"))
            p_name = normalize_pin(pin_data.get("name"))
            net_name = pin_data.get("net", "").strip()
            
            if not p_num and not p_name:
                continue
                
            if des_key not in actual_map:
                actual_map[des_key] = []
            actual_map[des_key].append({
                "number": p_num,
                "name": p_name,
                "net": net_name
            })

    # 핀 검색 헬퍼 함수
    def find_actual_pin_net(actual_pins, spec_pin_key):
        norm_spec = normalize_pin(spec_pin_key)
        
        # 1. 핀 번호 일치 또는 핀 이름 일치 검색
        for p in actual_pins:
            if p["number"] == norm_spec or p["name"] == norm_spec:
                return p["net"], p["number"], p["name"]
                
        # 2. GPIO/IO 알리아스 정규화 검색 (예: gpio15 -> 15 또는 15 -> gpio15)
        def get_gpio_num(s):
            n = s.replace("gpio", "").replace("io", "")
            return n if n.isdigit() else None
            
        spec_gpio = get_gpio_num(norm_spec)
        if spec_gpio:
            for p in actual_pins:
                p_name_g = get_gpio_num(p["name"])
                if p_name_g and p_name_g == spec_gpio:
                    return p["net"], p["number"], p["name"]
                    
        # 3. USB_C 전원 핀들의 복합 표현 검색 (예: a4b9 -> VBUS 등)
        # 스펙의 VBUS가 실제 a4b9 또는 b4a9 중 일부를 포함하는지
        for p in actual_pins:
            if (norm_spec in p["number"] or p["number"] in norm_spec) and len(p["number"]) > 1:
                return p["net"], p["number"], p["name"]
            if (norm_spec in p["name"] or p["name"] in norm_spec) and len(p["name"]) > 1:
                return p["net"], p["number"], p["name"]
                
        return None, None, None

    # 5. 1:1 교차 검증 수행
    errors = []
    warnings = []
    
    # 5A. 스펙 대비 실제 연결 확인 (누락/오매칭)
    for des, pin_nets in spec_map.items():
        if des not in actual_map:
            errors.append(f"부품 누락: 스펙의 부품 '{des}'이 회로도 넷리스트에 존재하지 않습니다.")
            continue
            
        actual_pins = actual_map[des]
        for spec_pin_key, spec_net in pin_nets.items():
            actual_net, act_num, act_name = find_actual_pin_net(actual_pins, spec_pin_key)
            
            # 스펙에는 연결이 존재하지만 실제 넷리스트에 넷 이름이 비어있거나 다를 경우
            if not actual_net:
                errors.append(f"연결 누락: {des} 핀 '{spec_pin_key}' -> 스펙 net '{spec_net}' / 실제 net 없음 (Floating)")
            elif actual_net != spec_net:
                errors.append(f"넷 불일치(쇼트/오결선): {des} 핀 '{spec_pin_key}' (실제 {act_num}/{act_name}) -> 스펙 net '{spec_net}' <-> 실제 net '{actual_net}'")
                
    # 5B. 실제 회로도 넷리스트 대비 스펙 확인 (과결선/오결선)
    # 스펙에 정의되지 않은 여분의 핀 연결이 있는지 확인 (GND 흡수 등 감지)
    for des, actual_pins in actual_map.items():
        spec_pins = spec_map.get(des, {})
        for p in actual_pins:
            actual_net = p["net"]
            if not actual_net:
                continue # 실제 연결이 없는 경우는 No-Connect로 패스
                
            # 실제 핀(number 또는 name)이 스펙 상에 어떤 넷으로 기재되어 있는지 확인
            spec_net_by_num = spec_pins.get(p["number"])
            spec_net_by_name = spec_pins.get(p["name"])
            
            # GPIO 정규화 확인
            def get_gpio_num(s):
                n = s.replace("gpio", "").replace("io", "")
                return n if n.isdigit() else None
            
            spec_net_by_gpio = None
            p_name_g = get_gpio_num(p["name"])
            for sk, sn in spec_pins.items():
                sk_g = get_gpio_num(sk)
                if sk_g and sk_g == p_name_g:
                    spec_net_by_gpio = sn
                    break
                    
            spec_net = spec_net_by_num or spec_net_by_name or spec_net_by_gpio
            
            # USB_C 전원 핀들의 복합 표현 검색 대안
            if not spec_net and des == "USB_C":
                if "vbus" in p["number"] or "vbus" in p["name"]:
                    spec_net = spec_pins.get("vbus")
                elif "gnd" in p["number"] or "gnd" in p["name"]:
                    spec_net = spec_pins.get("gnd")
            
            if not spec_net:
                # 스펙 상에는 연결이 없어야 하는데(No-Connect), 실제 넷이 할당된 경우
                # (예: GND 단락이나 다른 신호선 겹침에 의해 GND로 흡수된 경우)
                errors.append(f"비정상 연결: {des} 핀 '{p['number']}/{p['name']}' -> 스펙 상 연결 없음 <-> 실제 net '{actual_net}' (쇼트 위험!)")

    # 6. 결과 리포팅
    print("\n==================== 검증 결과 리포트 ====================")
    if errors:
        print(f"[FAIL] 총 {len(errors)}건의 전기적 불일치가 발견되었습니다:\n")
        for idx, err in enumerate(errors, 1):
            print(f"  {idx:2d}. {err}")
        print("\n=========================================================")
        sys.exit(1)
    else:
        print("[PASS] 회로도 실제 넷리스트가 스펙(mcp_design_flow.json)과 100% 일치합니다!")
        print(f"       매칭된 부품 수: {len(actual_map)}개")
        print("=========================================================\n")
        sys.exit(0)

if __name__ == "__main__":
    main()
