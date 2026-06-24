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
    let result = {};
    
    // Get a sample Via
    let vias = await eda.pcb_PrimitiveVia.getAll();
    if (vias && vias.length > 0) {
        let v = vias[0];
        let props = {};
        for (let k in v) {
            if (typeof v[k] !== 'function') props[k] = v[k];
        }
        result.sampleVia = props;
    }
    
    // Get a sample Track
    let lines = await eda.pcb_PrimitiveLine.getAll();
    if (lines && lines.length > 0) {
        let l = lines[0];
        let props = {};
        for (let k in l) {
            if (typeof l[k] !== 'function') props[k] = l[k];
        }
        result.sampleLine = props;
    }
    
    return result;
} catch(e) { return { error: e.message }; }
"""
print(json.dumps(execute_js(JS), indent=2))
