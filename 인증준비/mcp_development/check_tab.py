import json
import urllib.request
def execute_js(code):
    url = "http://127.0.0.1:49620/execute"
    payload = json.dumps({"code": code}).encode("utf-8")
    req = urllib.request.Request(url, data=payload, headers={"Content-Type": "application/json"}, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=45) as response:
            res = json.loads(response.read().decode("utf-8"))
            if res.get("success"): return res.get("result")
            return {"error": res.get("error")}
    except Exception as e:
        return {"error": str(e)}

JS = """
try {
    let title = document.title;
    let trackCount = 0;
    if (eda && eda.pcb_PrimitiveLine) {
        let tracks = eda.pcb_PrimitiveLine.getAllPrimitiveId();
        if (tracks) trackCount = tracks.length;
    }
    return { title: title, trackCount: trackCount };
} catch(e) { return e.message; }
"""
print(execute_js(JS))
