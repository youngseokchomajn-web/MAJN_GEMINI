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
    let output = {};
    
    if (drcRes && Array.isArray(drcRes)) {
        for (let cat of drcRes) {
            if (cat.name === "Connection Error") {
                let list = cat.list || [];
                for (let group of list) {
                    let netName = group.title;
                    if (netName && netName.includes(" (")) netName = netName.split(" (")[0];
                    if (netName === "GND") continue; // Skip GND for this check
                    
                    output[netName] = [];
                    let errs = group.errorList || group.list || group.items || [group];
                    for (let err of errs) {
                        if (err.obj1 && (err.obj1.typeName === "SMD Pad" || err.obj1.typeName === "TH Pad")) {
                            output[netName].push(err.obj1.suffix);
                        }
                    }
                }
            }
        }
    }
    
    // get coords
    let pads = await eda.pcb_PrimitivePad.getAll();
    for (let net in output) {
        let padDesignators = output[net];
        let coords = [];
        for (let suffix of padDesignators) {
            // suffix is like "(PVDD_12V): U5_4"
            let desig = suffix;
            if (suffix.includes(": ")) desig = suffix.split(": ")[1];
            
            // find pad
            if (pads) {
                for (let p of pads) {
                    let cprefix = p.parent ? p.parent.title : (p.componentPrefix || ""); 
                    // Wait, pads usually don't have direct component access easily, 
                    // better to look at all components
                }
            }
        }
    }
    
    // Actually, just returning the designators is enough for now
    return { unroutedSignalPads: output };
} catch(e) { return { error: e.message }; }
"""
print(json.dumps(execute_js(JS), indent=2))
