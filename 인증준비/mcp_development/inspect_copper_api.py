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
    let props = [];
    if (eda.pcb_PrimitiveCopperRegion) {
        for (let k in eda.pcb_PrimitiveCopperRegion) {
            props.push(k);
        }
    }
    
    // Also check standard primitive create method:
    let primProps = [];
    if (eda.pcb_Primitive) {
        for (let k in eda.pcb_Primitive) {
            primProps.push(k);
        }
    }
    
    // Check if sys_Command has copper region commands
    let cmds = [];
    if (eda.sys_Command) {
        for (let k in eda.sys_Command.commands) {
            if (k.toLowerCase().includes("copper")) cmds.push(k);
        }
    }
    
    return { copperProps: props, primProps: primProps, cmds: cmds };
} catch(e) { return { error: e.message }; }
"""
print(json.dumps(execute_js(JS), indent=2))
