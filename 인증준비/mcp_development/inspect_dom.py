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
    let result = { buttons: [], inputs: [], canvas: null };
    
    // Find canvas
    let canvases = document.querySelectorAll('canvas');
    if (canvases.length > 0) result.canvas = canvases.length;
    
    // Find right panel net input
    let inputs = document.querySelectorAll('input');
    for (let i = 0; i < inputs.length; i++) {
        let el = inputs[i];
        if (el.className) result.inputs.push(el.className);
    }
    
    // Let's try to simulate drawing by dispatching events to the canvas
    return result;
} catch(e) { return { error: e.message }; }
"""
print(json.dumps(execute_js(JS), indent=2))
