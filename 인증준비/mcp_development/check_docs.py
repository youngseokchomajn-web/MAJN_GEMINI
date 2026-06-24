import json
import urllib.request
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
    let currentDoc = null;
    try { currentDoc = await eda.dmt_SelectControl.getCurrentDocumentInfo(); } catch(e) {}
    
    let currentPcb = null;
    try { currentPcb = await eda.dmt_Pcb.getCurrentPcbInfo(); } catch(e) {}
    
    let allPcbs = [];
    try { allPcbs = await eda.dmt_Pcb.getAllPcbsInfo(); } catch(e) {}
    
    let projs = [];
    try { projs = await eda.dmt_Project.getAllProjectsInfo(); } catch(e) {}
    let currentProj = null;
    try { currentProj = await eda.dmt_Project.getCurrentProjectInfo(); } catch(e) {}
    
    let allComps = [];
    try { allComps = await eda.pcb_PrimitiveComponent.getAll(); } catch(e) {}
    let placedDes = allComps ? allComps.map(c => c.designator || (typeof c.getState_Designator === 'function' ? c.getState_Designator() : '')).filter(Boolean) : [];
    
    return { 
        currentDoc: currentDoc,
        currentPcb: currentPcb,
        allPcbs: allPcbs ? allPcbs.map(p => ({title: p.title, uuid: p.uuid})) : [],
        currentProj: currentProj ? currentProj.name : null,
        placed_designators_on_current_canvas: placedDes
    };
} catch(e) { return { error: e.message }; }
"""
print(json.dumps(execute_js(JS), indent=2))
