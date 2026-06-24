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
    let nr = await eda.pcb_Drc.getNetRules();
    let cfg = await eda.pcb_Drc.getCurrentRuleConfiguration();
    let trackRules = cfg.config.Physics.Track;
    
    // Create a thin rule (0.25mm)
    let thinRuleName = "Thin_Power_0_25";
    trackRules[thinRuleName] = {
        editName: thinRuleName, unit: "mm", isSetDefault: false,
        form: { status: 1, data: { "1": { minValue: 0.25, defaultValue: 0.25, maxValue: 2.54 } } }
    };
    await eda.pcb_Drc.overwriteCurrentRuleConfiguration(cfg);
    
    // Assign to failing nets
    let failingNets = ["PVDD_12V", "VBUS_5V", "BOOST_SW", "VCC_3V3"];
    let assignedCount = 0;
    
    if (nr) {
        for (let r of nr) {
            if (failingNets.includes(r.name)) {
                r.Track = thinRuleName;
                assignedCount++;
            }
        }
        await eda.pcb_Drc.overwriteNetRules(nr);
    }
    return { status: "Success", thinRuleAssignedTo: assignedCount };
} catch(e) { return { error: e.message }; }
"""
print(json.dumps(execute_js(JS), indent=2))
