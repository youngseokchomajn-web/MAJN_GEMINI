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
    let beforeSelect = [];
    try { beforeSelect = eda.pcb_SelectControl ? eda.pcb_SelectControl.getSelectIds() : []; } catch(e){}
    
    // Select via command?
    // Let's just try to call sys_Command to select 'e2911'
    let success = false;
    try {
        if (eda.sys_Command) {
             eda.sys_Command.execute("pcb_edit_find", { findText: "e2911" });
             success = true;
        }
    } catch(e){}
    
    return { beforeSelect: beforeSelect, success: success };
} catch(e) { return { error: e.message }; }
"""
print(json.dumps(execute_js(JS), indent=2))
