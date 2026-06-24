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
    let projs = await eda.sys_Project.getAllProjects();
    return { error: "Not allowed" };
} catch(e) { }

try {
    let docList = [];
    // Try to get all documents info
    let docs = await eda.dmt_Document.getAllDocumentsInfo();
    return { docs: docs };
} catch(e) { return { error: e.message }; }
"""
print(execute_js(JS))
