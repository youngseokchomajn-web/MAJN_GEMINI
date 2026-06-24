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
    let drcRes = await eda.pcb_Drc.check(false, false, true);
    let summary = {};
    let totalErrors = 0;
    
    if (drcRes && Array.isArray(drcRes)) {
        for (let cat of drcRes) {
            let catName = cat.name;
            let list = cat.list || [];
            if (list.length > 0) {
                summary[catName] = list.length;
                totalErrors += list.length;
            }
        }
    }
    return { status: "Success", total: totalErrors, breakdown: summary };
} catch(e) { return { error: e.message }; }
"""
print(json.dumps(execute_js(JS), indent=2))
