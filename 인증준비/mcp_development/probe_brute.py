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
    let testCmds = [
        'pcb_copperPour_rebuildAll',
        'pcb_pour_rebuild',
        'pcb_rebuildPour',
        'pcb_rebuildCopper',
        'pcb_copper_rebuild',
        'rebuildCopper',
        'rebuildPour',
        'pcb_updateCopperPour',
        'updateCopperPour',
        'pcb_copper_update',
        'pcb_fillCopper',
        'pcb_copperFill'
    ];
    let results = [];
    for (let c of testCmds) {
        try {
            if (eda.sys_Command.execute(c)) {
                results.push(c);
            }
        } catch(e) {}
    }
    return results;
} catch(e) { return e.message; }
"""
print(execute_js(JS))
