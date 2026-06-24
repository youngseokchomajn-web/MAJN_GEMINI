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
    let methods = [];
    if (eda.pcb_Drc) {
        methods = Object.getOwnPropertyNames(eda.pcb_Drc).concat(Object.keys(eda.pcb_Drc));
    }
    
    // Check if we can get rules
    let rules = null;
    try {
        if (eda.pcb_Drc && typeof eda.pcb_Drc.getNetRules === 'function') {
            rules = await eda.pcb_Drc.getNetRules();
        }
    } catch(e) {
        rules = "Error calling getNetRules: " + e.message;
    }
    
    // Is there a reset or set method?
    let setMethods = methods.filter(m => m.toLowerCase().includes("set") || m.toLowerCase().includes("rule"));
    
    // Also look at document level
    let docKeys = [];
    if (eda.pcb_Document && eda.pcb_Document.currentDocument) {
        docKeys = Object.keys(eda.pcb_Document.currentDocument).filter(k => k.toLowerCase().includes("rule"));
    }
    
    return { drcMethods: methods, setMethods, rulesType: typeof rules, rulesError: typeof rules === 'string' ? rules : null, docKeys };
} catch(e) { return { error: e.message }; }
"""
print(json.dumps(execute_js(JS), indent=2))
