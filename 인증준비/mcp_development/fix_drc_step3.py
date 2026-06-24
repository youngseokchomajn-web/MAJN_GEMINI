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
const out = { deletedItems: [] };
try {
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
    
    const lines = await eda.pcb_PrimitiveLine.getAll();
    let toDelete = [];
    if (lines) {
        lines.forEach(line => {
            let id = line.id || line.primitiveId;
            if (offendingIds.has(id)) toDelete.push(id);
        });
    }
    
    const vias = await eda.pcb_PrimitiveVia.getAll();
    if (vias) {
        vias.forEach(via => {
            let id = via.id || via.primitiveId;
            if (offendingIds.has(id)) toDelete.push(id);
        });
    }
    
    if (toDelete.length > 0) {
        // Unlock them first if they are locked
        toDelete.forEach(async id => {
            try {
                let obj = await eda.pcb_PrimitiveLine.get(id) || await eda.pcb_PrimitiveVia.get(id);
                if (obj && obj.setState_PrimitiveLock) {
                    obj.setState_PrimitiveLock(false);
                }
            } catch(e){}
        });
        
        await new Promise(r => setTimeout(r, 500));
        await eda.pcb_PrimitiveLine.delete(toDelete);
        await eda.pcb_PrimitiveVia.delete(toDelete);
        out.deletedItems = toDelete;
    }
    
    return out;
} catch(e) {
    return { error: e.message };
}
"""
print(execute_js(JS))
