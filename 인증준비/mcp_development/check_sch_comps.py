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
    let comps = [];
    try { comps = await eda.sch_PrimitiveComponent.getAll(); } catch(e) {}
    let schCount = comps ? comps.length : 0;
    
    // Check if Design -> Update PCB is possible via command
    let updatePcbCmd = false;
    try {
        if (eda.sys_Command && eda.sys_Command.hasCommand("pcb_updatePcbFromSch")) {
             updatePcbCmd = true;
        }
    } catch(e) {}
    
    return { schCompCount: schCount, hasUpdateCmd: updatePcbCmd };
} catch(e) { return { error: e.message }; }
"""
print(json.dumps(execute_js(JS), indent=2))
