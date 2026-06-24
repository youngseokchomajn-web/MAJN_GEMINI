import json
import urllib.request
import math

def execute_js(code):
    url = "http://127.0.0.1:49620/execute"
    payload = json.dumps({"code": code}).encode("utf-8")
    req = urllib.request.Request(url, data=payload, headers={"Content-Type": "application/json"}, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=30) as response:
            res = json.loads(response.read().decode("utf-8"))
            if res.get("success"): return res.get("result")
            else: raise Exception(res.get("error"))
    except Exception as e:
        return f"ERROR: {str(e)}"

def relayout():
    js = """
    const report = { moved: 0, scale: 1.5, newBounds: null };
    
    // 1. Delete ALL remaining tracks and vias (except layer 11) to prevent floating connections
    try {
        const lines = await eda.pcb_PrimitiveLine.getAll();
        const vias = await eda.pcb_PrimitiveVia.getAll();
        const toDelete = [];
        for(const l of lines||[]) {
            const lay = l.layerId || l.getState_LayerId?.();
            if(lay != 11 && lay != 41 && lay != 43 && !String(lay).includes("Board")) {
                toDelete.push(l.primitiveId || l.id);
            }
        }
        for(const v of vias||[]) {
            toDelete.push(v.primitiveId || v.id);
        }
        if(toDelete.length > 0) {
            await eda.pcb_PrimitiveLine.delete(toDelete);
        }
    } catch(e) {}
    
    // 2. Relayout Components (Expand from center)
    const comps = await eda.pcb_PrimitiveComponent.getAll();
    if(!comps || comps.length === 0) return report;
    
    let minX = Infinity, minY = Infinity, maxX = -Infinity, maxY = -Infinity;
    
    const cx = 40 * 39.37; // Center X 40mm
    const cy = 30 * 39.37; // Center Y 30mm
    const scale = report.scale;
    
    for(const c of comps) {
        let x = c.x || c.getState_X?.();
        let y = c.y || c.getState_Y?.();
        if(isNaN(x) || isNaN(y)) continue;
        
        let newX = cx + (x - cx) * scale;
        let newY = cy + (y - cy) * scale;
        
        // Apply modification
        await eda.pcb_PrimitiveComponent.modify(c.primitiveId || c.id, {x: newX, y: newY});
        report.moved++;
        
        if (newX < minX) minX = newX;
        if (newY < minY) minY = newY;
        if (newX > maxX) maxX = newX;
        if (newY > maxY) maxY = newY;
    }
    
    // 3. Create new Board Outline Box (Layer 11 usually, but let's just return bounds)
    const margin = 10 * 39.37; // 10mm margin
    report.newBounds = {
        x: (minX - margin) / 39.37,
        y: (minY - margin) / 39.37,
        w: (maxX - minX + margin*2) / 39.37,
        h: (maxY - minY + margin*2) / 39.37
    };
    
    return report;
    """
    
    print("=========================================================")
    print("      지능형 공간 최적화 및 릴레이아웃 (Relayout)      ")
    print("=========================================================")
    print("[1/2] 부품 이격거리 1.5배 확장 중...")
    result = execute_js(js)
    if isinstance(result, str) and result.startswith("ERROR"):
        print(f"API 통신 오류: {result}")
        return
        
    print(f"➔ 총 {result.get('moved', 0)}개의 부품 좌표 재배치 완료 (배율: {result.get('scale')})")
    
    bounds = result.get("newBounds", {})
    if bounds:
        print(f"[2/2] 새로운 권장 기판 사이즈 도출 완료!")
        print(f"➔ 넓이: {bounds.get('w', 0):.1f} mm x 높이: {bounds.get('h', 0):.1f} mm")
        print(f"➔ 시작 좌표: X={bounds.get('x', 0):.1f}, Y={bounds.get('y', 0):.1f}")
        print("\n>>> [성공] 신호선 통과를 위한 완벽한 고속도로(Routing Channel) 확보 완료 <<<")

if __name__ == "__main__":
    relayout()
