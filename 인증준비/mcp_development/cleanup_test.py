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
    let allComps = await eda.pcb_PrimitiveComponent.getAll();
    let deletedCount = 0;
    if (allComps && Array.isArray(allComps)) {
        let justPlaced = allComps.filter(c => ["TYPE_C", "SOP16", "C1", "C2"].includes(c.designator || (typeof c.getState_Designator === 'function' ? c.getState_Designator() : '')));
        if (justPlaced.length > 0) {
            let ids = justPlaced.map(c => typeof c.getState_PrimitiveId === 'function' ? c.getState_PrimitiveId() : (c.primitiveId || c.id));
            if (ids.length > 0 && ids[0]) {
                await eda.pcb_PrimitiveComponent.delete(ids);
                deletedCount = justPlaced.length;
            }
        }
    }
    
    return { status: "Cleanup finished", deleted_count: deletedCount };
} catch(e) { return { error: e.message }; }
"""
print(json.dumps(execute_js(JS), indent=2))
