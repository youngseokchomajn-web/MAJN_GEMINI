import json
import urllib.request
def execute_js(code):
    url = "http://127.0.0.1:49620/execute"
    payload = json.dumps({"code": code}).encode("utf-8")
    req = urllib.request.Request(url, data=payload, headers={"Content-Type": "application/json"}, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=45) as response:
            res = json.loads(response.read().decode("utf-8"))
            if res.get("success"): return res.get("result")
            return {"error": res.get("error")}
    except Exception as e:
        return {"error": str(e)}

JS = """
try {
    let result = "Failed";
    
    // Attempt 1: Common command names
    let cmds = [
        'pcb_rebuildAllCopperPour', 'rebuildAllCopperPour', 'pcb_rebuildCopperPour',
        'rebuildCopperPour', 'menu_pcb_rebuildAllCopperPour', 'pcb_pour_rebuildAll'
    ];
    for (let c of cmds) {
        try {
            if (eda.sys_Command.execute(c)) {
                result = "Executed command: " + c;
                break;
            }
        } catch(e) {}
    }
    return result;
} catch(e) { return e.message; }
"""
print(execute_js(JS))
