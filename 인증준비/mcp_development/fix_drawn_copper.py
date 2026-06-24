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
    let nets = await eda.pcb_PrimitiveNet.getAll();
    let gndId = "GND";
    if (nets) {
        for (let n of nets) {
            if (n.name === "GND") gndId = n.primitiveId;
        }
    }

    let changed = 0;
    
    // In EasyEDA, if we can't use getAll on CopperRegion, we can try SolidRegion
    let solids = [];
    try { solids = await eda.pcb_PrimitiveSolidRegion.getAll(); } catch(e){}
    if (solids) {
        for (let s of solids) {
            if (!s.net || s.net === "") {
                s.net = gndId;
                changed++;
            }
        }
        if (changed > 0) {
            // Need to apply changes somehow... typically via modify
            try { await eda.pcb_PrimitiveSolidRegion.modify(solids); } catch(e){}
        }
    }
    
    // Rebuild copper
    if (eda.sys_Command && eda.sys_Command.hasCommand("pcb_rebuildAllCopper")) {
        eda.sys_Command.execute("pcb_rebuildAllCopper");
    } else if (eda.sys_Command && eda.sys_Command.hasCommand("pcb_rebuildCopper")) {
        eda.sys_Command.execute("pcb_rebuildCopper");
    }
    
    return { status: "Success", solidsFound: solids ? solids.length : 0, changedCount: changed };
} catch(e) { return { error: e.message }; }
"""
print(json.dumps(execute_js(JS), indent=2))
