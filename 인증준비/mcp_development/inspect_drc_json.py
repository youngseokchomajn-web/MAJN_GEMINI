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
    let rules = [];
    if (eda.pcb_Drc && eda.pcb_Drc.getNetRules) {
        rules = await eda.pcb_Drc.getNetRules();
    }
    
    // Look for methods to save
    let methods = [];
    if (eda.pcb_Drc) {
        for (let k in eda.pcb_Drc) {
            methods.push(k);
        }
    }
    
    return { rules: rules, methods: methods };
} catch(e) { return { error: e.message }; }
"""
print(json.dumps(execute_js(JS), indent=2))
