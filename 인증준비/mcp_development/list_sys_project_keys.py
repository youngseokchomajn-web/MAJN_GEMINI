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
    let keys = [];
    if (eda && eda.sys_Project) {
        keys = Object.keys(eda.sys_Project);
    }
    let dmt_keys = [];
    if (eda && eda.dmt_Project) {
        dmt_keys = Object.keys(eda.dmt_Project);
    }
    return { sys_Project: keys, dmt_Project: dmt_keys };
} catch(e) { return { error: e.message }; }
"""
print(json.dumps(execute_js(JS), indent=2))
