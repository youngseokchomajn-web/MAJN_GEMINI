import json

with open("drc_temp.json", "w") as f:
    pass

import urllib.request

def execute_js(code):
    url = "http://127.0.0.1:49620/execute"
    payload = json.dumps({"code": code}).encode("utf-8")
    req = urllib.request.Request(url, data=payload, headers={"Content-Type": "application/json"}, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=45) as response:
            res = json.loads(response.read().decode("utf-8"))
            if res.get("success"): return res.get("result")
            else: raise Exception(res.get("error"))
    except Exception as e:
        return {"error": str(e)}

JS = """
const res = await eda.pcb_Drc.check(false, false, true);
return res;
"""

result = execute_js(JS)

if isinstance(result, list):
    for category in result:
        print(f"--- {category.get('title', ['Unknown'])[0]} ---")
        for item in category.get('list', []):
            name = item.get('name')
            count = item.get('count')
            print(f"Net {name}: {count} errors")
