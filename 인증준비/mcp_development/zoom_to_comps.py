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
    if (!allComps) return { error: "No comps" };
    
    let ids = [];
    for (let c of allComps) {
        let des = c.designator;
        if (!des && typeof c.getState_Designator === 'function') des = c.getState_Designator();
        if (["TYPE_C", "SOP16", "C1", "C2"].includes(des)) {
            ids.push(c.getState_PrimitiveId ? c.getState_PrimitiveId() : (c.id || c.primitiveId));
        }
    }
    
    if (ids.length > 0) {
        if (eda.sys_Selection && eda.sys_Selection.select) {
            await eda.sys_Selection.select(ids);
        } else if (eda.dmt_SelectControl && eda.dmt_SelectControl.select) {
            await eda.dmt_SelectControl.select(ids);
        } else if (eda.pcb_SelectControl && eda.pcb_SelectControl.select) {
            await eda.pcb_SelectControl.select(ids);
        }
        
        // Zoom to fit selected
        if (eda.pcb_View && eda.pcb_View.fitSelected) {
            await eda.pcb_View.fitSelected();
        } else if (eda.pcb_View && eda.pcb_View.fitAllObjects) {
            await eda.pcb_View.fitAllObjects();
        }
    }
    
    return { status: "Selected and Zoomed", selected: ids };
} catch(e) { return { error: e.message }; }
"""
print(json.dumps(execute_js(JS), indent=2))
