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
const out = { deletedLines: 0, deletedVias: 0 };
try {
    const lines = await eda.pcb_PrimitiveLine.getAll();
    let to_delete = [];
    if (lines) {
        for (const line of lines) {
            let locked = false;
            try { locked = line.getState_PrimitiveLock(); } catch(e){}
            if (!locked) to_delete.push(line.id || line.primitiveId);
        }
    }

    const vias = await eda.pcb_PrimitiveVia.getAll();
    if (vias) {
        for (const via of vias) {
            let locked = false;
            try { locked = via.getState_PrimitiveLock(); } catch(e){}
            let net = "";
            try { net = via.getState_Net(); } catch(e){}
            if (!locked && net !== "GND" && net !== "VBUS_5V" && net !== "PVDD_12V" && net !== "BOOST_SW") {
                to_delete.push(via.id || via.primitiveId);
            }
        }
    }
    
    to_delete = to_delete.filter(Boolean);
    if (to_delete.length > 0) {
        await eda.pcb_SelectControl.select(to_delete);
        await new Promise(r => setTimeout(r, 200));
        await eda.sys_Command.execute('delete');
        out.deleted = to_delete.length;
    }
    return out;
} catch(e) {
    return { error: e.message };
}
"""
print(execute_js(JS))
