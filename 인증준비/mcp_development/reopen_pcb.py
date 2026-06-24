import json
import urllib.request
import time

def execute_js(code):
    url = "http://127.0.0.1:49620/execute"
    payload = json.dumps({"code": code}).encode("utf-8")
    req = urllib.request.Request(url, data=payload, headers={"Content-Type": "application/json"}, method="POST")
    with urllib.request.urlopen(req, timeout=30) as response:
        res = json.loads(response.read().decode("utf-8"))
        if res.get("success"): return res.get("result")
        else: raise Exception(res.get("error"))

js = """
// Get all documents
let pcbUuid = null;
try {
    const pcbInfo = await eda.dmt_Project.getCurrentPcbInfo();
    if (pcbInfo) pcbUuid = pcbInfo.uuid;
} catch(e) {}

if (pcbUuid) {
    await eda.dmt_EditorControl.openDocument(pcbUuid);
    await new Promise(resolve => setTimeout(resolve, 2000));
    await eda.dmt_EditorControl.activateDocument(pcbUuid);
    return "PCB Opened: " + pcbUuid;
} else {
    // try to find any PCB in project
    const proj = await eda.dmt_Project.getCurrentProjectInfo();
    return "No PCB found. Proj: " + (proj ? proj.uuid : 'null');
}
"""
print(execute_js(js))
