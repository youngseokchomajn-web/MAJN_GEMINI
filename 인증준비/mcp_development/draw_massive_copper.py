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
    // A massive rectangle that covers everything. EasyEDA automatically clips to board outline.
    let minX = -1000, minY = -1000, maxX = 15000, maxY = 15000;
    
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
    
    // Attempt to trigger rebuild automatically
    if (eda.sys_Command && eda.sys_Command.hasCommand("pcb_rebuildAllCopper")) {
        eda.sys_Command.execute("pcb_rebuildAllCopper");
    }
    
    return { status: "Success" };
} catch(e) { return { error: e.message }; }
"""
print(json.dumps(execute_js(JS), indent=2))
