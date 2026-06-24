import json
import urllib.request

def execute_js(code):
    url = "http://127.0.0.1:49620/execute"
    payload = json.dumps({"code": code}).encode("utf-8")
    req = urllib.request.Request(url, data=payload, headers={"Content-Type": "application/json"}, method="POST")
    with urllib.request.urlopen(req, timeout=45) as response:
        res = json.loads(response.read().decode("utf-8"))
        if res.get("success"): return res.get("result")
        return {"error": res.get("error")}

JS = "return await eda.pcb_Drc.check(false, false, true);"
res = execute_js(JS)

summary = []
if isinstance(res, list):
    for cat in res:
        cat_name = cat.get('title', ['Unknown'])[0]
        for item in cat.get('list', []):
            name = item.get('name')
            for err in item.get('list', []):
                rule = err.get('ruleName')
                exp = err.get('explanation', {}).get('str', '')
                if 'errData' in err.get('explanation', {}):
                    errData = err['explanation']['errData']
                    exp += f" | act: {errData.get('act')}, req: {errData.get('req')}"
                summary.append(f"[{cat_name}] {name} (Rule: {rule}) - {exp}")

with open("drc_summary.txt", "w") as f:
    f.write("\n".join(summary))
print(f"Dumped {len(summary)} errors to drc_summary.txt")
