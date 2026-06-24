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
    if (eda.pcb_Document && eda.pcb_Document.currentDocument) {
        // Look for export methods
        let doc = eda.pcb_Document.currentDocument;
        let methods = [];
        for (let k in doc) {
            if (k.toLowerCase().includes("export") || k.toLowerCase().includes("json")) {
                methods.push(k);
            }
        }
        result.methods = methods;
    }
    
    // Check sys_Command for export commands
    if (eda.sys_Command) {
        let cmds = [];
        for (let k in eda.sys_Command.commands) {
            if (k.toLowerCase().includes("export")) cmds.push(k);
        }
        result.commands = cmds;
    }
    
    return result;
} catch(e) { return { error: e.message }; }
"""
print(json.dumps(execute_js(JS), indent=2))
