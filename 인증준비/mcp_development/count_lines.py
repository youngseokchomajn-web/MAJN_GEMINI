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
    let allLines = await eda.pcb_PrimitiveLine.getAll();
    let lockedCount = 0;
    let unlockedCount = 0;
    if (allLines) {
        for (let l of allLines) {
            if (l.primitiveLock) lockedCount++;
            else unlockedCount++;
        }
    }
    return { lockedLines: lockedCount, unlockedLines: unlockedCount };
} catch(e) { return { error: e.message }; }
"""
print(json.dumps(execute_js(JS), indent=2))
