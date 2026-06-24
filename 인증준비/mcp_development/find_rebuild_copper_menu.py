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
    let result = [];
    if (eda.sys_Command && eda.sys_Command.commands) {
        for (let key in eda.sys_Command.commands) {
            let cmd = eda.sys_Command.commands[key];
            if (cmd.name && cmd.name.toLowerCase().includes("copper")) {
                result.push({ id: key, name: cmd.name });
            }
        }
    }
    return { cmds: result };
} catch(e) { return { error: e.message }; }
"""
print(json.dumps(execute_js(JS), indent=2))
