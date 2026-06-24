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
    // R1 0603 footprint
    let fp = {
        title: "0603",
        uuid: "20ad086208cb4d2ebefae5f44daaa2c4", // Just a dummy UUID, or we can use LCSC ID in some contexts
    };
    
    // We can also just fetch an existing component and move it, to be perfectly safe.
    let comps = await eda.pcb_PrimitiveComponent.getAll();
    if (comps && comps.length > 0) {
        let testComp = comps[0];
        let originalX = testComp.x || 0;
        let originalY = testComp.y || 0;
        let originalRotation = testComp.rotation || 0;
        
        // Move it temporarily
        await eda.pcb_PrimitiveComponent.modify(testComp.getState_PrimitiveId(), {
            x: originalX + 10,
            y: originalY + 10,
            rotation: (originalRotation + 90) % 360
        });
        
        // Verify
        let updated = await eda.pcb_PrimitiveComponent.getAll();
        let updatedComp = updated.find(c => c.getState_PrimitiveId() === testComp.getState_PrimitiveId());
        
        // Restore
        await eda.pcb_PrimitiveComponent.modify(testComp.getState_PrimitiveId(), {
            x: originalX,
            y: originalY,
            rotation: originalRotation
        });
        
        return {
            status: "Success",
            message: `Moved component ${testComp.designator} from (${originalX}, ${originalY}) to (${updatedComp.x}, ${updatedComp.y}) and restored.`
        };
    }
    return { status: "Skipped", message: "No components found to test movement." };
} catch(e) { return { error: e.message }; }
"""
print(json.dumps(execute_js(JS), indent=2))
