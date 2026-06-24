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
    let nets = await eda.pcb_PrimitiveNet.getAll();
    let gndId = "GND";
    if (nets) {
        for (let n of nets) {
            if (n.name === "GND") {
                gndId = n.primitiveId;
                break;
            }
        }
    }
    
    // Attempt create with exact parameters
    let minX = 1800, minY = 1800, maxX = 7600, maxY = 5200;
    
    let pour = {
        primitiveType: "Pour",
        layer: 1,
        net: gndId, // use the exact UUID
        pathStr: `M ${minX} ${minY} L ${maxX} ${minY} L ${maxX} ${maxY} L ${minX} ${maxY} Z`,
        fillType: 0,
        lineWidth: 0.254,
        clearance: 0.254
    };
    
    try {
        await eda.pcb_PrimitivePour.create([pour]);
        return { status: "Success pathStr", gndId };
    } catch(e) {
        // try pointArr
        pour.pointArr = [
            { x: minX, y: minY },
            { x: maxX, y: minY },
            { x: maxX, y: maxY },
            { x: minX, y: maxY },
            { x: minX, y: minY }
        ];
        delete pour.pathStr;
        try {
            await eda.pcb_PrimitivePour.create([pour]);
            return { status: "Success pointArr", gndId };
        } catch(e2) {
            return { error: e2.message };
        }
    }
} catch(e) { return { error: e.message }; }
"""
print(json.dumps(execute_js(JS), indent=2))
