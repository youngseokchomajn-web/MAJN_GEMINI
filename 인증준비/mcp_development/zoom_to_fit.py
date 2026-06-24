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
    // Zoom to fit all objects
    if (eda.pcb_View && eda.pcb_View.fitAllObjects) {
        await eda.pcb_View.fitAllObjects();
    }
    
    // Select the components to make them glow
    let allComps = await eda.pcb_PrimitiveComponent.getAll();
    if (allComps && allComps.length > 0) {
        let ids = allComps.map(c => c.getState_PrimitiveId ? c.getState_PrimitiveId() : (c.id || c.primitiveId)).filter(Boolean);
        await eda.pcb_SelectControl.selectPrimitives(ids);
    }
    
    return { status: "Zoomed and Selected" };
} catch(e) { return { error: e.message }; }
"""
print(json.dumps(execute_js(JS), indent=2))
