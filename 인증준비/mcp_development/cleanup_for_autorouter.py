import json
import urllib.request

def execute_js(code):
    url = "http://127.0.0.1:49620/execute"
    payload = json.dumps({"code": code}).encode("utf-8")
    req = urllib.request.Request(url, data=payload, headers={"Content-Type": "application/json"}, method="POST")
    with urllib.request.urlopen(req, timeout=30) as response:
        res = json.loads(response.read().decode("utf-8"))
        if res.get("success"): return res.get("result")
        else: raise Exception(res.get("error"))

js = """
const powerNets = ['VBUS_5V', 'BOOST_SW', 'PVDD_12V', 'VCC_3V3', 'AMP_OUT_A+', 'AMP_OUT_A-', 'AMP_OUT_B+', 'AMP_OUT_B-', 'GND'];
let locked = 0;
let deleted = 0;

// In EasyEDA Pro, tracks are PrimitiveLine
const lines = await eda.pcb_PrimitiveLine.getAll();
const toDelete = [];

for (const line of lines || []) {
    const net = line.net || (typeof line.getState_Net === 'function' ? line.getState_Net() : '');
    
    // Check if it's a power net
    let isPower = false;
    for (const pn of powerNets) {
        if (net === pn || net.includes(pn)) {
            isPower = true; break;
        }
    }
    
    if (isPower) {
        // Lock the power line so autorouter doesn't touch it
        // Depending on EasyEDA API version, it might be setState_IsLocked or just setting isLocked
        if (typeof line.setState_IsLocked === 'function') {
            await line.setState_IsLocked(true);
            if (typeof line.done === 'function') await line.done();
            locked++;
        }
    } else {
        // Not a power net, we should delete it to clean up for Auto Router
        toDelete.push(line.primitiveId || (typeof line.getState_PrimitiveId === 'function' ? line.getState_PrimitiveId() : line.id));
    }
}

if (toDelete.length > 0) {
    try {
        await eda.pcb_PrimitiveLine.delete(toDelete);
        deleted = toDelete.length;
    } catch(e) {}
}

return { lockedCount: locked, deletedCount: deleted };
"""
print(execute_js(js))
