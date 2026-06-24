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
out = []
if isinstance(res, list):
    for cat in res:
        if "Clearance" in cat.get('title', [''])[0]:
            for item in cat.get('list', []):
                name = item.get('name')
                for err in item.get('list', [])[:3]: # grab first 3
                    net1 = err.get('obj1', {}).get('suffix', '')
                    net2 = err.get('obj2', {}).get('suffix', '')
                    out.append(f"{name}: {net1} <-> {net2}")
with open("drc_detail.txt", "w") as f:
    f.write("\n".join(out))
print("Done")
