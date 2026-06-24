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
    let pads = await eda.pcb_PrimitivePad.getAll();
    if (pads && pads.length > 0) {
        let p = pads[0];
        let props = {};
        for (let k in p) {
            if (typeof p[k] !== 'function') props[k] = p[k];
        }
        return { count: pads.length, sampleProps: props };
    }
    return { count: 0 };
} catch(e) { return { error: e.message }; }
"""
print(json.dumps(execute_js(JS), indent=2))
