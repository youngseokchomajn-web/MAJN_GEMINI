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
    let lines = await eda.pcb_PrimitiveLine.getAll();
    if (lines && lines.length > 0) {
        let l = lines[0];
        
        let props = {};
        for (let k in l) {
            if (typeof l[k] !== 'function') {
                props[k] = l[k];
            } else {
                try { props[k + "()"] = l[k](); } catch(e) { props[k + "()"] = "ERROR"; }
            }
        }
        return { props: props };
    }
    return { empty: true };
} catch(e) { return { error: e.message }; }
"""
res = execute_js(JS)
with open("line_props.json", "w") as f:
    json.dump(res, f, indent=2)
print("Dumped line_props.json")
