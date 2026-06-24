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
    let region = await eda.pcb_PrimitiveRegion.create({
        "layerId": "97",
        "pathStr": "M 0 0 L 1000 0 L 1000 1000 L 0 1000 Z",
        "lineWidth": 10
    });
    return { status: "Outline created" };
} catch(e) { return { error: e.message }; }
"""
print(execute_js(JS))
