import json
import urllib.request

def execute_js(code):
    url = "http://127.0.0.1:49620/execute"
    payload = json.dumps({"code": code}).encode("utf-8")
    req = urllib.request.Request(url, data=payload, headers={"Content-Type": "application/json"}, method="POST")
    with urllib.request.urlopen(req, timeout=45) as response:
        res = json.loads(response.read().decode("utf-8"))
        if res.get("success"): return res.get("result")
        return {"error": res.get("error")}

JS = """
try {
    const pours = await eda.pcb_PrimitivePour.getAll();
    if (pours && pours.length > 0) {
        await eda.pcb_PrimitivePour.rebuild(pours.map(p => p.id || p.primitiveId).filter(Boolean));
        return "Rebuilt " + pours.length + " copper pours.";
    }
    return "No copper pours found.";
} catch(e) {
    return e.message;
}
"""
print(execute_js(JS))
