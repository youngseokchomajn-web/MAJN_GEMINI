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
const out = { addedGndVias: 0 };
try {
    const comps = await eda.pcb_PrimitiveComponent.getAll();
    const pins = [];
    for (const c of comps) {
        const pads = await c.getAllPins();
        for (const p of pads || []) {
            const net = p.net || p.getState_Net?.() || '';
            if (net === 'GND') {
                pins.push(p);
            }
        }
    }
    
    // Add a via EXACTLY on every GND pad to force connection to Layer 2 GND Plane
    // 24.0 mil diameter (0.6096mm), 12.0 mil hole (0.3048mm)
    for (const pin of pins) {
        const px = pin.x;
        const py = pin.y;
        
        await eda.pcb_PrimitiveVia.create('GND', px, py, 12.0, 24.0);
        out.addedGndVias++;
    }
    
    return out;
} catch(e) {
    return { error: e.message };
}
"""
print(execute_js(JS))
