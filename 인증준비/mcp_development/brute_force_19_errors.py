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
    
    // Group disconnected pad suffixes by Net
    let errorNets = {}; // net -> [ "U4_16", "R1_1" ]
    
    if (drcRes && Array.isArray(drcRes)) {
        for (let cat of drcRes) {
            if (cat.name === "Connection Error") {
                let list = cat.list || [];
                for (let group of list) {
                    let netName = group.title;
                    if (netName && netName.includes(" (")) netName = netName.split(" (")[0];
                    if (!errorNets[netName]) errorNets[netName] = [];
                    
                    let errs = group.errorList || group.list || group.items || [group];
                    for (let err of errs) {
                        if (err.obj1 && (err.obj1.typeName === "SMD Pad" || err.obj1.typeName === "TH Pad")) {
                            errorNets[netName].push(err.obj1.suffix);
                        }
                    }
                }
            }
        }
    }
    
    // Fetch all pads to map suffix to coordinates
    let pads = await eda.pcb_PrimitivePad.getAll();
    let netCoords = {}; // net -> [ {x, y, layer} ]
    
    if (pads) {
        for (let net in errorNets) {
            netCoords[net] = [];
            // We just fetch all pads matching the net.
            // Actually, to be safe, any pad in this net is a valid connection point!
            // We can just grab ALL pads of the net and daisy-chain them, or drop vias on them.
            for (let p of pads) {
                if (p.net === net && p.x !== undefined && p.y !== undefined) {
                    netCoords[net].push({ x: p.x, y: p.y, layer: p.layer || 1 });
                }
            }
        }
    }
    
    let viasAdded = 0;
    let tracksAdded = 0;
    
    for (let net in netCoords) {
        let plist = netCoords[net];
        
        if (net === "GND") {
            // Drop a via on EVERY GND pad. That will guarantee stitching to the Copper Pour!
            for (let p of plist) {
                try {
                    await eda.pcb_PrimitiveVia.create("GND", p.x, p.y, 12, 24); // 0.3mm hole, 0.6mm dia
                    viasAdded++;
                } catch(e) {}
            }
        } else {
            // Signal nets: daisy chain them with 10mil (0.254mm) lines on Top Layer
            if (plist.length >= 2) {
                for (let i = 0; i < plist.length - 1; i++) {
                    let p1 = plist[i];
                    let p2 = plist[i+1];
                    try {
                        await eda.pcb_PrimitiveLine.create(net, 1, p1.x, p1.y, p2.x, p2.y, 10, false);
                        tracksAdded++;
                    } catch(e) {}
                }
            }
        }
    }
    
    // Rebuild Copper
    if (eda.sys_Command && eda.sys_Command.hasCommand("pcb_rebuildAllCopper")) {
        eda.sys_Command.execute("pcb_rebuildAllCopper");
    } else if (eda.sys_Command && eda.sys_Command.hasCommand("pcb_rebuildCopper")) {
        eda.sys_Command.execute("pcb_rebuildCopper");
    }
    
    return { status: "Success", viasAdded: viasAdded, tracksAdded: tracksAdded };
} catch(e) { return { error: e.message }; }
"""
print(json.dumps(execute_js(JS), indent=2))
