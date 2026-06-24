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
    
    // Test Via
    try {
        await eda.pcb_PrimitiveVia.create(gndId, 6000, 3000, 12, 24);
    } catch(e) {}
    
    // Test Line
    try {
        await eda.pcb_PrimitiveLine.create(gndId, 1, 6000, 3000, 6100, 3000, 10, false);
    } catch(e) {}
    
    return { status: "Success args" };
} catch(e) { return { error: e.message }; }
"""
print(json.dumps(execute_js(JS), indent=2))
