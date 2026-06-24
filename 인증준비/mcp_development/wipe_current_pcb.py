import json
import urllib.request

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
    let result = [];
    
    let allComps = await eda.pcb_PrimitiveComponent.getAll();
    if (allComps && allComps.length > 0) {
        let ids = allComps.map(c => c.getState_PrimitiveId ? c.getState_PrimitiveId() : (c.id || c.primitiveId)).filter(Boolean);
        if (ids.length > 0) {
            await eda.pcb_PrimitiveComponent.delete(ids);
            result.push("Deleted " + ids.length + " components.");
        }
    }
    
    let allLines = await eda.pcb_PrimitiveLine.getAll();
    if (allLines && allLines.length > 0) {
        let ids = allLines.map(c => c.getState_PrimitiveId ? c.getState_PrimitiveId() : (c.id || c.primitiveId)).filter(Boolean);
        if (ids.length > 0) {
            await eda.pcb_PrimitiveLine.delete(ids);
            result.push("Deleted " + ids.length + " lines/tracks.");
        }
    }
    
    let allRegions = await eda.pcb_PrimitiveRegion.getAll();
    if (allRegions && allRegions.length > 0) {
        let ids = allRegions.map(c => c.getState_PrimitiveId ? c.getState_PrimitiveId() : (c.id || c.primitiveId)).filter(Boolean);
        if (ids.length > 0) {
            await eda.pcb_PrimitiveRegion.delete(ids);
            result.push("Deleted " + ids.length + " regions.");
        }
    }
    
    return { status: "Wiped", log: result };
} catch(e) { return { error: e.message }; }
"""
print(json.dumps(execute_js(JS), indent=2))
