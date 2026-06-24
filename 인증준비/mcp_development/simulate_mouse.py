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
    // 1. Activate Copper Region command
    if (eda.sys_Command) {
        eda.sys_Command.execute("pcb_copper_region");
    }
    
    // Wait for command to activate
    await new Promise(r => setTimeout(r, 500));
    
    // We can't easily simulate native Canvas events that EasyEDA catches because it uses custom event listeners on the document or a specific div.
    // Instead of mouse clicks, let's see if we can just create the object by bypassing the validation.
    // Let's look at the internal command object
    let cmd = eda.sys_Command.commands["pcb_copper_region"];
    return { cmdInfo: typeof cmd, cmdProps: Object.keys(cmd || {}) };
} catch(e) { return { error: e.message }; }
"""
print(json.dumps(execute_js(JS), indent=2))
