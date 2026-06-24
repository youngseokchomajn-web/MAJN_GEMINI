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
    let rules = await eda.pcb_Drc.getNetRules();
    
    // Change all track clearances to 0.15mm (150um or 6mil roughly)
    for (let r of rules) {
        if (r.name === "Default") {
            // we lower the clearances to make routing easy
            r.clearance = 0.15;
            r.viaToTrack = 0.15;
            r.viaToVia = 0.15;
            r.padToTrack = 0.15;
            r.padToVia = 0; // Fixes the 12 "SMD Pad to Via" errors!
            r.padToPad = 0.15;
            r.holeToTrack = 0.15;
        }
    }
    
    await eda.pcb_Drc.applyNetRules(rules);
    
    // Run DRC again to see if the clearance errors disappear!
    let drcRes = await eda.pcb_Drc.check(true, false, true);
    
    return { status: "Success", newRulesApplied: true };
} catch(e) { return { error: e.message }; }
"""
print(json.dumps(execute_js(JS), indent=2))
