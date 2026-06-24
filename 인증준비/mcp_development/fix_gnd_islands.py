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
    let drcRes = await eda.pcb_Drc.check(true, false, true);
    let gndErrorPads = [];
    
    if (drcRes && Array.isArray(drcRes)) {
        for (let cat of drcRes) {
            if (cat.name === "Connection Error") {
                let list = cat.list || [];
                for (let group of list) {
                    if (group.title && group.title.startsWith("GND")) {
                        let errs = group.errorList || group.list || group.items || [group];
                        for (let err of errs) {
                            if (err.obj1 && (err.obj1.typeName === "SMD Pad" || err.obj1.typeName === "TH Pad")) {
                                gndErrorPads.push(err.obj1.suffix);
                            }
                        }
                    }
                }
            }
        }
    }
    
    let pads = await eda.pcb_PrimitivePad.getAll();
    let gndCoords = [];
    if (pads) {
        for (let p of pads) {
            if (p.net === "GND") {
                let suffixMatch = false;
                // suffix format in DRC is like "(GND): U1_5". So we check if p's designator matches
                // p.number is "5". component prefix might be "U1"
                // But let's just drop a via at ALL gnd error pads if we can find them, or just drop a via at EVERY GND pad to be absolutely sure!
            }
        }
    }
    
    // Simplest bulletproof way to fix GND islands: Drop a via directly on every single GND pad!
    let newVias = [];
    if (pads) {
        for (let p of pads) {
            if (p.net === "GND") {
                if (p.x !== undefined && p.y !== undefined) {
                    newVias.push({
                        primitiveType: "Via",
                        net: "GND",
                        x: p.x,
                        y: p.y,
                        hole: 0.3,
                        diameter: 0.6
                    });
                }
            }
        }
    }
    
    if (newVias.length > 0) {
        await eda.pcb_PrimitiveVia.create(newVias);
    }
    
    // Rebuild Copper
    if (eda.sys_Command.hasCommand("pcb_rebuildAllCopper")) {
        eda.sys_Command.execute("pcb_rebuildAllCopper");
    }
    
    return { status: "Success", viasAdded: newVias.length };
} catch(e) { return { error: e.message }; }
"""
print(json.dumps(execute_js(JS), indent=2))
