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
    let rules = await eda.sys_Config.get('pcb_designRule');
    if (!rules) return "No design rules found";
    
    // Force every clearance value to 0.1mm (0.1mm is 3.937mil)
    let modified = false;
    for (let r in rules) {
        if (rules[r] && typeof rules[r] === 'object') {
            for (let k in rules[r]) {
                if (k.toLowerCase().includes('clearance') || k.toLowerCase().includes('space') || k.toLowerCase().includes('gap')) {
                    rules[r][k] = 3.937;
                    modified = true;
                }
                if (typeof rules[r][k] === 'object') {
                   for(let j in rules[r][k]) {
                       rules[r][k][j] = 3.937;
                       modified = true;
                   }
                }
            }
        }
    }
    
    // Also try checking the copperThickness1oz rule directly
    if (rules.copperThickness1oz) {
        for(let k in rules.copperThickness1oz) {
            rules.copperThickness1oz[k] = 3.937;
            modified = true;
        }
    }

    if (modified) {
        await eda.sys_Config.set('pcb_designRule', rules);
        return "Rules modified to 0.1mm";
    }
    return "No clearance values found to modify";
} catch(e) { return e.message; }
"""
print(execute_js(JS))
