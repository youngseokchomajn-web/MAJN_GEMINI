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
        // Find command related to rebuild copper
        let cmds = [];
        for (let k in eda.sys_Command.commands) {
            let n = eda.sys_Command.commands[k].name;
            if (n && n.toLowerCase().includes("copper")) {
                cmds.push(k);
            }
        }
        result.foundCmds = cmds;
        
        // Try to execute the most likely one
        let target = cmds.find(c => c.toLowerCase().includes("rebuild"));
        if (target) {
            eda.sys_Command.execute(target);
            result.executed = target;
        } else if (eda.sys_Command.hasCommand("pcb_rebuildCopper")) {
            eda.sys_Command.execute("pcb_rebuildCopper");
            result.executed = "pcb_rebuildCopper";
        } else if (eda.sys_Command.hasCommand("pcb_rebuildAllCopper")) {
            eda.sys_Command.execute("pcb_rebuildAllCopper");
            result.executed = "pcb_rebuildAllCopper";
        }
    }
    return result;
} catch(e) { return { error: e.message }; }
"""
print(json.dumps(execute_js(JS), indent=2))
