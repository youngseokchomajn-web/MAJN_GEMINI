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
const result = [];
const types = Object.keys(eda).filter(k => k.startsWith('pcb_Primitive'));
for (const t of types) {
    if (eda[t] && typeof eda[t].getAll === 'function') {
        try {
            const objs = await eda[t].getAll();
            for (const o of objs || []) {
                const layer = o.layerId || (typeof o.getState_LayerId === 'function' ? o.getState_LayerId() : null);
                if (layer == 11 || layer == 41 || layer == 43 || layer == "BoardOutline") {
                    result.push({
                        type: t,
                        id: o.primitiveId || (typeof o.getState_PrimitiveId === 'function' ? o.getState_PrimitiveId() : null),
                        suffix: o.suffix || (typeof o.getState_Suffix === 'function' ? o.getState_Suffix() : null),
                        locked: o.isLocked || (typeof o.getState_IsLocked === 'function' ? o.getState_IsLocked() : null)
                    });
                }
            }
        } catch(e) {}
    }
}
return result;
"""
print(execute_js(js))
