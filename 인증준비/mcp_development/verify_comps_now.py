import json
import urllib.request
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
    let allComps = await eda.pcb_PrimitiveComponent.getAll();
    if (!allComps) return { error: "No comps" };
    
    let result = [];
    for (let c of allComps) {
        let des = c.designator;
        if (!des && typeof c.getState_Designator === 'function') des = c.getState_Designator();
        result.push(des);
    }
    return { count: allComps.length, designators: result };
} catch(e) { return { error: e.message }; }
"""
print(json.dumps(execute_js(JS), indent=2))
