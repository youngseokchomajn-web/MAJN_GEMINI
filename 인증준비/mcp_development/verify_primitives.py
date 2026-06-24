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
    let allTracks = eda.pcb_PrimitiveLine.getAll();
    let trackCount = allTracks ? allTracks.length : 0;
    
    let allVias = eda.pcb_PrimitiveVia.getAll();
    let viaCount = allVias ? allVias.length : 0;
    
    return {tracks: trackCount, vias: viaCount};
} catch(e) { return e.message; }
"""
print(execute_js(JS))
