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
    let hasTrack = typeof eda.pcb_PrimitiveTrack !== "undefined";
    let hasTrackGet = hasTrack && typeof eda.pcb_PrimitiveTrack.getAll === "function";
    
    // Actually, in EasyEDA, lines are 'pcb_PrimitiveLine' but tracks are sometimes just Lines that belong to a net.
    // Let's dump the primitive ID of some lines to see if they match the 'e...' IDs.
    let lines = await eda.pcb_PrimitiveLine.getAll();
    let sampleLines = lines ? lines.slice(0,3).map(l => l.getState_PrimitiveId ? l.getState_PrimitiveId() : l.primitiveId) : [];
    
    // What if the ID is just internal and we need to use `eda.pcb_Command` or `eda.dmt_EditorControl` to delete?
    return { hasTrack, hasTrackGet, sampleLines };
} catch(e) { return { error: e.message }; }
"""
print(json.dumps(execute_js(JS), indent=2))
