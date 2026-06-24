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
            if (n.name === "GND") gndId = n.primitiveId;
        }
    }

    let viaObj = {
        primitiveType: "Via",
        net: gndId,
        x: 6000,
        y: 3000,
        holeDiameter: 12,
        diameter: 24,
        viaType: 0
    };
    
    let lineObj = {
        primitiveType: "Line",
        net: gndId,
        layer: 1,
        startX: 6000,
        startY: 3000,
        endX: 6100,
        endY: 3000,
        lineWidth: 10
    };
    
    await eda.pcb_PrimitiveVia.create([viaObj]);
    await eda.pcb_PrimitiveLine.create([lineObj]);
    
    return { status: "Created successfully!" };
} catch(e) { return { error: e.message }; }
"""
print(json.dumps(execute_js(JS), indent=2))
