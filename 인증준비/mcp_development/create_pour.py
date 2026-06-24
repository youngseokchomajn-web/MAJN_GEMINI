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
    let minX = -1000, minY = -1000, maxX = 15000, maxY = 15000;
    
    let topPour = {
        primitiveType: "Pour",
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
    
    let bottomPour = {
        primitiveType: "Pour",
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
    
    if (eda.pcb_PrimitivePour && eda.pcb_PrimitivePour.create) {
        await eda.pcb_PrimitivePour.create([topPour, bottomPour]);
    } else if (eda.pcb_PrimitiveRegion && eda.pcb_PrimitiveRegion.create) {
        // sometimes it is 'Region' with type 'Copper'
        topPour.primitiveType = "Region";
        topPour.type = "Copper";
        bottomPour.primitiveType = "Region";
        bottomPour.type = "Copper";
        await eda.pcb_PrimitiveRegion.create([topPour, bottomPour]);
    } else {
        return { error: "No create method found on Pour or Region" };
    }
    
    // Rebuild Copper
    if (eda.sys_Command && eda.sys_Command.hasCommand("pcb_rebuildAllCopper")) {
        eda.sys_Command.execute("pcb_rebuildAllCopper");
    } else if (eda.sys_Command && eda.sys_Command.hasCommand("pcb_rebuildCopper")) {
        eda.sys_Command.execute("pcb_rebuildCopper");
    }
    
    return { status: "Success" };
} catch(e) { return { error: e.message }; }
"""
print(json.dumps(execute_js(JS), indent=2))
