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
    if (eda.sys_Command && eda.sys_Command.hasCommand("sys_undo")) {
        eda.sys_Command.execute("sys_undo");
        return { status: "Undo 1" };
    } else if (eda.sys_Command.hasCommand("undo")) {
        eda.sys_Command.execute("undo");
        return { status: "Undo 2" };
    }
    return { status: "No undo command" };
} catch(e) { return { error: e.message }; }
"""
print(json.dumps(execute_js(JS), indent=2))
