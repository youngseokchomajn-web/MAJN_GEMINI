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

js_del = """
let deleted = false;
const types = Object.keys(eda).filter(k => k.startsWith('pcb_Primitive'));
for (const t of types) {
    if (eda[t] && typeof eda[t].delete === 'function') {
        try {
            await eda[t].delete(['e2']);
            deleted = true;
        } catch(e) {}
    }
}
return deleted;
"""
print(execute_js(js_del))
