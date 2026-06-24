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
        let idsToDelete = [];
        for (let c of allComps) {
            let des = c.designator;
            if (!des && typeof c.getState_Designator === 'function') des = c.getState_Designator();
            if (["USBC1", "U1", "U2", "U3", "USBC2", "U4", "U5", "U6"].includes(des)) {
                let id = c.getState_PrimitiveId ? c.getState_PrimitiveId() : (c.id || c.primitiveId);
                if (id) idsToDelete.push(id);
            }
        }
        if (idsToDelete.length > 0) {
            await eda.pcb_PrimitiveComponent.delete(idsToDelete);
            result.push("Deleted " + idsToDelete.length + " old components.");
        }
    }
    
    return { status: "Cleaned", log: result };
} catch(e) { return { error: e.message }; }
"""
print(json.dumps(execute_js(JS), indent=2))
