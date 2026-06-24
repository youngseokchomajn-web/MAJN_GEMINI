import json, urllib.request

def execute_js(code):
    url = "http://127.0.0.1:49620/execute"
    payload = json.dumps({"code": code}).encode("utf-8")
    req = urllib.request.Request(url, data=payload, headers={"Content-Type": "application/json"}, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=90) as response:
            res = json.loads(response.read().decode("utf-8"))
            if res.get("success"): return res.get("result")
            return {"error": res.get("error")}
    except Exception as e:
        return {"error": str(e)}

JS = """
try {
    // 1. Get Board Outline to know the dimensions
    let outlines = await eda.pcb_PrimitiveBoardOutline.getAll();
    let minX = 100000, minY = 100000, maxX = -100000, maxY = -100000;
    
    if (outlines && outlines.length > 0) {
        for (let o of outlines) {
            let pts = o.pointArr || [];
            for (let pt of pts) {
                if (pt.x < minX) minX = pt.x;
                if (pt.y < minY) minY = pt.y;
                if (pt.x > maxX) maxX = pt.x;
                if (pt.y > maxY) maxY = pt.y;
            }
        }
    }
    
    // Fallback if no outline found
    if (minX === 100000) {
        minX = 1800; minY = 1800;
        maxX = 7600; maxY = 5200;
    }
    
    // Add a small margin
    let margin = 5;
    minX -= margin; minY -= margin;
    maxX += margin; maxY += margin;
    
    // Create Top and Bottom Copper Regions for GND
    let topCopper = {
        primitiveType: "CopperRegion",
        layer: 1, // Top
        net: "GND",
        pointArr: [
            { x: minX, y: minY },
            { x: maxX, y: minY },
            { x: maxX, y: maxY },
            { x: minX, y: maxY },
            { x: minX, y: minY }
        ]
    };
    
    let bottomCopper = {
        primitiveType: "CopperRegion",
        layer: 2, // Bottom
        net: "GND",
        pointArr: [
            { x: minX, y: minY },
            { x: maxX, y: minY },
            { x: maxX, y: maxY },
            { x: minX, y: maxY },
            { x: minX, y: minY }
        ]
    };
    
    await eda.pcb_PrimitiveCopperRegion.create([topCopper, bottomCopper]);
    return { status: "Success", minX, minY, maxX, maxY };
} catch(e) { return { error: e.message }; }
"""
print(json.dumps(execute_js(JS), indent=2))
