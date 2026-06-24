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
    let allVias = await eda.pcb_PrimitiveVia.getAll();
    
    let lineIds = [];
    if (allLines) {
        for (let l of allLines) {
            // Check if line is locked. Only delete unlocked lines.
            let locked = l.primitiveLock;
            if (!locked) {
                let id = l.getState_PrimitiveId ? l.getState_PrimitiveId() : l.primitiveId;
                if (id) lineIds.push(id);
            }
        }
    }
    
    let viaIds = [];
    if (allVias) {
        for (let v of allVias) {
            let locked = v.primitiveLock;
            if (!locked) {
                let id = v.getState_PrimitiveId ? v.getState_PrimitiveId() : v.primitiveId;
                if (id) viaIds.push(id);
            }
        }
    }
    
    if (lineIds.length > 0) await eda.pcb_PrimitiveLine.delete(lineIds);
    if (viaIds.length > 0) await eda.pcb_PrimitiveVia.delete(viaIds);
    
    return { deletedLines: lineIds.length, deletedVias: viaIds.length };
} catch(e) { return { error: e.message }; }
"""
print(json.dumps(execute_js(JS), indent=2))
