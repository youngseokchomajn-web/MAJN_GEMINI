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
    let unrouted = [];
    try {
        let lines = await eda.pcb_PrimitiveRatline.getAll();
        if (lines) {
            for (let r of lines) {
                unrouted.push(r.net || "Unknown");
            }
        }
    } catch(e) {}
    
    let counts = {};
    for (let net of unrouted) {
        counts[net] = (counts[net] || 0) + 1;
    }
    
    // Sort by count
    let sorted = Object.entries(counts).sort((a,b) => b[1] - a[1]);
    
    return { 
        totalUnrouted: unrouted.length,
        breakdown: Object.fromEntries(sorted)
    };
} catch(e) { return { error: e.message }; }
"""
print(json.dumps(execute_js(JS), indent=2))
