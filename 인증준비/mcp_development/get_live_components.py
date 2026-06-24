import json
import urllib.request
import sys
import pprint
import time

def execute_js(code):
    url = "http://127.0.0.1:49620/execute"
    payload = json.dumps({"code": code}).encode("utf-8")
    req = urllib.request.Request(url, data=payload, headers={"Content-Type": "application/json"}, method="POST")
    with urllib.request.urlopen(req, timeout=10) as response:
        res = json.loads(response.read().decode("utf-8"))
        if res.get("success"): return res.get("result")
        else: raise Exception(res.get("error"))

js_activate = """
const pcbs = await eda.dmt_Pcb.getAllPcbsInfo();
if (pcbs && pcbs.length > 0) {
    await eda.dmt_EditorControl.openDocument(pcbs[0].uuid);
    await eda.dmt_EditorControl.activateDocument(pcbs[0].uuid);
    return pcbs[0].uuid;
}
return null;
"""

js_fetch = """
const comps = await eda.pcb_PrimitiveComponent.getAll();
const result = [];
for (const c of comps || []) {
    let des = c.designator;
    if (!des && typeof c.getState_Designator === 'function') des = c.getState_Designator();
    result.push({
        designator: des,
        x: c.x || (typeof c.getState_X === 'function' ? c.getState_X() : 0),
        y: c.y || (typeof c.getState_Y === 'function' ? c.getState_Y() : 0),
        angle: c.angle || (typeof c.getState_Rotation === 'function' ? c.getState_Rotation() : 0)
    });
}
return result;
"""

try:
    print("Activating PCB...")
    pcb_uuid = execute_js(js_activate)
    print("PCB UUID:", pcb_uuid)
    if pcb_uuid:
        time.sleep(1) # wait for document to fully activate
        print("Fetching components...")
        comps = execute_js(js_fetch)
        pprint.pprint(comps)
    else:
        print("No PCB found in the current project.")
except Exception as e:
    print("Error:", e)
