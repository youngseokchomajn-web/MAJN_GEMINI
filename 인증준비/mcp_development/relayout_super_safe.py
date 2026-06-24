import json
import urllib.request

def execute_js(code):
    url = "http://127.0.0.1:49620/execute"
    payload = json.dumps({"code": code}).encode("utf-8")
    req = urllib.request.Request(url, data=payload, headers={"Content-Type": "application/json"}, method="POST")
    with urllib.request.urlopen(req, timeout=30) as response:
        res = json.loads(response.read().decode("utf-8"))
        if res.get("success"): return res.get("result")
        else: raise Exception(res.get("error"))

def relayout_super_safe():
    js = """
    // 1. Delete all tracks
    try {
        const lines = await eda.pcb_PrimitiveLine.getAll();
        const vias = await eda.pcb_PrimitiveVia.getAll();
        const toDelete = [];
        for(const l of lines||[]) {
            const lay = l.layerId || l.getState_LayerId?.();
            if(lay != 11 && !String(lay).includes("Board")) toDelete.push(l.primitiveId||l.id);
        }
        for(const v of vias||[]) toDelete.push(v.primitiveId||v.id);
        if(toDelete.length > 0) await eda.pcb_PrimitiveLine.delete(toDelete);
    } catch(e){}
    
    // 2. Get components and calculate center
    const comps = await eda.pcb_PrimitiveComponent.getAll();
    if(!comps || comps.length===0) return;
    
    let minX=Infinity, minY=Infinity, maxX=-Infinity, maxY=-Infinity;
    for(const c of comps) {
        let x=c.x||c.getState_X?.(), y=c.y||c.getState_Y?.();
        if(isNaN(x)||isNaN(y)) continue;
        if(x<minX)minX=x; if(y<minY)minY=y;
        if(x>maxX)maxX=x; if(y>maxY)maxY=y;
    }
    
    const cx = (minX + maxX)/2;
    const cy = (minY + maxY)/2;
    const scale = 1.3;
    const shiftX = 30 * 39.37; // +30mm
    const shiftY = 30 * 39.37; // +30mm
    
    let newMinX=Infinity, newMinY=Infinity, newMaxX=-Infinity, newMaxY=-Infinity;
    
    for(const c of comps) {
        let x=c.x||c.getState_X?.(), y=c.y||c.getState_Y?.();
        if(isNaN(x)||isNaN(y)) continue;
        
        let newX = cx + (x - cx) * scale + shiftX;
        let newY = cy + (y - cy) * scale + shiftY;
        
        await eda.pcb_PrimitiveComponent.modify(c.primitiveId||c.id, {x: newX, y: newY});
        
        if(newX<newMinX)newMinX=newX; if(newY<newMinY)newMinY=newY;
        if(newX>newMaxX)newMaxX=newX; if(newY>newMaxY)newMaxY=newY;
    }
    
    return {
        x: newMinX/39.37, y: newMinY/39.37,
        w: (newMaxX-newMinX)/39.37, h: (newMaxY-newMinY)/39.37
    };
    """
    bounds = execute_js(js)
    print("Super Safe Relayout Completed!")
    print(f"New Bounds: X={bounds.get('x'):.1f}mm, Y={bounds.get('y'):.1f}mm")
    print(f"Size: {bounds.get('w'):.1f}mm x {bounds.get('h'):.1f}mm")

if __name__ == "__main__":
    relayout_super_safe()
