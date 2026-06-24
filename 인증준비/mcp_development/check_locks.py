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
    let lines = await eda.pcb_PrimitiveLine.getAll();
    let vias = await eda.pcb_PrimitiveVia.getAll();
    
    let unlockedLines = 0;
    let unlockedVias = 0;
    
    if (lines) {
        for (let l of lines) {
            if (l.primitiveLock === false || l.primitiveLock === undefined) unlockedLines++;
        }
    }
    
    if (vias) {
        for (let v of vias) {
            if (v.primitiveLock === false || v.primitiveLock === undefined) unlockedVias++;
        }
    }
    
    return { status: "Success", unlockedLines, unlockedVias };
} catch(e) { return { error: e.message }; }
"""
print(json.dumps(execute_js(JS), indent=2))
