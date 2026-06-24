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
    let lines = await eda.pcb_PrimitiveLine.getAll();
    let vias = await eda.pcb_PrimitiveVia.getAll();
    
    let toDelete = [];
    
    // Delete the tracks I added
    let targetNets = ["PVDD_12V", "VBUS_5V", "USB_CC2", "NET_CC1"];
    if (lines) {
        for (let l of lines) {
            // If the line belongs to one of the 4 nets I brute-forced, AND has lineWidth 10
            if (targetNets.includes(l.net) && l.lineWidth === 10) {
                toDelete.push(l.primitiveId);
            }
        }
    }
    
    // Delete the vias I added (GND, hole 12, dia 24)
    if (vias) {
        for (let v of vias) {
            if (v.net === "GND" && v.diameter === 24) {
                toDelete.push(v.primitiveId);
            }
        }
    }
    
    if (toDelete.length > 0) {
        await eda.pcb_Primitive.delete(toDelete);
    }
    
    // Rebuild Copper
    if (eda.sys_Command && eda.sys_Command.hasCommand("pcb_rebuildAllCopper")) {
        eda.sys_Command.execute("pcb_rebuildAllCopper");
    }
    
    return { status: "Success", deletedCount: toDelete.length };
} catch(e) { return { error: e.message }; }
"""
print(json.dumps(execute_js(JS), indent=2))
