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
    // List all opened documents across all open projects
    let allPcb = [];
    try { allPcb = await eda.dmt_Pcb.getAllPcbsInfo(); } catch(e) {}
    
    let allSch = [];
    try { allSch = await eda.dmt_Schematic.getAllSchematicsInfo(); } catch(e) {}
    
    return { pcbs: allPcb ? allPcb.map(p=>p.title) : [], schs: allSch ? allSch.map(s=>s.title) : [] };
} catch(e) { return { error: e.message }; }
"""
print(json.dumps(execute_js(JS), indent=2))
