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
    if (!allComps || allComps.length === 0) return { error: "No comps found." };
    
    let sample = allComps[0];
    let keys = [];
    for(let k in sample) {
        keys.push(k);
    }
    
    return { 
        keys: keys, 
        id: sample.id, 
        primitiveId: sample.primitiveId,
        hasGetState_PrimitiveId: typeof sample.getState_PrimitiveId === 'function' 
    };
} catch(e) { return { error: e.message }; }
"""
print(json.dumps(execute_js(JS), indent=2))
