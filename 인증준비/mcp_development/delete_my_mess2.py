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
    
    let lineIds = [];
    let viaIds = [];
    
    let targetNets = ["PVDD_12V", "VBUS_5V", "USB_CC2", "NET_CC1"];
    if (lines) {
        for (let l of lines) {
            if (targetNets.includes(l.net) && l.lineWidth === 10) {
                lineIds.push(l.primitiveId);
            }
        }
    }
    
    if (vias) {
        for (let v of vias) {
            if (v.net === "GND" && v.diameter === 24) {
                viaIds.push(v.primitiveId);
            }
        }
    }
    
    if (lineIds.length > 0) await eda.pcb_PrimitiveLine.delete(lineIds);
    if (viaIds.length > 0) await eda.pcb_PrimitiveVia.delete(viaIds);
    
    if (eda.sys_Command && eda.sys_Command.hasCommand("pcb_rebuildAllCopper")) {
        eda.sys_Command.execute("pcb_rebuildAllCopper");
    }
    
    return { status: "Success", deletedLines: lineIds.length, deletedVias: viaIds.length };
} catch(e) { return { error: e.message }; }
"""
print(json.dumps(execute_js(JS), indent=2))
