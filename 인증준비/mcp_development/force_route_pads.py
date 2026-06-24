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
    
    // 1. Gather disconnected pads by net
    let disconnectedPads = {}; // net -> [ "U3_5", "C1_1" ]
    
    if (drcRes && Array.isArray(drcRes)) {
        for (let cat of drcRes) {
            if (cat.name === "Connection Error") {
                let list = cat.list || [];
                for (let group of list) {
                    let netName = group.title;
                    // strip " (count)" from netName
                    if (netName && netName.includes(" (")) {
                        netName = netName.split(" (")[0];
                    }
                    if (!disconnectedPads[netName]) disconnectedPads[netName] = [];
                    
                    let errs = group.errorList || group.list || group.items || [group];
                    for (let err of errs) {
                        if (err.obj1 && (err.obj1.typeName === "SMD Pad" || err.obj1.typeName === "TH Pad")) {
                            let suffix = err.obj1.suffix; // e.g. "(BOOST_SW): U3_5"
                            let parts = suffix.split(": ");
                            if (parts.length > 1) {
                                disconnectedPads[netName].push(parts[1].trim());
                            }
                        }
                    }
                }
            }
        }
    }
    
    // 2. Map pad designators to coordinates
    let allComps = await eda.pcb_PrimitiveComponent.getAll();
    let padCoords = {}; // "U3_5" -> {x, y, layer}
    
    if (allComps) {
        for (let comp of allComps) {
            let prefix = comp.title || ""; // e.g. "U3"
            let pads = comp.primitivePads || [];
            for (let pad of pads) {
                let padNum = pad.number || "";
                let key = prefix + "_" + padNum;
                // Actually, component x, y are base. pad.x, pad.y are relative to component?
                // In EasyEDA, pad.x and pad.y are usually absolute coordinates in the Canvas!
                let px = pad.x;
                let py = pad.y;
                if (px !== undefined && py !== undefined) {
                    padCoords[key] = { x: px, y: py, layer: pad.layer || 1 };
                }
            }
        }
    }
    
    // 3. Draw tracks to connect pads in the same net
    let createdTracks = 0;
    let newTracks = [];
    
    for (let net in disconnectedPads) {
        let pads = disconnectedPads[net];
        // Deduplicate
        pads = [...new Set(pads)];
        
        let coords = [];
        for (let p of pads) {
            if (padCoords[p]) {
                coords.push(padCoords[p]);
            }
        }
        
        // Form a chain
        if (coords.length >= 2) {
            for (let i = 0; i < coords.length - 1; i++) {
                let p1 = coords[i];
                let p2 = coords[i+1];
                
                // create a track
                newTracks.push({
                    primitiveType: "Track",
                    layer: p1.layer || 1, // draw on p1's layer
                    net: net,
                    lineWidth: 0.2, // thin route
                    pointArr: [
                        { x: p1.x, y: p1.y },
                        { x: p2.x, y: p2.y }
                    ]
                });
                createdTracks++;
            }
        }
    }
    
    // Apply creations
    if (newTracks.length > 0) {
        await eda.pcb_PrimitiveTrack.create(newTracks);
    }
    
    return { status: "Success", createdTracks: createdTracks, padsMapped: Object.keys(padCoords).length };
} catch(e) { return { error: e.message }; }
"""
print(json.dumps(execute_js(JS), indent=2))
