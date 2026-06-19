#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
마중 스마트배시넷 EasyEDA Schematic 자동 생성 스크립트 (분할 처리 최적화 버전)
"""

import json
import os
import sys
import time
from easyeda_mcp_client import EasyEDAMCPClient

def get_net_for_pin(pin_to_net_map, des, pin_num, pin_name):
    comp_map = pin_to_net_map.get(des)
    if not comp_map:
        return None
    
    num_key = str(pin_num).lower() if pin_num else ""
    name_key = str(pin_name).lower() if pin_name else ""
    
    # 1. Direct match
    if num_key and num_key in comp_map:
        return comp_map[num_key]
    if name_key and name_key in comp_map:
        return comp_map[name_key]
        
    # 2. Normalization
    def norm(s):
        return "".join(c for c in s if c.isalnum()).lower()
        
    num_norm = norm(num_key)
    name_norm = norm(name_key)
    
    for k, net in comp_map.items():
        kn = norm(k)
        if num_norm and kn == num_norm:
            return net
        if name_norm and kn == name_norm:
            return net
            
    # 3. GPIO/IO aliases
    def get_gpio_num(s):
        n = norm(s)
        if n.startswith("gpio"):
            return n[4:]
        if n.startswith("io"):
            return n[2:]
        return None
        
    target_gpio = get_gpio_num(num_key) or get_gpio_num(name_key)
    if target_gpio:
        for k, net in comp_map.items():
            kn = get_gpio_num(k)
            if kn and kn == target_gpio:
                return net
                
    # 4. Prefix/Alias match — 접두사 한정(임의 부분문자열은 'en'이 'sensorvn'(IO39) 등에 오매칭됨)
    for k, net in comp_map.items():
        kn = norm(k)
        if name_norm and kn and (name_norm.startswith(kn) or kn.startswith(name_norm)):
            return net
            
    return None

def main():
    print("=========================================================")
    print("    마중 스마트배시넷 EasyEDA 회로도(Schematic) 자동 구성    ")
    print("=========================================================\n")

    # 1. 설계 구성 데이터 로드
    flow_file = "mcp_design_flow.json"
    if not os.path.exists(flow_file):
        print(f"[ERROR] '{flow_file}' 파일을 찾을 수 없습니다.")
        sys.exit(1)
        
    with open(flow_file, "r", encoding="utf-8") as f:
        flow = json.load(f)
        
    print(f"설계 데이터 로드 완료: {flow['project_name']}")
    
    # 2. 브릿지 클라이언트 초기화 및 연결
    client = EasyEDAMCPClient()
    if not client.connect():
        print("[ERROR] 브릿지 서버 및 에디터 연결 실패")
        sys.exit(1)

    components_js = json.dumps(flow["components"])
    
    grid_map = {
        "USB_C": {"x": 100, "y": 150},
        "D1": {"x": 100, "y": 270},
        "D2": {"x": 100, "y": 380},
        "U2": {"x": 250, "y": 150},
        "C3": {"x": 250, "y": 270},
        "C4": {"x": 250, "y": 380},
        "U3": {"x": 450, "y": 150},
        "L1": {"x": 450, "y": 270},
        "D3": {"x": 450, "y": 380},
        "C5": {"x": 450, "y": 490},
        "C6": {"x": 600, "y": 150},
        "C7": {"x": 600, "y": 250},
        "R1": {"x": 600, "y": 350},
        "R2": {"x": 600, "y": 450},
        "U1": {"x": 800, "y": 200},
        "C1": {"x": 800, "y": 400},
        "C2": {"x": 800, "y": 480},
        "UART_HDR": {"x": 980, "y": 200},
        "U5": {"x": 800, "y": 600},
        "C10": {"x": 800, "y": 700},
        "U4": {"x": 1000, "y": 450},
        "C8": {"x": 1000, "y": 600},
        "C9": {"x": 1000, "y": 700},
        "R7": {"x": 1200, "y": 450},
        "R8": {"x": 1200, "y": 530},
        "C18": {"x": 1200, "y": 610},
        "C19": {"x": 1200, "y": 690},
        "C20": {"x": 1200, "y": 770}
    }
    grid_map_js = json.dumps(grid_map)

    # 1단계: 컴포넌트 배치 및 핀 정보 리턴
    js_place_and_query = f"""
    let logs = [];
    try {{
        logs.push("1. 회로도 페이지 찾기 및 활성화");
        let pages = await eda.dmt_Schematic.getAllSchematicPagesInfo();
        if (!pages || pages.length === 0) {{
            logs.push("회로도 페이지 없음 -> 생성 시도");
            let schematics = await eda.dmt_Schematic.getAllSchematicsInfo();
            let schUuid;
            if (!schematics || schematics.length === 0) {{
                schUuid = await eda.dmt_Schematic.createSchematic();
            }} else {{
                schUuid = schematics[0].uuid;
            }}
            if (schUuid) {{
                await eda.dmt_Schematic.createSchematicPage(schUuid);
                await new Promise(resolve => setTimeout(resolve, 2000));
                pages = await eda.dmt_Schematic.getAllSchematicPagesInfo();
            }}
        }}
        if (!pages || pages.length === 0) {{
            return {{ success: false, error: "회로도 페이지 생성 실패", logs }};
        }}
        const pageUuid = pages[0].uuid;
        logs.push("페이지 열기: " + pageUuid);
        await eda.dmt_EditorControl.openDocument(pageUuid);
        await new Promise(resolve => setTimeout(resolve, 1500));
        await eda.dmt_EditorControl.activateDocument(pageUuid);
        await new Promise(resolve => setTimeout(resolve, 1500));

        logs.push("2. 기존 회로도 요소 클리어");
        const oldComps = await eda.sch_PrimitiveComponent.getAll();
        if (oldComps && oldComps.length > 0) {{
            const ids = oldComps.filter(c => c.getState_ComponentType() !== 'sheet').map(c => c.getState_PrimitiveId());
            if (ids.length > 0) {{
                logs.push("기존 부품 삭제 개수: " + ids.length);
                await eda.sch_PrimitiveComponent.delete(ids);
            }}
        }}
        const oldWires = await eda.sch_PrimitiveWire.getAll();
        if (oldWires && oldWires.length > 0) {{
            const ids = oldWires.map(w => w.getState_PrimitiveId());
            logs.push("기존 와이어 삭제 개수: " + ids.length);
            await eda.sch_PrimitiveWire.delete(ids);
        }}

        const flowComps = {components_js};
        const gridMap = {grid_map_js};

        logs.push("3. 디바이스 정보 조회 및 캐싱");
        const devMap = {{}};
        for (const compInfo of flowComps) {{
            const lcscId = compInfo.lcsc_id;
            try {{
                const devices = await eda.lib_Device.getByLcscIds([lcscId]);
                if (devices && devices.length > 0) {{
                    devMap[compInfo.designator] = devices[0];
                    logs.push("디바이스 캐싱 완료: " + compInfo.designator + " (" + lcscId + ")");
                }} else {{
                    logs.push("디바이스 캐시 없음 (LCSC 검색 안됨): " + compInfo.designator + " (" + lcscId + ")");
                }}
                await new Promise(resolve => setTimeout(resolve, 50));
            }} catch (e) {{
                logs.push("디바이스 조회 에러: " + compInfo.designator + " - " + e.message);
            }}
        }}

        logs.push("4. 순차 컴포넌트 배치");
        const schComps = [];
        for (const compInfo of flowComps) {{
            const des = compInfo.designator;
            const dev = devMap[des];
            if (!dev) {{
                logs.push("디바이스 배치 건너뜀 (캐시 없음): " + des);
                continue;
            }}
            const coords = gridMap[des] || {{ x: 800, y: 400 }};
            
            let schComp;
            try {{
                schComp = await eda.sch_PrimitiveComponent.create({{ libraryUuid: dev.libraryUuid, uuid: dev.uuid }}, coords.x, coords.y);
                logs.push("컴포넌트 배치 완료: " + des + " (" + coords.x + "," + coords.y + ")");
            }} catch(e) {{
                logs.push("컴포넌트 배치 실패: " + des + " - " + e.message);
            }}
            if (schComp) {{
                await schComp.setState_Designator(des);
                const linkId = "link_" + des;
                if (typeof schComp.setState_UniqueId === 'function') {{
                    await schComp.setState_UniqueId(linkId);
                }}
                if (typeof schComp.done === 'function') await schComp.done();
                schComps.push({{ des, schComp, coords }});
            }}
        }}

        logs.push("5. 모든 핀 정보 조회 및 수집");
        const pinData = [];
        for (const item of schComps) {{
            try {{
                const pins = await eda.sch_PrimitiveComponent.getAllPinsByPrimitiveId(item.schComp.getState_PrimitiveId());
                logs.push("핀 조회 완료: " + item.des + " (핀 개수: " + (pins ? pins.length : 0) + ")");
                if (pins) {{
                    for (const pin of pins) {{
                        pinData.push({{
                            des: item.des,
                            coords: item.coords,
                            pinNumber: pin.getState_PinNumber(),
                            pinName: pin.getState_PinName(),
                            x: pin.getState_X(),
                            y: pin.getState_Y()
                        }});
                    }}
                }}
                await new Promise(resolve => setTimeout(resolve, 30));
            }} catch (e) {{
                logs.push("핀 조회 실패: " + item.des + " - " + e.message);
            }}
        }}

        return {{ success: true, logs: logs, pins: pinData }};
    }} catch(e) {{
        return {{ success: false, error: e.message, stack: e.stack, logs: logs }};
    }}
    """

    print("1단계: 컴포넌트 배치 및 핀 좌표 정보 수집 중...")
    res1 = client.execute_js(js_place_and_query)
    
    if res1 and res1.get("logs"):
        print("\n=== 에디터 실행 로그 (1단계) ===")
        for log_line in res1.get("logs"):
            print(f"  [Editor] {log_line}")
        print("================================\n")
        
    if not res1 or not res1.get("success"):
        err = res1.get("error") if res1 else "알 수 없는 응답"
        print(f"[ERROR] 1단계 실패: {err}")
        sys.exit(1)
        
    pins = res1.get("pins", [])
    print(f"수집된 총 핀 개수: {len(pins)}개")

    # 2단계: 와이어 및 네트 태스크 계산 (파이썬에서 수행)
    flow_nets = flow["nets"]
    pin_to_net_map = {}
    for net_name, net_pins in flow_nets.items():
        for p in net_pins:
            des = p[0]
            pin_key = str(p[1]).lower()
            if des not in pin_to_net_map:
                pin_to_net_map[des] = {}
            pin_to_net_map[des][pin_key] = net_name

    all_wires = []
    net_tasks = []

    for pin in pins:
        des = pin["des"]
        coords = pin["coords"]
        pin_num = pin["pinNumber"]
        pin_name = pin["pinName"]
        
        net_name = get_net_for_pin(pin_to_net_map, des, pin_num, pin_name)
        if not net_name:
            continue
            
        px = pin["x"]
        py = pin["y"]
        
        if px is None or py is None:
            continue
            
        px = round(px)
        py = round(py)
        
        target_x = px
        target_y = py
        
        cx = coords["x"]
        cy = coords["y"]
        
        if px > cx:
            target_x += 30
        elif px < cx:
            target_x -= 30
        elif py > cy:
            target_y += 30
        elif py < cy:
            target_y -= 30
        else:
            target_y -= 30
            
        target_x = round(target_x)
        target_y = round(target_y)
        
        all_wires.append([px, py, target_x, target_y])
        
        # Net flag type determination
        net_type = 'Port'
        if net_name == 'GND':
            net_type = 'GND'
        elif net_name in ['VCC_3V3', 'VBUS_5V', 'PVDD_12V']:
            net_type = 'Power'
            
        net_tasks.append({
            "netName": net_name,
            "type": net_type,
            "x": target_x,
            "y": target_y
        })

    # --- S3 견고화: 스펙↔심볼 핀 커버리지 검증 (조용한 누락 방지) ---
    sym_by_des = {}
    for p in pins:
        sym_by_des.setdefault(p["des"], []).append((str(p["pinNumber"]), str(p["pinName"])))
    unmatched_spec = []
    for net_name_c, net_pins_c in flow_nets.items():
        for des_c, pinid_c in net_pins_c:
            matched = False
            for (num_c, name_c) in sym_by_des.get(des_c, []):
                if get_net_for_pin({des_c: {str(pinid_c).lower(): net_name_c}}, des_c, num_c, name_c) == net_name_c:
                    matched = True
                    break
            if not matched:
                unmatched_spec.append((des_c, pinid_c, net_name_c))
    if unmatched_spec:
        print(f"\n[WARN] 스펙↔심볼 미매칭 {len(unmatched_spec)}건 (연결 누락 위험 — 심볼 핀명/번호 확인 필요):")
        for d_, pid_, n_ in unmatched_spec:
            print(f"   - {d_}.{pid_}  (net {n_})")
        print("")
    else:
        print("[OK] 모든 스펙 핀이 심볼 핀과 매칭 확인됨")

    print(f"그려야 할 와이어: {len(all_wires)}개, 배치할 네트 포트/플래그: {len(net_tasks)}개")

    # 3단계: 와이어 및 네트 포트 분할(Chunk) 전송 및 드로잉
    # 1회 전송당 와이어 25개 + 네트 25개씩으로 분할하여 Timeout 회피
    chunk_size = 25
    total_chunks = (max(len(all_wires), len(net_tasks)) + chunk_size - 1) // chunk_size

    for i in range(total_chunks):
        chunk_wires = all_wires[i*chunk_size : (i+1)*chunk_size]
        chunk_nets = net_tasks[i*chunk_size : (i+1)*chunk_size]
        
        print(f"드로잉 묶음 {i+1}/{total_chunks} 전송 중 (와이어 {len(chunk_wires)}개, 네트 {len(chunk_nets)}개)...")
        
        js_draw_chunk = f"""
        let logs = [];
        const runWithTimeout = (promise, ms) => {{
            return Promise.race([
                promise,
                new Promise((_, reject) => setTimeout(() => reject(new Error("Timeout after " + ms + "ms")), ms))
            ]);
        }};

        try {{
            const wires = {json.dumps(chunk_wires)};
            const nets = {json.dumps(chunk_nets)};
            
            logs.push("와이어 그리기 시작");
            for (const wire of wires) {{
                try {{
                    await runWithTimeout(eda.sch_PrimitiveWire.create(wire), 2000);
                }} catch(e) {{
                    logs.push("와이어 생성 실패: " + JSON.stringify(wire) + " - " + e.message);
                }}
                await new Promise(resolve => setTimeout(resolve, 35));
            }}
            
            logs.push("네트 생성 시작");
            for (const task of nets) {{
                try {{
                    let p;
                    if (task.type === 'GND') {{
                        p = eda.sch_PrimitiveComponent.createNetFlag('Ground', 'GND', task.x, task.y);
                    }} else if (task.type === 'Power') {{
                        p = eda.sch_PrimitiveComponent.createNetFlag('Power', task.netName, task.x, task.y);
                    }} else {{
                        p = eda.sch_PrimitiveComponent.createNetPort('BI', task.netName, task.x, task.y);
                    }}
                    await runWithTimeout(p, 2000);
                }} catch(e) {{
                    logs.push("네트 생성 실패: " + task.netName + " - " + e.message);
                }}
                await new Promise(resolve => setTimeout(resolve, 35));
            }}
            return {{ success: true, logs: logs }};
        }} catch(e) {{
            return {{ success: false, error: e.message, logs: logs }};
        }}
        """
        
        res_chunk = client.execute_js(js_draw_chunk)
        if not res_chunk or not res_chunk.get("success"):
            err = res_chunk.get("error") if res_chunk else "알 수 없는 응답"
            print(f"[Warning] 드로잉 묶음 {i+1} 실행 실패: {err}")
            if res_chunk and res_chunk.get("logs"):
                print("상세 로그:")
                for log_line in res_chunk.get("logs"):
                    print(f"  [Editor] {log_line}")
        else:
            print(f"[OK] 묶음 {i+1} 그리기 완료")
            
        time.sleep(0.5) # 안전 대기

    # 4단계: PCB Unique ID 동기화 및 마무리
    js_sync_pcb = f"""
    try {{
        let pcbUuid = null;
        try {{
            const pcbs = await eda.dmt_Pcb.getAllPcbsInfo();
            if (pcbs && pcbs.length > 0) {{
                pcbUuid = pcbs[0].uuid;
            }} else {{
                const pcbInfo = await eda.dmt_Pcb.getCurrentPcbInfo();
                if (pcbInfo) pcbUuid = pcbInfo.uuid;
            }}
        }} catch(e) {{}}
        if (!pcbUuid) {{
            pcbUuid = "c9f1fdba7e0a3f4c";
        }}
        await eda.dmt_EditorControl.openDocument(pcbUuid);
        await new Promise(resolve => setTimeout(resolve, 2000));
        await eda.dmt_EditorControl.activateDocument(pcbUuid);
        await new Promise(resolve => setTimeout(resolve, 2000));

        const pcbComps = await eda.pcb_PrimitiveComponent.getAll();
        if (pcbComps && pcbComps.length > 0) {{
            for (const c of pcbComps) {{
                const des = c.designator || c.getState_Designator();
                if (des) {{
                    const linkId = "link_" + des;
                    const asyncC = c.toAsync();
                    if (typeof asyncC.setState_UniqueId === 'function') {{
                        await asyncC.setState_UniqueId(linkId);
                    }}
                    await asyncC.done();
                }}
            }}
        }}

        // 다시 회로도 활성화하여 화면 표시 유지
        const pages = await eda.dmt_Schematic.getAllSchematicPagesInfo();
        if (pages && pages.length > 0) {{
            await eda.dmt_EditorControl.activateDocument(pages[0].uuid);
        }}
        return {{ success: true }};
    }} catch(e) {{
        return {{ success: false, error: e.message, stack: e.stack }};
    }}
    """

    print("마무리 단계: PCB Unique ID 동기화 작업 전송 중...")
    res_sync = client.execute_js(js_sync_pcb)

    if res_sync and res_sync.get("success"):
        print("\n=========================================================")
        print(" 회로도(Schematic1) 자동 생성 및 PCB 매핑(UniqueId) 완료! ")
        print(" 에디터에서 PCB와 회로도가 정상 연결된 것을 확인하세요.   ")
        print("=========================================================\n")
    else:
        err = res_sync.get("error") if res_sync else "알 수 없는 응답"
        print(f"\n[ERROR] PCB 동기화 실패: {err}")
        sys.exit(1)

if __name__ == "__main__":
    main()
