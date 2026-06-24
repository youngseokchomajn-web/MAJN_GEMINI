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
    let config = await eda.pcb_Drc.getCurrentRuleConfiguration();
    if (!config) return "No config found";

    // Modify safe spacing values to 0.15mm
    let tables = config.config.Spacing["Safe Spacing"].copperThickness1oz.tables["1"].content;
    for (let r = 0; r < tables.length; r++) {
        for (let c = 0; c < tables[r].length; c++) {
            tables[r][c] = 0.15;
        }
    }
    
    await eda.pcb_Drc.overwriteCurrentRuleConfiguration(config);
    return "Rules updated successfully!";
} catch(e) {
    return e.message;
}
"""
print(execute_js(JS))
