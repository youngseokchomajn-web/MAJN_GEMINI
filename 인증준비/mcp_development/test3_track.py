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
    // 1. Draw a test track
    const netName = "GND"; // dummy net
    const layer = 1; // Top Layer
    const startX = 4000;
    const startY = 4000;
    const endX = 4200;
    const endY = 4200;
    const lineWidth = 10; // 10 mil
    
    // Create track
    let track = await eda.pcb_PrimitiveLine.create(netName, layer, startX, startY, endX, endY, lineWidth, false);
    
    // Verify track
    let allLines = await eda.pcb_PrimitiveLine.getAll();
    let found = allLines.find(l => l.getState_PrimitiveId() === track.getState_PrimitiveId());
    
    // Delete track
    await eda.pcb_PrimitiveLine.delete([track.getState_PrimitiveId()]);
    
    let allLinesAfter = await eda.pcb_PrimitiveLine.getAll();
    let foundAfter = allLinesAfter.find(l => l.getState_PrimitiveId() === track.getState_PrimitiveId());
    
    return {
        status: "Success",
        message: `Created track ID ${track.getState_PrimitiveId()}. Found in list: ${!!found}. Deleted track. Found after delete: ${!!foundAfter}`
    };
} catch(e) { return { error: e.message }; }
"""
print(json.dumps(execute_js(JS), indent=2))
