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
    let configName = await eda.pcb_Drc.getCurrentRuleConfigurationName();
    let config = await eda.pcb_Drc.getCurrentRuleConfiguration();
    
    if (config) {
        let clearance = config.config.Spacing["Safe Spacing"].copperThickness1oz.tables["1"].content[0][0];
        return {
            status: "Success",
            name: configName,
            clearance: clearance
        };
    }
    return { status: "Failed", message: "Config not found" };
} catch(e) { return { error: e.message }; }
"""
print(json.dumps(execute_js(JS), indent=2))
