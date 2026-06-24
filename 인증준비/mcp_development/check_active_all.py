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
    let pcb = null;
    try { pcb = await eda.dmt_Pcb.getCurrentPcbInfo(); } catch(e) {}
    
    let sch = null;
    try { sch = await eda.dmt_Schematic.getCurrentSchematicInfo(); } catch(e) {}
    
    let proj = null;
    try { proj = await eda.dmt_Project.getCurrentProjectInfo(); } catch(e) {}
    
    let allComps = [];
    try { allComps = await eda.pcb_PrimitiveComponent.getAll(); } catch(e) {}
    let compCount = allComps ? allComps.length : 0;
    
    return {
        pcb: pcb ? pcb.name : null,
        pcb_uuid: pcb ? pcb.uuid : null,
        sch: sch ? sch.name : null,
        proj: proj ? proj.name : null,
        compCount: compCount
    };
} catch(e) { return { error: e.message }; }
"""
print(json.dumps(execute_js(JS), indent=2))
