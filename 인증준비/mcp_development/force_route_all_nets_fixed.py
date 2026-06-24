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
    
    let errorNets = new Set();
    if (drcRes && Array.isArray(drcRes)) {
        for (let cat of drcRes) {
            if (cat.name === "Connection Error") {
                let list = cat.list || [];
                for (let group of list) {
                    let netName = group.title;
                    if (netName && netName.includes(" (")) {
                        netName = netName.split(" (")[0];
                    }
                    if (netName) errorNets.add(netName);
                }
            }
        }
    }
    
    let pads = await eda.pcb_PrimitivePad.getAll();
    let netToPads = {};
    if (pads) {
        for (let p of pads) {
            let n = p.net;
            if (n && errorNets.has(n)) {
                if (!netToPads[n]) netToPads[n] = [];
                if (p.x !== undefined && p.y !== undefined) {
                    netToPads[n].push({ x: p.x, y: p.y, layer: p.layer || 1 });
                }
            }
        }
    }
    
    let createdTracks = 0;
    let createdVias = 0;
    let newTracks = [];
    let newVias = [];
    
    for (let net in netToPads) {
        let plist = netToPads[net];
        plist.sort((a, b) => {
            if (Math.abs(a.x - b.x) > 10) return a.x - b.x;
            return a.y - b.y;
        });
        
        if (plist.length >= 2) {
            for (let i = 0; i < plist.length - 1; i++) {
                let p1 = plist[i];
                let p2 = plist[i+1];
                
                newTracks.push({
                    primitiveType: "Line",
                    layer: p1.layer || 1,
                    net: net,
                    lineWidth: 0.2, // 0.2mm
                    pointArr: [
                        { x: p1.x, y: p1.y },
                        { x: p2.x, y: p2.y }
                    ]
                });
                createdTracks++;
            }
        }
        
        if (net === "GND") {
            for (let p of plist) {
                newVias.push({
                    primitiveType: "Via",
                    net: "GND",
                    x: p.x,
                    y: p.y,
                    hole: 0.3,
                    diameter: 0.6
                });
                createdVias++;
            }
        }
    }
    
    if (newTracks.length > 0) await eda.pcb_PrimitiveLine.create(newTracks);
    if (newVias.length > 0) await eda.pcb_PrimitiveVia.create(newVias);
    
    return { status: "Success", errorNetsFound: errorNets.size, createdTracks: createdTracks, createdVias: createdVias };
} catch(e) { return { error: e.message }; }
"""
print(json.dumps(execute_js(JS), indent=2))
