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
    const config = await eda.pcb_Drc.getCurrentRuleConfiguration();
    return config;
} catch(e) { return e.message; }
"""
res = execute_js(JS)
with open("current_rule.json", "w") as f:
    json.dump(res, f, indent=2)
print("Saved to current_rule.json")
