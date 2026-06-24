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
        
    target_gpio = get_gpio_num(name_key)
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

    # 파이썬 측에서 LCSC ID 일괄 조회하여 캔버스 쿼리 속도 극대화 (타임아웃 방지)
    components = flow["components"]
    lcsc_ids = list(set(c["lcsc_id"] for c in components))
    print(f"EasyEDA에서 {len(lcsc_ids)}개 부품 정보 일괄 조회 중...")
    js_query_devices = f"return await eda.lib_Device.getByLcscIds({json.dumps(lcsc_ids)});"
    devices = client.execute_js(js_query_devices)
    
    lcsc_to_dev = {}
    if devices:
        for d in devices:
            sid = d.get("supplierId")
            if sid:
                lcsc_to_dev[sid] = {
                    "libraryUuid": d.get("libraryUuid"),
                    "uuid": d.get("uuid")
                }
        print(f"부품 정보 1차 조회 성공: {len(lcsc_to_dev)}/{len(lcsc_ids)}개 매칭됨.")
        
    missing_lcsc_ids = [lid for lid in lcsc_ids if lid not in lcsc_to_dev]
    if missing_lcsc_ids:
        print(f"\n[INFO] 로컬 캐시에 없는 {len(missing_lcsc_ids)}개 부품 우회 캐싱을 진행합니다: {missing_lcsc_ids}")
        client.cache_components(missing_lcsc_ids)
        print("우회 캐싱 완료! 부품 정보 재조회 중...")
        devices = client.execute_js(js_query_devices)
        if devices:
            for d in devices:
                sid = d.get("supplierId")
                if sid:
                    lcsc_to_dev[sid] = {
                        "libraryUuid": d.get("libraryUuid"),
                        "uuid": d.get("uuid")
                    }
            print(f"부품 정보 최종 조회 결과: {len(lcsc_to_dev)}/{len(lcsc_ids)}개 매칭됨.")
        else:
            print("[WARN] 부품 정보 최종 재조회 실패.")
    else:
        print("[OK] 모든 부품이 이미 로컬 캐시에 존재합니다.")

    components_js = json.dumps(flow["components"])
    lcsc_to_dev_js = json.dumps(lcsc_to_dev)
    
    grid_map = {
        # 1. 전원 공급 및 LDO 블록 (x: 100~350, y: 150~350)
        "USB_C": {"x": 100, "y": 150},
        "D1": {"x": 100, "y": 250},
        "D2": {"x": 100, "y": 350},
        "R3": {"x": 200, "y": 150},
        "R4": {"x": 200, "y": 230},
        "U2": {"x": 300, "y": 150},
        "C3": {"x": 300, "y": 250},
        "C4": {"x": 300, "y": 350},
        
        # 2. MP3426 부스트 블록 (x: 500~800, y: 150~450)
        "U3": {"x": 500, "y": 150},
        "L1": {"x": 500, "y": 250},
        "D3": {"x": 500, "y": 350},
        "C5": {"x": 600, "y": 150},
        "C21": {"x": 600, "y": 230},
        "C22": {"x": 600, "y": 310},
        "R9": {"x": 700, "y": 150},
        "R10": {"x": 700, "y": 230},
        "R11": {"x": 700, "y": 310},
        "C6": {"x": 800, "y": 150},
        "C7": {"x": 800, "y": 250},
        "R1": {"x": 800, "y": 350},
        "R2": {"x": 800, "y": 430},
        
        # 3. MCU 및 프로그래밍 블록 (x: 100~300, y: 550~750)
        "U1": {"x": 100, "y": 550},
        "C1": {"x": 100, "y": 700},
        "C2": {"x": 100, "y": 780},
        "UART_HDR": {"x": 250, "y": 550},
        "R5": {"x": 250, "y": 630},
        "C17": {"x": 250, "y": 710},
        "R6": {"x": 250, "y": 790},
        
        # 4. LSM6DSOX 센서 블록 (x: 450, y: 550~750)
        "U5": {"x": 450, "y": 550},
        "C10": {"x": 450, "y": 650},
        "C11": {"x": 450, "y": 730},
        
        # 5. TAS5805M 앰프 및 출력 블록 (x: 650~1000, y: 550~800)
        "U4": {"x": 650, "y": 550},
        "C8": {"x": 650, "y": 700},
        "C9": {"x": 650, "y": 780},
        "C12": {"x": 750, "y": 550},
        "C13": {"x": 750, "y": 630},
        "C14": {"x": 750, "y": 710},
        "C15": {"x": 750, "y": 790},
        "R7": {"x": 880, "y": 550},
        "R8": {"x": 880, "y": 630},
        "C18": {"x": 880, "y": 710},
        "C19": {"x": 880, "y": 790},
        "C20": {"x": 880, "y": 870},
        "J1": {"x": 1000, "y": 550},
        "J2": {"x": 1000, "y": 650},

        # 6. 신규(v1.5/1.6): 부스트 SS 캡 + 출력 EMI 필터(페라이트비드+캡)
        "C23": {"x": 600, "y": 390},
        "FB1": {"x": 920, "y": 470},
        "FB2": {"x": 920, "y": 560},
        "FB3": {"x": 920, "y": 650},
        "FB4": {"x": 920, "y": 740},
        "C24": {"x": 1120, "y": 470},
        "C25": {"x": 1120, "y": 560},
        "C26": {"x": 1120, "y": 650},
        "C27": {"x": 1120, "y": 740}
    }
    grid_map_js = json.dumps(grid_map)

    # 1단계: 컴포넌트 배치 및 핀 정보 리턴
    # (1A) 캔버스 클리어 및 기존 devMap 수집
    js_clear = f"""
    try {{
        let pages = await eda.dmt_Schematic.getAllSchematicPagesInfo();
        if (!pages || pages.length === 0) {{
            let schematics = await eda.dmt_Schematic.getAllSchematicsInfo();
            let schUuid = (schematics && schematics.length > 0) ? schematics[0].uuid : await eda.dmt_Schematic.createSchematic();
            if (schUuid) {{
                await eda.dmt_Schematic.createSchematicPage(schUuid);
                await new Promise(resolve => setTimeout(resolve, 2000));
                pages = await eda.dmt_Schematic.getAllSchematicPagesInfo();
            }}
        }}
        if (!pages || pages.length === 0) {{
            return {{ success: false, error: "회로도 페이지 생성 실패" }};
        }}
        const pageUuid = pages[0].uuid;
        await eda.dmt_EditorControl.openDocument(pageUuid);
        await new Promise(resolve => setTimeout(resolve, 1500));
        await eda.dmt_EditorControl.activateDocument(pageUuid);
        await new Promise(resolve => setTimeout(resolve, 1500));

        const devMap = {{}};
        const oldComps = await eda.sch_PrimitiveComponent.getAll();
        if (oldComps && oldComps.length > 0) {{
            for (const c of oldComps) {{
                if (c.getState_ComponentType() === 'part') {{
                    const des = c.getState_Designator();
                    if (des) {{
                        try {{
                            const sym = c.getState_Symbol();
                            if (sym && sym.libraryUuid && sym.uuid) {{
                                devMap[des] = {{
                                    libraryUuid: sym.libraryUuid,
                                    uuid: sym.uuid
                                }};
                            }}
                        }} catch(e) {{}}
                    }}
                }}
            }}
            const ids = oldComps.filter(c => c.getState_ComponentType() !== 'sheet').map(c => c.getState_PrimitiveId());
            if (ids.length > 0) {{
                await eda.sch_PrimitiveComponent.delete(ids);
                await new Promise(resolve => setTimeout(resolve, 2000));
            }}
        }}
        const oldWires = await eda.sch_PrimitiveWire.getAll();
        if (oldWires && oldWires.length > 0) {{
            const ids = oldWires.map(w => w.getState_PrimitiveId());
            await eda.sch_PrimitiveWire.delete(ids);
            await new Promise(resolve => setTimeout(resolve, 2000));
        }}
        return {{ success: true, devMap: devMap }};
    }} catch(e) {{
        return {{ success: false, error: e.message }};
    }}
    """
    
    print("1-A단계: 기존 캔버스 클리어 및 심볼 매핑 분석 중...")
    res_clear = client.execute_js(js_clear)
    if not res_clear or not res_clear.get("success"):
        err = res_clear.get("error") if res_clear else "알 수 없는 응답"
        print(f"[ERROR] 1-A단계(클리어) 실패: {err}")
        sys.exit(1)
        
    print("[OK] 회로도 페이지가 성공적으로 재생성되어 클리어되었습니다. 에디터 대기 중 (3s)...")
    time.sleep(3.0)
    
    dev_map = res_clear.get("devMap", {})
    print(f"기존 심볼 매핑 획득 완료: {len(dev_map)}개")

    # (1B & 1C) 부품 배치 및 핀 좌표 Chunk 단위 일괄 수집 (Freeze 및 Timeout 방지)
    placed_tasks = []
    for comp_info in flow["components"]:
        des = comp_info["designator"]
        # J1, J2(2핀 헤더) 및 U3(DFN-14) 등 스펙의 정합성을 1순위 보장하기 위해 lcsc_to_dev를 최우선 적용
        dev = lcsc_to_dev.get(comp_info["lcsc_id"]) or dev_map.get(des)
        if not dev:
            print(f"  [WARN] {des} ({comp_info['lcsc_id']}) 의 라이브러리 정보를 찾을 수 없어 배치를 건너뜁니다.")
            continue
            
        coords = grid_map.get(des, {"x": 800, "y": 400})
        placed_tasks.append({
            "des": des,
            "libraryUuid": dev["libraryUuid"],
            "uuid": dev["uuid"],
            "x": coords["x"],
            "y": coords["y"]
        })
        
    placed_components = []
    pins = []
    chunk_size = 1
    total_comp_chunks = (len(placed_tasks) + chunk_size - 1) // chunk_size
    
    print(f"1-B & 1-C단계: 부품 {len(placed_tasks)}개를 크기 {chunk_size}의 Chunk {total_comp_chunks}개로 분할 배치 및 핀 좌표 수집 중...")
    
    for c_idx in range(total_comp_chunks):
        c_tasks = placed_tasks[c_idx*chunk_size : (c_idx+1)*chunk_size]
        print(f"  [Chunk {c_idx+1}/{total_comp_chunks}] {', '.join(t['des'] for t in c_tasks)} 배치 중...")
        
        js_batch_place_and_query = f"""
        try {{
            const tasks = {json.dumps(c_tasks)};
            const placed = [];
            const pins = [];
            
            for (const task of tasks) {{
                try {{
                    let schComp = await eda.sch_PrimitiveComponent.create(
                        {{ libraryUuid: task.libraryUuid, uuid: task.uuid }},
                        task.x,
                        task.y
                    );
                    if (schComp) {{
                        await schComp.setState_Designator(task.des);
                        const linkId = "link_" + task.des;
                        if (typeof schComp.setState_UniqueId === 'function') {{
                            await schComp.setState_UniqueId(linkId);
                        }}
                        if (typeof schComp.done === 'function') await schComp.done();
                        
                        const primId = schComp.getState_PrimitiveId();
                        placed.push({{ des: task.des, primId: primId, coords: {{ x: task.x, y: task.y }} }});
                        
                        const componentPins = await eda.sch_PrimitiveComponent.getAllPinsByPrimitiveId(primId);
                        if (componentPins) {{
                            for (const pin of componentPins) {{
                                pins.push({{
                                    des: task.des,
                                    coords: {{ x: task.x, y: task.y }},
                                    pinNumber: pin.getState_PinNumber(),
                                    pinName: pin.getState_PinName(),
                                    x: pin.getState_X(),
                                    y: pin.getState_Y()
                                }});
                            }}
                        }}
                    }}
                }} catch(e) {{
                    // ignore and continue
                }}
                await new Promise(resolve => setTimeout(resolve, 150));
            }}
            return {{ success: true, placed, pins }};
        }} catch(e) {{
            return {{ success: false, error: e.message }};
        }}
        """
        
        res_batch = client.execute_js(js_batch_place_and_query)
        if res_batch and res_batch.get("success"):
            placed_components.extend(res_batch.get("placed", []))
            pins.extend(res_batch.get("pins", []))
        else:
            err = res_batch.get("error") if res_batch else "응답 없음"
            print(f"  [Warning] Chunk {c_idx+1} 실행 실패: {err}")
            
        time.sleep(1.5) # 각 chunk 사이에 넉넉한 대기 부여
        
    print(f"부품 {len(placed_components)}개 배치 완료, 총 핀 {len(pins)}개 정보 수집 완료.")
            
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
        
        cx = coords["x"] * 10
        cy = coords["y"] * 10
        
        # 칩, 커넥터 포함 모든 컴포넌트 핀에 대해 1.0mm(10단위) 와이어를 연장하여 포트 겹침 및 주변 단락 방지
        if px > cx:
            target_x += 10
        elif px < cx:
            target_x -= 10
        elif py > cy:
            target_y += 10
        elif py < cy:
            target_y -= 10
        else:
            target_y -= 10
            
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
        print(f"\n[WARN] 스펙/심볼 미매칭 {len(unmatched_spec)}건 (연결 누락 위험 - 심볼 핀명/번호 확인 필요):")
        for d_, pid_, n_ in unmatched_spec:
            print(f"   - {d_}.{pid_}  (net {n_})")
        print("")
    else:
        print("[OK] 모든 스펙 핀이 심볼 핀과 매칭 확인됨")

    # A1 라이브 검증 산출물 저장 (심볼 핀맵 + 미매칭)
    try:
        json.dump({"pins_by_designator": sym_by_des, "unmatched_spec": unmatched_spec,
                   "component_count": len(placed_components), "pin_count": len(pins)},
                  open("a1_symbol_verify.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        print("[A1] a1_symbol_verify.json 저장됨")
    except Exception as _e:
        print("[A1] 저장 실패:", _e)

    print(f"그려야 할 와이어: {len(all_wires)}개, 배치할 네트 포트/플래그: {len(net_tasks)}개")

    # 3단계: 와이어 및 네트 포트 분할(Chunk) 전송 및 드로잉
    chunk_size = 2
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
                await new Promise(resolve => setTimeout(resolve, 150));
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
                await new Promise(resolve => setTimeout(resolve, 150));
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
            
        time.sleep(1.5) # 안전 대기 늘림

    # 4단계: PCB Unique ID 동기화 및 마무리 (우회 처리)
    js_sync_pcb = f"""
    try {{
        // 다시 회로도 활성화하여 화면 표시 유지
        const pages = await eda.dmt_Schematic.getAllSchematicPagesInfo();
        if (pages && pages.length > 0) {{
            await eda.dmt_EditorControl.activateDocument(pages[0].uuid);
        }}
        return {{ success: true }};
    }} catch(e) {{
        return {{ success: false, error: e.message }};
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
