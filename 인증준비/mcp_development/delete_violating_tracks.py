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
    let idsToDelete = new Set();
    
    function extractId(obj) {
        if (!obj || !obj.suffix) return null;
        let parts = obj.suffix.split(': ');
        if (parts.length > 1) {
            return parts[parts.length - 1].trim();
        }
        return null;
    }
    
    if (drcRes && Array.isArray(drcRes)) {
        for (let cat of drcRes) {
            if (cat.name.includes("Clearance Error")) {
                let list = cat.list || [];
                for (let group of list) {
                    // Only target Tracks and Vias
                    if (group.title && (group.title.includes('Track') || group.title.includes('Via'))) {
                        let errs = group.errorList || group.list || group.items || [group];
                        for (let err of errs) {
                            if (err.obj1 && (err.obj1.typeName === 'Track' || err.obj1.typeName === 'Via')) {
                                let id = extractId(err.obj1);
                                if (id) idsToDelete.add(id);
                            }
                            if (err.obj2 && (err.obj2.typeName === 'Track' || err.obj2.typeName === 'Via')) {
                                let id = extractId(err.obj2);
                                if (id) idsToDelete.add(id);
                            }
                        }
                    }
                }
            }
        }
    }
    
    let toDeleteArr = Array.from(idsToDelete);
    if (toDeleteArr.length > 0) {
        let allLines = await eda.pcb_PrimitiveLine.getAll();
        let allVias = await eda.pcb_PrimitiveVia.getAll();
        
        let validIds = new Set();
        if (allLines) allLines.forEach(l => {
            let id = l.getState_PrimitiveId ? l.getState_PrimitiveId() : l.primitiveId;
            if (id) validIds.add(id);
        });
        if (allVias) allVias.forEach(v => {
            let id = v.getState_PrimitiveId ? v.getState_PrimitiveId() : v.primitiveId;
            if (id) validIds.add(id);
        });
        
        let lineIds = toDeleteArr.filter(id => allLines && allLines.some(l => (l.getState_PrimitiveId?l.getState_PrimitiveId():l.primitiveId) === id));
        let viaIds = toDeleteArr.filter(id => allVias && allVias.some(v => (v.getState_PrimitiveId?v.getState_PrimitiveId():v.primitiveId) === id));
        
        if (lineIds.length > 0) await eda.pcb_PrimitiveLine.delete(lineIds);
        if (viaIds.length > 0) await eda.pcb_PrimitiveVia.delete(viaIds);
        
        return { deletedTracks: lineIds.length, deletedVias: viaIds.length, targetIds: toDeleteArr };
    }
    return { deletedTracks: 0, deletedVias: 0, targetIds: toDeleteArr };
} catch(e) { return { error: e.message }; }
"""
print(json.dumps(execute_js(JS), indent=2))
