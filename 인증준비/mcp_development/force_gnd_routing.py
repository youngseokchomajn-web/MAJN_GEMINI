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
                    let netName = group.title;
                    if (netName && netName.includes(" (")) netName = netName.split(" (")[0];
                    if (netName !== "GND") continue; // ONLY GND
                    
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
    
    let pads = await eda.pcb_PrimitivePad.getAll();
    let gndCoords = [];
    if (pads) {
        for (let p of pads) {
            if (p.net === "GND") {
                if (p.x !== undefined && p.y !== undefined) {
                    gndCoords.push({ x: p.x, y: p.y, layer: p.layer || 1 });
                }
            }
        }
    }
    
    let newTracks = [];
    let newVias = [];
    
    // Stitch all GND pads with a Via
    for (let c of gndCoords) {
        newVias.push({
            primitiveType: "Via",
            net: "GND",
            x: c.x,
            y: c.y,
            hole: 0.3,
            diameter: 0.6
        });
    }
    
    // Sort coords by X, then Y to make a somewhat logical daisy chain
    gndCoords.sort((a,b) => {
        if (Math.abs(a.x - b.x) > 5) return a.x - b.x;
        return a.y - b.y;
    });
    
    for (let i = 0; i < gndCoords.length - 1; i++) {
        let p1 = gndCoords[i];
        let p2 = gndCoords[i+1];
        
        // Only connect if reasonably close to avoid crossing the entire board
        let dist = Math.sqrt(Math.pow(p1.x - p2.x, 2) + Math.pow(p1.y - p2.y, 2));
        if (dist < 1500) { 
            newTracks.push({
                primitiveType: "Line",
                layer: 1, // Top
                net: "GND",
                lineWidth: 0.3, 
                pointArr: [
                    { x: p1.x, y: p1.y },
                    { x: p2.x, y: p2.y }
                ]
            });
            newTracks.push({
                primitiveType: "Line",
                layer: 2, // Bottom
                net: "GND",
                lineWidth: 0.3,
                pointArr: [
                    { x: p1.x, y: p1.y },
                    { x: p2.x, y: p2.y }
                ]
            });
        }
    }
    
    if (newVias.length > 0) await eda.pcb_PrimitiveVia.create(newVias);
    if (newTracks.length > 0) await eda.pcb_PrimitiveLine.create(newTracks);
    
    return { status: "Success", createdVias: newVias.length, createdTracks: newTracks.length };
} catch(e) { return { error: e.message }; }
"""
print(json.dumps(execute_js(JS), indent=2))
