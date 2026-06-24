import json
import urllib.request
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
    let projs = await eda.dmt_Project.getAllProjectsInfo();
    let tp = projs ? projs.find(p => p.name === "Test_Tangled_Board_Project") : null;
    
    if (tp) {
        await eda.dmt_Project.openProject(tp.uuid);
        return { status: "Project found and opened", uuid: tp.uuid };
    }
    
    return { status: "Project not found" };
} catch(e) { return { error: e.message }; }
"""
print(json.dumps(execute_js(JS), indent=2))
