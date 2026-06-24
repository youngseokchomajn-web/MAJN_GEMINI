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
const report = {};

// 1. Current PCB
try {
    const pcbInfo = await eda.dmt_Project.getCurrentPcbInfo();
    report.pcbInfo = pcbInfo ? {uuid: pcbInfo.uuid, title: pcbInfo.title} : null;
} catch(e) { report.pcbInfoError = e.message; }

// 2. Components
try {
    const comps = await eda.pcb_PrimitiveComponent.getAll();
    report.componentCount = comps ? comps.length : 0;
    report.u3u4 = comps ? comps.filter(c => c.designator === 'U3' || c.designator === 'U4').map(c => c.designator) : [];
} catch(e) {}

// 3. Board Outline (Layer 11)
try {
    const outlines = [];
    const types = ["pcb_PrimitiveLine", "pcb_PrimitiveArc", "pcb_PrimitivePolyline", "pcb_PrimitiveTrack"];
    for (const t of types) {
        if (eda[t] && typeof eda[t].getAll === "function") {
            const objs = await eda[t].getAll();
            for (const o of objs || []) {
                const lay = o.layerId || o.getState_LayerId?.();
                if (lay == 11 || lay == 41 || lay == 43 || lay == "BoardOutline" || String(lay).includes("Board")) {
                    outlines.push({type: t, id: o.primitiveId || o.id});
                }
            }
        }
    }
    report.boardOutlines = outlines;
} catch(e) {}

// 4. Native DRC errors
try {
    const drc = await eda.pcb_Drc.check(true, false, true);
    report.drcErrors = drc ? drc.map(cat => ({title: cat.title, count: cat.count})) : [];
} catch(e) { report.drcErrorMsg = e.message; }

return report;
"""
try:
    print(json.dumps(execute_js(js), indent=2))
except Exception as e:
    print("Error:", e)
