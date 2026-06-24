import json
import urllib.request
import time
from easyeda_mcp_client import EasyEDAMCPClient

def execute_js(code):
    url = "http://127.0.0.1:49620/execute"
    payload = json.dumps({"code": code}).encode("utf-8")
    req = urllib.request.Request(url, data=payload, headers={"Content-Type": "application/json"}, method="POST")
    with urllib.request.urlopen(req, timeout=30) as response:
        res = json.loads(response.read().decode("utf-8"))
        if res.get("success"): return res.get("result")
        else: raise Exception(res.get("error"))

client = EasyEDAMCPClient()
if not client.connect():
    print("Bridge connection failed")
    exit(1)

# Delete existing U3, U4
js_delete = """
const comps = await eda.pcb_PrimitiveComponent.getAll();
const toDelete = [];
for (const c of comps || []) {
    const des = c.designator || c.getState_Designator?.();
    if (des === 'U3' || des === 'U4') {
        toDelete.push(c.getState_PrimitiveId?.() || c.primitiveId || c.id);
    }
}
if (toDelete.length > 0) {
    await eda.pcb_PrimitiveComponent.delete(toDelete);
    return { deleted: toDelete.length };
}
return { deleted: 0 };
"""
print("Deleting old U3 and U4...")
res = execute_js(js_delete)
print(res)

with open("mcp_design_flow.json", "r", encoding="utf-8") as f:
    flow = json.load(f)
client.project_data["components"] = flow["components"]

u3_data = next(c for c in flow["components"] if c["designator"] == "U3")
u4_data = next(c for c in flow["components"] if c["designator"] == "U4")

print("Caching components...")
client.cache_components(["C2909511", "C478472"])

print("Placing U3...")
client.place_component("U3", u3_data["name"], u3_data["lcsc_id"], u3_data["x"], u3_data["y"], u3_data["angle"])

print("Placing U4...")
client.place_component("U4", u4_data["name"], u4_data["lcsc_id"], u4_data["x"], u4_data["y"], u4_data["angle"])

print("Component fix complete!")
