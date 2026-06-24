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

JS = "return await eda.pcb_Drc.check(false, false, true);"
res = execute_js(JS)
summary = []
total = 0
if isinstance(res, list):
    for cat in res:
        cat_name = cat.get('title', ['Unknown'])[0]
        for item in cat.get('list', []):
            name = item.get('name')
            count = item.get('count')
            total += count
            summary.append(f"{cat_name} -> {name}: {count} errors")
print(f"Total: {total}")
print("\n".join(summary))
