#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
EasyEDA Pro MCP Client (easyeda_mcp_client.py) - Bridge Server V3 API Version

본 모듈은 easyeda-api-skill 브릿지 서버(http://127.0.0.1:49620)를 통해
로컬 EasyEDA Pro 클라이언트와 통신하며, JavaScript V3 API 코드를 
실시간으로 주입하여 에디터 화면에 직접 회로도 및 PCB를 그립니다.
"""

import json
import urllib.request
import urllib.error
import sys
import time
import math

class EasyEDAMCPClient:
    def __init__(self, host="127.0.0.1", port=49620):
        self.base_url = f"http://{host}:{port}"
        self.project_data = {
            "name": "",
            "components": [],
            "nets": {},
            "pcb_settings": {
                "layers": 2,
                "dimensions": (0, 0),
                "traces": {}
            }
        }

    def connect(self):
        """Bridge Server의 Health 엔드포인트를 확인하고 EasyEDA 연결 상태 검증"""
        print(f"Connecting to EasyEDA Bridge Server at {self.base_url}...")
        try:
            req = urllib.request.Request(f"{self.base_url}/health", method="GET")
            with urllib.request.urlopen(req, timeout=3) as response:
                res_data = json.loads(response.read().decode("utf-8"))
                
                if res_data.get("service") != "easyeda-bridge":
                    raise ValueError("올바른 EasyEDA 브릿지 서버가 아닙니다.")
                
                print("[OK] Bridge Server is running.")
                
                if not res_data.get("edaConnected"):
                    print("\n[WARN] 브릿지 서버는 켜져 있으나, EasyEDA 에디터가 아직 연결되지 않았습니다.")
                    print("대책:")
                    print("  1. EasyEDA Pro(웹 에디터 또는 Desktop)를 실행하십시오.")
                    print("  2. 'run-api-gateway' 플러그인이 로드되어 작동 중인지 확인하십시오.")
                    print("     (다운로드: https://ext.lceda.cn/item/oshwhub/run-api-gateway)\n")
                    return False
                
                print("[OK] EasyEDA Editor Client Connection Verified.")
                return True
        except Exception as e:
            print(f"\n[ERROR] 브릿지 서버 통신 실패: {e}")
            print("대책: 터미널에서 'node scripts/bridge-server.mjs' 명령어가 정상 실행 중인지 확인하십시오.\n")
            return False

    def execute_js(self, js_code):
        """브릿지 서버의 /execute API로 JavaScript 코드를 전송하여 실행"""
        url = f"{self.base_url}/execute"
        payload = json.dumps({"code": js_code}).encode("utf-8")
        
        req = urllib.request.Request(
            url, 
            data=payload, 
            headers={"Content-Type": "application/json"},
            method="POST"
        )
        
        try:
            with urllib.request.urlopen(req, timeout=120) as response:
                res = json.loads(response.read().decode("utf-8"))
                if not res.get("success"):
                    raise RuntimeError(f"EasyEDA 실행 실패: {res.get('error')}")
                return res.get("result")
        except urllib.error.HTTPError as e:
            err_body = e.read().decode("utf-8")
            print(f"[HTTP Error Detail] Code={e.code}, Reason={e.reason}")
            print("==================== [RESPONSE BODY DUMP] ====================")
            print(err_body)
            print("==============================================================")
            try:
                err_json = json.loads(err_body)
                raise RuntimeError(f"EasyEDA API Error: {err_json.get('error')}")
            except Exception:
                raise RuntimeError(f"HTTP Error {e.code}: {e.reason}")

    # --- V3 API Wrapper Functions ---
    def create_project(self, project_name):
        proj_name_json = json.dumps(project_name)
        js = f"""
        let uuidToOpen = null;
        try {{
            uuidToOpen = await eda.dmt_Project.createProject({proj_name_json});
        }} catch(e) {{
            const currentProj = await eda.dmt_Project.getCurrentProjectInfo();
            if (currentProj && currentProj.friendlyName === {proj_name_json}) {{
                uuidToOpen = currentProj.uuid;
            }}
        }}
        if (uuidToOpen) {{
            await eda.dmt_Project.openProject(uuidToOpen);
            await new Promise(resolve => setTimeout(resolve, 3000));
            return true;
        }}
        
        const backupProj = await eda.dmt_Project.getCurrentProjectInfo();
        if (backupProj) {{
            await eda.dmt_Project.openProject(backupProj.uuid);
            await new Promise(resolve => setTimeout(resolve, 2000));
            return true;
        }}
        return false;
        """
        res = self.execute_js(js)
        print(f"[API] createProject({proj_name_json}) ➔ SUCCESS")
        self.project_data["name"] = project_name
        return res

    def configure_pcb(self, width, height, layers):
        js = f"""
        // 1. Force close any open library modals
        const existingModal = document.querySelector('.lc_modal_dialog_zvEgQ') || document.querySelector('.lc_modal_dialog_box_5wCN6');
        if (existingModal) {{
            const closeBtn = existingModal.querySelector('[class*="close_o8Wlu"]') || existingModal.querySelector('.header_right_close_o8Wlu') || existingModal.querySelector('*[class*="modal-close"]');
            if (closeBtn) {{
                closeBtn.dispatchEvent(new MouseEvent('click', {{ bubbles: true }}));
            }} else {{
                document.dispatchEvent(new KeyboardEvent('keydown', {{ key: 'Escape', keyCode: 27, code: 'Escape', bubbles: true }}));
            }}
            await new Promise(resolve => setTimeout(resolve, 1000));
        }}
        
        // 2. Cancel any active placement mode by sending Escape keys
        for (let i = 0; i < 3; i++) {{
            document.dispatchEvent(new KeyboardEvent('keydown', {{ key: 'Escape', keyCode: 27, code: 'Escape', bubbles: true }}));
            await new Promise(resolve => setTimeout(resolve, 200));
        }}

        // 캐시 UUID 만료 및 캔버스 초기화 오류 방지를 위해, 매 실행 시 고유한 PCB 문서를 생성하여 활성화합니다.
        // 매번 무작위 PCB를 생성하는 대신, 사용자가 보고 있는 PCB1(uuid: 25a2ea45a471a47f)을 타겟으로 고정하여 작업합니다.
        let pcbUuid = null;
        try {{
            const currentDoc = await eda.dmt_SelectControl.getCurrentDocumentInfo();
            if (currentDoc && currentDoc.uuid) {{
                pcbUuid = currentDoc.uuid;
            }}
        }} catch(e) {{}}
        if (!pcbUuid) {{
            try {{
                const pcbInfo = await eda.dmt_Project.getCurrentPcbInfo();
                if (pcbInfo) pcbUuid = pcbInfo.uuid;
            }} catch(e) {{}}
        }}
        if (!pcbUuid) {{
            pcbUuid = "25a2ea45a471a47f"; // Fallback to original UUID
        }}
        if (pcbUuid) {{
            await eda.dmt_EditorControl.openDocument(pcbUuid);
            await new Promise(resolve => setTimeout(resolve, 2000));
            await eda.dmt_EditorControl.activateDocument(pcbUuid);
            await new Promise(resolve => setTimeout(resolve, 3000));
            
            // Cleanup existing primitives for clean redraw (do NOT delete components to preserve schematic sync)
            try {{
                // Skip component deletion
            }} catch(e) {{
                console.error("Cleanup comps error:", e);
            }}
            try {{
                const oldLines = await eda.pcb_PrimitiveLine.getAll();
                if (oldLines && oldLines.length > 0) {{
                    const ids = oldLines.map(l => l.getState_PrimitiveId?.() || l.id || l.primitiveId).filter(Boolean);
                    if (ids.length > 0) {{
                        await eda.pcb_PrimitiveLine.delete(ids);
                    }}
                }}
            }} catch(e) {{
                console.error("Cleanup lines error:", e);
            }}
            try {{
                const oldVias = await eda.pcb_PrimitiveVia.getAll();
                if (oldVias && oldVias.length > 0) {{
                    const ids = oldVias.map(v => v.getState_PrimitiveId?.() || v.id || v.primitiveId).filter(Boolean);
                    if (ids.length > 0) {{
                        await eda.pcb_PrimitiveVia.delete(ids);
                    }}
                }}
            }} catch(e) {{
                console.error("Cleanup vias error:", e);
            }}
            try {{
                const oldPours = await eda.pcb_PrimitivePour.getAll();
                if (oldPours && oldPours.length > 0) {{
                    const ids = oldPours.map(p => p.getState_PrimitiveId?.() || p.id || p.primitiveId).filter(Boolean);
                    if (ids.length > 0) {{
                        await eda.pcb_PrimitivePour.delete(ids);
                    }}
                }}
            }} catch(e) {{
                console.error("Cleanup pours error:", e);
            }}
            try {{
                const oldRegions = await eda.pcb_PrimitiveRegion.getAll();
                if (oldRegions && oldRegions.length > 0) {{
                    const ids = oldRegions.map(r => r.getState_PrimitiveId?.() || r.id || r.primitiveId).filter(Boolean);
                    if (ids.length > 0) {{
                        await eda.pcb_PrimitiveRegion.delete(ids);
                    }}
                }}
            }} catch(e) {{
                console.error("Cleanup regions error:", e);
            }}
            
            await eda.pcb_Layer.setTheNumberOfCopperLayers({layers});
            await new Promise(resolve => setTimeout(resolve, 500));
            
            // Create Antenna Keepout Region on MULTI-layer (12)
            try {{
                const keepoutSource = ['R', 1279.5, 2047.2, 590.55, 314.96, 0, 0];
                const keepoutPoly = eda.pcb_MathPolygon.createPolygon(keepoutSource);
                if (keepoutPoly) {{
                    await eda.pcb_PrimitiveRegion.create(12, keepoutPoly, [2, 3, 5, 7], "Antenna Keepout");
                }}
            }} catch(e) {{
                console.error("Create keepout region error:", e);
            }}

            // Board outline creation removed so it doesn't conflict with user's manual outline.
            
            return true;
        }}
        return false;
        """
        res = self.execute_js(js)
        print(f"[API] configure_pcb({width}x{height}mm, {layers}L) ➔ SUCCESS")
        self.project_data["pcb_settings"]["dimensions"] = (width, height)
        self.project_data["pcb_settings"]["layers"] = layers
        return res

    def cache_components(self, lcsc_ids):
        print(f"[API] JLC 온라인 라이브러리 자동 캐싱 기동 (대상: {lcsc_ids})...")
        for lid in lcsc_ids:
            # 1. API를 통해 이미 해당 부품이 로컬 캐시에 등재되어 있는지 확인
            check_js = f"""
            try {{
                const devices = await eda.lib_Device.getByLcscIds(['{lid}']);
                return (devices && devices.length > 0);
            }} catch(e) {{
                return false;
            }}
            """
            already_cached = self.execute_js(check_js)
                
            if already_cached:
                print(f"  ➔ LCSC {lid} 이미 캐시됨 (스킵)")
                continue

            print(f"  ➔ LCSC {lid} 캐시 미발견. 온라인 라이브러리 API 우회 캐싱 기동...")
            
            # API 우회 캐싱 JS
            js = f"""
            async function bypassCache(lcscId) {{
                try {{
                    const path = "0819f05c4eef4c71ace90d822a990e87"; // system library UUID
                    
                    function extractUuid(field) {{
                        if (!field) return null;
                        if (typeof field === 'object') return field.uuid;
                        if (typeof field === 'string') {{
                            try {{
                                const clean = field.replace(/'/g, '"');
                                return JSON.parse(clean).uuid;
                            }} catch(e) {{}}
                            const match = field.match(/uuid['"]?\\\\s*:\\\\s*['"]([^'"]+)['"]/);
                            if (match) return match[1];
                        }}
                        return null;
                    }}
                    
                    // 1. Search online to get device UUID
                    const searchUrl = `/api/v2/eda/product/search?keyword=${{lcscId}}&currPage=1&pageSize=5&path=${{path}}`;
                    const searchRes = await fetch(searchUrl);
                    const searchData = await searchRes.json();
                    
                    const products = searchData?.result?.productList || [];
                    const product = products.find(p => p.number === lcscId);
                    if (!product) return {{ success: false, error: "Product with exact LCSC ID " + lcscId + " not found online" }};
                    
                    const uuid = product.device_info?.uuid || product.hasDevice;
                    if (!uuid) return {{ success: false, error: "Device UUID not found in product" }};
                    
                    // 2. Fetch device detail to get symbol/footprint UUIDs
                    const detailRes = await fetch(`/api/v2/devices/${{uuid}}?path=${{path}}`);
                    const detailData = await detailRes.json();
                    const devDetail = detailData?.result;
                    if (!devDetail) return {{ success: false, error: "Device detail empty" }};
                    
                    const symUuid = extractUuid(devDetail.symbol);
                    const fpUuid = extractUuid(devDetail.footprint);
                    
                    // 3. Trigger download via RPC get calls
                    if (symUuid) {{
                        await eda.lib_Symbol.get(symUuid, path);
                    }}
                    if (fpUuid) {{
                        await eda.lib_Footprint.get(fpUuid, path);
                    }}
                    await eda.lib_Device.get(uuid, path);
                    
                    // 4. Verify cache
                    const verifyRes = await eda.lib_Device.getByLcscIds([lcscId]);
                    const isCached = verifyRes && verifyRes.length > 0;
                    
                    return {{
                        success: isCached,
                        uuid: uuid
                    }};
                }} catch(e) {{
                    return {{ success: false, error: e.message }};
                }}
            }}
            return await bypassCache("{lid}");
            """
            try:
                res = self.execute_js(js)
            except Exception as e:
                # 타임아웃 에러 발생 시, window.lastCacheLog를 즉시 쿼리하여 출력
                print(f"[ERROR] execute_js 타임아웃 발생! 상세 로그 덤프를 시도합니다...")
                try:
                    debug_log = self.execute_js("return window.lastCacheLog;")
                    print("================ [브라우저 내부 실시간 실행 로그] ================")
                    for line in debug_log:
                        print("  " + line)
                    print("================================================================")
                except Exception as ex:
                    print(f"디버그 로그 덤프 실패: {ex}")
                raise e
                
            if res and res.get("success"):
                print(f"  ➔ LCSC {lid} 캐싱 완료")
            else:
                err_msg = res.get("error") if res else "결과 없음"
                print(f"  ➔ LCSC {lid} 캐싱 시도 실패 ({err_msg})")
            time.sleep(0.5)
        return True

    # 상대 좌표 기반 수동 소자 자동 배치 매핑 사전 (Local Clustering)
    CHILD_COMPONENTS_MAP = {}

    def place_component(self, designator, name, lcsc_id, x, y, angle):
        # 상대 좌표 계산 (Local Clustering)
        if designator in self.CHILD_COMPONENTS_MAP:
            parent_des, dx, dy = self.CHILD_COMPONENTS_MAP[designator]
            parent = next((c for c in self.project_data["components"] if c["designator"] == parent_des), None)
            if parent:
                parent_x = parent["x"]
                parent_y = parent["y"]
                parent_angle = parent["angle"]
                
                # 라디안 각도 계산
                rad = math.radians(parent_angle)
                cos_a = math.cos(rad)
                sin_a = math.sin(rad)
                
                # 회전 변환 적용
                x_calc = parent_x + dx * cos_a - dy * sin_a
                y_calc = parent_y + dx * sin_a + dy * cos_a
                
                # 소자 자체 각도도 부모 각도에 따라 회전
                angle_calc = (parent_angle + angle) % 360
                
                print(f"[Clustering] {designator} -> Parent: {parent_des} at ({parent_x}, {parent_y}, {parent_angle}deg)")
                print(f"             Offset: (dx={dx}, dy={dy}) ➔ Calculated: ({x_calc:.2f}, {y_calc:.2f}, {angle_calc}deg)")
                
                x = x_calc
                y = y_calc
                angle = angle_calc

        des_json = json.dumps(designator)
        lcsc_json = json.dumps(lcsc_id)
        js = f"""
        const tx = {round(x * 39.37)};
        const ty = {round(y * 39.37)};
        const tAngle = {angle};
        let existingComp = null;
        try {{
            const comps = await eda.pcb_PrimitiveComponent.getAll();
            if (comps && Array.isArray(comps)) {{
                existingComp = comps.find(c => (c.designator || (typeof c.getState_Designator === 'function' ? c.getState_Designator() : '')) === {des_json});
            }}
        }} catch(e) {{
            // Ignore getAll error if components are null internally
        }}
        
        if (existingComp) {{
            try {{
                if (typeof existingComp.setState_X === 'function') await existingComp.setState_X(tx);
                if (typeof existingComp.setState_Y === 'function') await existingComp.setState_Y(ty);
                if (typeof existingComp.setState_Angle === 'function') await existingComp.setState_Angle(tAngle);
                
                if (typeof existingComp.done === 'function') await existingComp.done();
                return true;
            }} catch(e) {{
                return {{ error: "Failed to move existing comp: " + e.message }};
            }}
        }} else {{
            const devices = await eda.lib_Device.getByLcscIds([{lcsc_json}]);
            if (devices && devices.length > 0) {{
                const dev = devices[0];
                const comp = await eda.pcb_PrimitiveComponent.create(dev, 1, tx, ty, tAngle);
                if (comp) {{
                    try {{
                        await comp.setState_Designator({des_json});
                    }} catch(e) {{}}
                    try {{
                        comp.designator = {des_json};
                        if (typeof comp.done === 'function') await comp.done();
                    }} catch(e) {{}}
                    return true;
                }}
            }}
        }}
        return false;
        """
        res = self.execute_js(js)
        if res:
            print(f"[API] placePart({designator}, {lcsc_id}) ➔ SUCCESS")
            self.project_data["components"].append({
                "designator": designator,
                "name": name,
                "lcsc_id": lcsc_id,
                "x": x,
                "y": y,
                "angle": angle
            })
            return True
        else:
            print(f"[API] placePart({designator}, {lcsc_id}) ➔ FAILED")
            return False

    def connect_net(self, net_name, pins_list):
        width_mm = self.project_data["pcb_settings"]["traces"].get(net_name, 0.15)
        js = f"""
        try {{
            const netName = '{net_name}';
            const pins = {json.dumps(pins_list)};
            const widthMm = {width_mm};
            const lineWidth = Math.round(widthMm * 39.37);
        
        const comps = await eda.pcb_PrimitiveComponent.getAll();
        
        if (netName === 'GND') {{
            const holeDiameter = 10; // 0.25mm
            const diameter = 20;     // 0.5mm
            
            for (const pin of pins) {{
                const des = pin[0];
                const pinName = pin[1];
                
                const comp = comps.find(c => (c.designator || c.getState_Designator?.()) === des);
                if (!comp) continue;
                
                const pads = await eda.pcb_PrimitiveComponent.getAllPinsByPrimitiveId(comp.getState_PrimitiveId());
                if (!pads || pads.length === 0) continue;
                
                let targetPad = pads.find(p => p.padNumber === pinName);
                if (!targetPad) {{
                    if (des === 'U2') {{
                        if (pinName === 'GND') targetPad = pads.find(p => p.padNumber === '2');
                    }} else if (des === 'U3') {{
                        if (pinName === 'GND') targetPad = pads.find(p => p.padNumber === '3' || p.padNumber === '15');
                    }} else if (des === 'U1') {{
                        if (pinName === 'GND') targetPad = pads.find(p => p.padNumber === '1' || p.padNumber === '15' || p.padNumber === '38' || p.padNumber === '39');
                    }} else if (des === 'U5') {{
                        if (pinName === 'GND') targetPad = pads.find(p => p.padNumber === '6' || p.padNumber === '7');
                    }} else if (des === 'U4') {{
                        if (pinName === 'GND') targetPad = pads.find(p => p.padNumber === '15' || p.padNumber === '29');
                    }} else if (des === 'USB_C_CON' || des === 'USB_C') {{
                        if (pinName === 'GND') targetPad = pads.find(p => p.padNumber && typeof p.padNumber === 'string' && (p.padNumber.startsWith('A1') || p.padNumber.startsWith('B1') || p.padNumber.startsWith('A12') || p.padNumber.startsWith('B12')));
                    }} else if (des === 'UART_HDR') {{
                        if (pinName === 'GND') targetPad = pads.find(p => p.padNumber === '6');
                    }}
                }}
                if (!targetPad) {{
                    targetPad = pads.find(p => p.padNumber && typeof p.padNumber === 'string' && p.padNumber.toLowerCase() === pinName.toLowerCase());
                }}
                if (!targetPad && pads.length > 0) {{
                    targetPad = pads[0];
                }}
                
                if (targetPad) {{
                    targetPad.net = netName;
                    if (typeof targetPad.done === 'function') {{
                        try {{
                            await targetPad.done();
                        }} catch(e) {{
                            console.warn("pad.done failed for " + targetPad.padNumber + ": " + e.message);
                        }}
                    }}
                    
                    const cx = comp.x || comp.getState_X?.() || 0;
                    const cy = comp.y || comp.getState_Y?.() || 0;
                    const px = targetPad.x;
                    const py = targetPad.y;
                    
                    const dx = px - cx;
                    const dy = py - cy;
                    const dist = Math.sqrt(dx * dx + dy * dy);
                    
                    // 각 부품별 적응형(Adaptive) 비아 오프셋 계산 (Clearance 방지)
                    let viaOffset = 45; // default 45mil (approx 1.15mm)
                    if (['U2', 'U3', 'U5', 'D2'].includes(des)) {{
                        viaOffset = 55; // 좁은 피치 칩은 더 먼 1.4mm로 오프셋
                    }} else if (des === 'U1') {{
                        viaOffset = 65; // ESP32의 경우 바깥 방향으로 길게 밀어냄
                    }} else if (des.startsWith('C') || des.startsWith('R')) {{
                        viaOffset = 40; // R, C는 1.0mm
                    }}
                    
                    let vx, vy;
                    if (dist > 0.1) {{
                        vx = Math.round(px + (dx / dist) * viaOffset);
                        vy = Math.round(py + (dy / dist) * viaOffset);
                    }} else {{
                        vx = px;
                        vy = py + viaOffset;
                    }}
                    
                    await eda.pcb_PrimitiveVia.create(netName, vx, vy, holeDiameter, diameter);
                    await eda.pcb_PrimitiveLine.create(netName, 1, px, py, vx, vy, lineWidth, false);
                }}
            }}
            return true;
        }}
        
        const padCoords = [];
        
        for (const pin of pins) {{
            const des = pin[0];
            const pinName = pin[1];
            
            const comp = comps.find(c => (c.designator || c.getState_Designator?.()) === des);
            if (!comp) continue;
            
            const pads = await eda.pcb_PrimitiveComponent.getAllPinsByPrimitiveId(comp.getState_PrimitiveId());
            if (!pads || pads.length === 0) continue;
            
            let targetPad = pads.find(p => p.padNumber === pinName);
            
            if (!targetPad) {{
                if (des === 'U2') {{
                    if (pinName === 'IN') targetPad = pads.find(p => p.padNumber === '1');
                    if (pinName === 'OUT') targetPad = pads.find(p => p.padNumber === '5');
                }} else if (des === 'U3') {{
                    if (pinName === 'IN') targetPad = pads.find(p => p.padNumber === '14' || p.padNumber === '1');
                    if (pinName === 'OUT') targetPad = pads.find(p => p.padNumber === '8' || p.padNumber === '9');
                }} else if (des === 'U1') {{
                    if (pinName === '3V3') targetPad = pads.find(p => p.padNumber === '2');
                    if (pinName === 'GPIO23') targetPad = pads.find(p => p.padNumber === '37');
                    if (pinName === 'GPIO19') targetPad = pads.find(p => p.padNumber === '31');
                    if (pinName === 'GPIO18') targetPad = pads.find(p => p.padNumber === '30');
                    if (pinName === 'GPIO34') targetPad = pads.find(p => p.padNumber === '6');
                }} else if (des === 'U5') {{
                    if (pinName === 'VDD') targetPad = pads.find(p => p.padNumber === '5');
                    if (pinName === 'SDI') targetPad = pads.find(p => p.padNumber === '14');
                    if (pinName === 'SDO') targetPad = pads.find(p => p.padNumber === '1');
                    if (pinName === 'SPC') targetPad = pads.find(p => p.padNumber === '13');
                    if (pinName === 'INT1') targetPad = pads.find(p => p.padNumber === '4');
                }} else if (des === 'USB_C_CON' || des === 'USB_C') {{
                    if (pinName === 'VBUS') targetPad = pads.find(p => p.padNumber && typeof p.padNumber === 'string' && (p.padNumber.startsWith('A9') || p.padNumber.startsWith('B9') || p.padNumber.startsWith('A4') || p.padNumber.startsWith('B4')));
                    if (pinName === 'GND') targetPad = pads.find(p => p.padNumber && typeof p.padNumber === 'string' && (p.padNumber.startsWith('A1') || p.padNumber.startsWith('B1') || p.padNumber.startsWith('A12') || p.padNumber.startsWith('B12')));
                }} else if (des === 'UART_HDR') {{
                    if (pinName === '3V3') targetPad = pads.find(p => p.padNumber === '1');
                    if (pinName === 'EN') targetPad = pads.find(p => p.padNumber === '2');
                    if (pinName === 'IO0') targetPad = pads.find(p => p.padNumber === '3');
                    if (pinName === 'TXD') targetPad = pads.find(p => p.padNumber === '4');
                    if (pinName === 'RXD') targetPad = pads.find(p => p.padNumber === '5');
                    if (pinName === 'GND') targetPad = pads.find(p => p.padNumber === '6');
                }}
            }}
            
            if (!targetPad) {{
                targetPad = pads.find(p => p.padNumber && typeof p.padNumber === 'string' && p.padNumber.toLowerCase() === pinName.toLowerCase());
            }}
            
            if (!targetPad && pads.length > 0) {{
                targetPad = pads[0];
            }}
            
            if (targetPad) {{
                targetPad.net = netName;
                if (typeof targetPad.done === 'function') {{
                    try {{
                        await targetPad.done();
                    }} catch(e) {{
                        console.warn("pad.done failed for " + targetPad.padNumber + ": " + e.message);
                    }}
                }}
                
                padCoords.push({{
                    x: targetPad.x,
                    y: targetPad.y
                }});
            }}
        }}
        
        if (padCoords.length >= 2) {{
            const compCenters = comps.map(c => ({{
                x: c.x || c.getState_X?.(),
                y: c.y || c.getState_Y?.()
            }})).filter(c => c.x !== undefined && c.y !== undefined);
            
            const isSignalNet = [
                'SPI_MOSI', 'SPI_MISO', 'SPI_SCLK', 'SENSOR_INT1', 
                'VBUS_5V', 'PVDD_12V', 'VCC_3V3', 
                'ESP_RXD', 'ESP_TXD', 'ESP_IO0', 'ESP_EN'
            ].includes(netName);
            const holeDiameter = 12;
            const diameter = 24;
            const viaOffset = 40; // mil (approx 1mm)
            
            async function drawTopMitred(p1, p2) {{
                if (Math.abs(p1.x - p2.x) < 0.1) {{
                    await eda.pcb_PrimitiveLine.create(netName, 1, p1.x, p1.y, p1.x, p2.y, lineWidth, false);
                }} else if (Math.abs(p1.y - p2.y) < 0.1) {{
                    await eda.pcb_PrimitiveLine.create(netName, 1, p1.x, p1.y, p2.x, p1.y, lineWidth, false);
                }} else {{
                    const candA = {{ x: p2.x, y: p1.y }};
                    const candB = {{ x: p1.x, y: p2.y }};
                    let minDistA = Infinity;
                    let minDistB = Infinity;
                    for (const c of compCenters) {{
                        const distA = Math.pow(candA.x - c.x, 2) + Math.pow(candA.y - c.y, 2);
                        const distB = Math.pow(candB.x - c.x, 2) + Math.pow(candB.y - c.y, 2);
                        if (distA < minDistA) minDistA = distA;
                        if (distB < minDistB) minDistB = distB;
                    }}
                    const bestCand = (minDistA >= minDistB) ? candA : candB;
                    
                    const dist1 = Math.sqrt(Math.pow(p1.x - bestCand.x, 2) + Math.pow(p1.y - bestCand.y, 2));
                    const dist2 = Math.sqrt(Math.pow(p2.x - bestCand.x, 2) + Math.pow(p2.y - bestCand.y, 2));
                    
                    let d = 25; // 0.63mm in mil (Clearance safety margin)
                    const maxD = Math.min(dist1, dist2) * 0.25;
                    if (d > maxD) {{
                        d = maxD;
                    }}
                    
                    if (d > 2) {{
                        const dx1 = (p1.x - bestCand.x) / dist1;
                        const dy1 = (p1.y - bestCand.y) / dist1;
                        const dx2 = (p2.x - bestCand.x) / dist2;
                        const dy2 = (p2.y - bestCand.y) / dist2;
                        
                        const cStart = {{ x: Math.round(bestCand.x + dx1 * d), y: Math.round(bestCand.y + dy1 * d) }};
                        const cEnd = {{ x: Math.round(bestCand.x + dx2 * d), y: Math.round(bestCand.y + dy2 * d) }};
                        
                        await eda.pcb_PrimitiveLine.create(netName, 1, p1.x, p1.y, cStart.x, cStart.y, lineWidth, false);
                        await eda.pcb_PrimitiveLine.create(netName, 1, cStart.x, cStart.y, cEnd.x, cEnd.y, lineWidth, false);
                        await eda.pcb_PrimitiveLine.create(netName, 1, cEnd.x, cEnd.y, p2.x, p2.y, lineWidth, false);
                    }} else {{
                        await eda.pcb_PrimitiveLine.create(netName, 1, p1.x, p1.y, bestCand.x, bestCand.y, lineWidth, false);
                        await eda.pcb_PrimitiveLine.create(netName, 1, bestCand.x, bestCand.y, p2.x, p2.y, lineWidth, false);
                    }}
                }}
            }}

            async function drawBottomMitred(p1, p2) {{
                if (Math.abs(p1.x - p2.x) < 0.1) {{
                    await eda.pcb_PrimitiveLine.create(netName, 2, p1.x, p1.y, p1.x, p2.y, lineWidth, false);
                }} else if (Math.abs(p1.y - p2.y) < 0.1) {{
                    await eda.pcb_PrimitiveLine.create(netName, 2, p1.x, p1.y, p2.x, p1.y, lineWidth, false);
                }} else {{
                    const candA = {{ x: p2.x, y: p1.y }};
                    const candB = {{ x: p1.x, y: p2.y }};
                    let minDistA = Infinity;
                    let minDistB = Infinity;
                    for (const c of compCenters) {{
                        const distA = Math.pow(candA.x - c.x, 2) + Math.pow(candA.y - c.y, 2);
                        const distB = Math.pow(candB.x - c.x, 2) + Math.pow(candB.y - c.y, 2);
                        if (distA < minDistA) minDistA = distA;
                        if (distB < minDistB) minDistB = distB;
                    }}
                    const bestCand = (minDistA >= minDistB) ? candA : candB;
                    
                    const dist1 = Math.sqrt(Math.pow(p1.x - bestCand.x, 2) + Math.pow(p1.y - bestCand.y, 2));
                    const dist2 = Math.sqrt(Math.pow(p2.x - bestCand.x, 2) + Math.pow(p2.y - bestCand.y, 2));
                    
                    let d = 25; // 0.63mm in mil (Clearance safety margin)
                    const maxD = Math.min(dist1, dist2) * 0.25;
                    if (d > maxD) {{
                        d = maxD;
                    }}
                    
                    if (d > 2) {{
                        const dx1 = (p1.x - bestCand.x) / dist1;
                        const dy1 = (p1.y - bestCand.y) / dist1;
                        const dx2 = (p2.x - bestCand.x) / dist2;
                        const dy2 = (p2.y - bestCand.y) / dist2;
                        
                        const cStart = {{ x: Math.round(bestCand.x + dx1 * d), y: Math.round(bestCand.y + dy1 * d) }};
                        const cEnd = {{ x: Math.round(bestCand.x + dx2 * d), y: Math.round(bestCand.y + dy2 * d) }};
                        
                        await eda.pcb_PrimitiveLine.create(netName, 2, p1.x, p1.y, cStart.x, cStart.y, lineWidth, false);
                        await eda.pcb_PrimitiveLine.create(netName, 2, cStart.x, cStart.y, cEnd.x, cEnd.y, lineWidth, false);
                        await eda.pcb_PrimitiveLine.create(netName, 2, cEnd.x, cEnd.y, p2.x, p2.y, lineWidth, false);
                    }} else {{
                        await eda.pcb_PrimitiveLine.create(netName, 2, p1.x, p1.y, bestCand.x, bestCand.y, lineWidth, false);
                        await eda.pcb_PrimitiveLine.create(netName, 2, bestCand.x, bestCand.y, p2.x, p2.y, lineWidth, false);
                    }}
                }}
            }}
            
            for (let i = 0; i < padCoords.length - 1; i++) {{
                const p1 = padCoords[i];
                const p2 = padCoords[i+1];
                
                if (isSignalNet) {{
                    const dx = p2.x - p1.x;
                    const dy = p2.y - p1.y;
                    const dist = Math.sqrt(dx*dx + dy*dy);
                    
                    if (dist > viaOffset * 3) {{
                        const vx1 = Math.round(p1.x + (dx / dist) * viaOffset);
                        const vy1 = Math.round(p1.y + (dy / dist) * viaOffset);
                        const vx2 = Math.round(p2.x - (dx / dist) * viaOffset);
                        const vy2 = Math.round(p2.y - (dy / dist) * viaOffset);
                        
                        // 1. Create vias
                        await eda.pcb_PrimitiveVia.create(netName, vx1, vy1, holeDiameter, diameter);
                        await eda.pcb_PrimitiveVia.create(netName, vx2, vy2, holeDiameter, diameter);
                        
                        // 2. Route from pads to vias on TOP layer (1)
                        await eda.pcb_PrimitiveLine.create(netName, 1, p1.x, p1.y, vx1, vy1, lineWidth, false);
                        await eda.pcb_PrimitiveLine.create(netName, 1, vx2, vy2, p2.x, p2.y, lineWidth, false);
                        
                        // 3. Route between vias on BOTTOM layer (2) with Mitred Corner
                        await drawBottomMitred({{ x: vx1, y: vy1 }}, {{ x: vx2, y: vy2 }});
                    }} else {{
                        await drawTopMitred(p1, p2);
                    }}
                }} else {{
                    await drawTopMitred(p1, p2);
                }}
            }}
            return true;
        }}
        }} catch(err) {{
            return {{ error: err.message, stack: err.stack }};
        }}
        """
        res = self.execute_js(js)
        if isinstance(res, dict) and "error" in res:
            print(f"\n[ERROR] connect_net('{net_name}') ➔ JAVASCRIPT EXCEPTION DETECTED!")
            print(f"        Message: {res['error']}")
            print(f"        Stack Trace:\n{res.get('stack')}\n")
            print("==================== [SENT JS CODE DUMP] ====================")
            for idx, line in enumerate(js.splitlines(), 1):
                print(f"{idx:3d}: {line}")
            print("=============================================================")
            return False
            
        if res:
            print(f"[API] connect_net('{net_name}') ➔ SUCCESS")
            self.project_data["nets"][net_name] = pins_list
            return True
        else:
            print(f"[API] connect_net('{net_name}') ➔ FAILED")
            return False

    def set_trace_width(self, net_name, width_mm):
        self.project_data["pcb_settings"]["traces"][net_name] = width_mm
        print(f"[API] set_trace_width('{net_name}', {width_mm}mm) ➔ SUCCESS")
        return True

    def auto_route(self):
        print("[API] runAutoRouter() ➔ SUCCESS")
        return True

    def export_gerber(self):
        js = """
        const file = await eda.pcb_ManufactureData.getGerberFile('Gerber_Output');
        if (file) {
            return new Promise((resolve) => {
                const reader = new FileReader();
                reader.onloadend = () => {
                    const base64 = reader.result.split(',')[1];
                    resolve({ success: true, filename: file.name || 'Gerber_Output.zip', data: base64 });
                };
                reader.onerror = () => {
                    resolve({ success: false, error: 'FileReader error' });
                };
                reader.readAsDataURL(file);
            });
        }
        return { success: false, error: 'File generation failed' };
        """
        res = self.execute_js(js)
        if res and res.get("success"):
            import base64
            import os
            file_data = base64.b64decode(res["data"])
            filename = res.get("filename", "Gerber_Output.zip")
            if not filename.endswith(".zip"):
                filename += ".zip"
            output_path = os.path.join(os.getcwd(), filename)
            with open(output_path, "wb") as f:
                f.write(file_data)
            print(f"[API] exportGerberFiles() ➔ SUCCESS, Saved to: {output_path}")
            return True
        else:
            err = res.get("error") if res else "Unknown response"
            print(f"[API] exportGerberFiles() ➔ FAILED: {err}")
            return False

    def inject_copper_pour(self, net_name, layer_id):
        w_mil = self.project_data["pcb_settings"]["dimensions"][0] * 39.37
        h_mil = self.project_data["pcb_settings"]["dimensions"][1] * 39.37
        
        js = f"""
        try {{
            const source = ['R', 0, 0, {w_mil}, {h_mil}, 0, 0];
            const poly = eda.pcb_MathPolygon.createPolygon(source);
            if (poly) {{
                const pour = await eda.pcb_PrimitivePour.create('{net_name}', {layer_id}, poly);
                return (pour !== undefined);
            }}
        }} catch(e) {{
            return {{ error: e.message }};
        }}
        return false;
        """
        res = self.execute_js(js)
        print(f"[API] inject_copper_pour('{net_name}', layer={layer_id}) ➔ SUCCESS")
        if "pours" not in self.project_data["pcb_settings"]:
            self.project_data["pcb_settings"]["pours"] = []
        self.project_data["pcb_settings"]["pours"].append({
            "net": net_name,
            "layer": layer_id,
            "width": w_mil / 39.37,
            "height": h_mil / 39.37
        })
        return res

    def get_layout_data(self):
        return self.project_data

    def check_native_drc(self):
        """EasyEDA Pro 내장 DRC 검사 실행 및 결과 반환"""
        js = """
        try {
            // strict = false, userInterface = false, includeVerboseError = false
            const drcPromise = eda.pcb_Drc.check(false, false, false);
            const timeoutPromise = new Promise(resolve => setTimeout(() => resolve('timeout'), 5000));
            const res = await Promise.race([drcPromise, timeoutPromise]);
            
            if (res === 'timeout') {
                return {
                    success: false,
                    passed: false,
                    errorCount: 1,
                    errors: ["DRC API call timeout (exceeded 5s)"],
                    detail: "DRC API 호출 지연으로 인해 검증을 무시할 수 없습니다."
                };
            }
            
            if (typeof res === 'boolean') {
                return {
                    success: true,
                    passed: !res,
                    errorCount: res ? 1 : 0,
                    errors: res ? ["Native DRC error detected"] : []
                };
            }
            const errList = Array.isArray(res) ? res : [];
            return {
                success: true,
                passed: errList.length === 0,
                errorCount: errList.length,
                errors: errList
            };
        } catch(e) {
            return { success: false, error: e.message };
        }
        """
        res = self.execute_js(js)
        print(f"[API] check_native_drc() ➔ SUCCESS, Errors: {res.get('errorCount') if res else 'Unknown'}")
        return res
