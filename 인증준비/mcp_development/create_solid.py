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
    let topFill = {
        primitiveType: "Fill", // Try Fill!
        layer: 1, 
        net: "GND",
        pathStr: "M 1000 1000 L 9000 1000 L 9000 9000 L 1000 9000 Z"
    };
    
    let botFill = {
        primitiveType: "Fill",
        layer: 2, 
        net: "GND",
        pathStr: "M 1000 1000 L 9000 1000 L 9000 9000 L 1000 9000 Z"
    };
    
    if (eda.pcb_PrimitiveFill && eda.pcb_PrimitiveFill.create) {
        await eda.pcb_PrimitiveFill.create([topFill, botFill]);
        return { status: "Success Fill" };
    }
    
    return { error: "No Fill create method" };
} catch(e) { return { error: e.message }; }
"""
print(json.dumps(execute_js(JS), indent=2))
