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
    let tracks = eda.pcb_PrimitiveLine.getAll();
    let trackCount = tracks ? tracks.length : 0;
    
    let vias = eda.pcb_PrimitiveVia.getAll();
    let viaCount = vias ? vias.length : 0;
    
    return { trackCount: trackCount, viaCount: viaCount };
} catch(e) { return e.message; }
"""
res = execute_js(JS)
print(f"Track count: {res.get('trackCount')}")
print(f"Via count: {res.get('viaCount')}")
