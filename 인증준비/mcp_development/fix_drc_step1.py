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
const out = { deletedOffending: 0, stitchedVias: 0 };
try {
    // 1. Get DRC errors to find offending tracks
    const drc = await eda.pcb_Drc.check(false, false, true);
    let offendingIds = new Set();
    
    if (Array.isArray(drc)) {
        drc.forEach(cat => {
            if (cat.title[0].includes("Clearance Error")) {
                cat.list.forEach(item => {
                    item.list.forEach(err => {
                        if (err.objs) {
                            err.objs.forEach(id => offendingIds.add(id));
                        }
                    });
                });
            }
        });
    }
    
    // We only want to delete lines, not pads/vias that are locked
    const lines = await eda.pcb_PrimitiveLine.getAll();
    let linesToDelete = [];
    if (lines) {
        lines.forEach(line => {
            let id = line.id || line.primitiveId;
            if (offendingIds.has(id)) {
                let locked = false;
                try { locked = line.getState_PrimitiveLock(); } catch(e){}
                if (!locked) {
                    linesToDelete.push(id);
                }
            }
        });
    }
    
    if (linesToDelete.length > 0) {
        await eda.pcb_PrimitiveLine.delete(linesToDelete);
        out.deletedOffending = linesToDelete.length;
    }
    
    return out;
} catch(e) {
    return { error: e.message };
}
"""
print(execute_js(JS))
