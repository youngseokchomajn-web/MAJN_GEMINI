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
    let result = {};
    if (eda.sys_Command) {
        // Try to select
        try { eda.sys_Command.execute("sys_select", { gIds: ["e2911"] }); result.method1 = true; } catch(e){}
    }
    
    // Check if there is an API to delete by gId directly
    let hasDeleteByGid = false;
    // We can also just read the DOM!
    // In EasyEDA, you can do: let svgEl = document.getElementById('e2911');
    // From SVG element, maybe we can get coordinates or primitiveId?
    
    return result;
} catch(e) { return { error: e.message }; }
"""
print(json.dumps(execute_js(JS), indent=2))
