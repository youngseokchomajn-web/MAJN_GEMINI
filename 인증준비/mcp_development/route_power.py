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

# 1. Load Flow
with open("mcp_design_flow.json", "r", encoding="utf-8") as f:
    flow = json.load(f)

# 2. Init Client
client = EasyEDAMCPClient()
if not client.connect():
    print("Bridge connection failed")
    exit(1)

client.project_data["name"] = flow["project_name"]
client.project_data["components"] = flow["components"]
client.project_data["nets"] = flow["nets"]
client.project_data["pcb_settings"]["traces"] = flow["pcb_constraints"]["routing_widths_mm"]
# Update specifically based on the plan
client.project_data["pcb_settings"]["traces"]["VBUS_5V"] = 1.016 # 40mil
client.project_data["pcb_settings"]["traces"]["BOOST_SW"] = 0.762 # 30mil
client.project_data["pcb_settings"]["traces"]["PVDD_12V"] = 0.635 # 25mil
client.project_data["pcb_settings"]["traces"]["AMP_OUT_A+"] = 0.508 # 20mil
client.project_data["pcb_settings"]["traces"]["AMP_OUT_A-"] = 0.508 # 20mil
client.project_data["pcb_settings"]["traces"]["AMP_OUT_B+"] = 0.508 # 20mil
client.project_data["pcb_settings"]["traces"]["AMP_OUT_B-"] = 0.508 # 20mil
client.project_data["pcb_settings"]["traces"]["VCC_3V3"] = 0.381 # 15mil
client.project_data["pcb_settings"]["traces"]["GND"] = 0.5 # vias will be used

power_nets = [
    "GND", "VBUS_5V", "BOOST_SW", "PVDD_12V", 
    "VCC_3V3", "AMP_OUT_A+", "AMP_OUT_A-", "AMP_OUT_B+", "AMP_OUT_B-"
]

# 3. Route Power Nets
for net in power_nets:
    print(f"Routing {net}...")
    pins = flow["nets"].get(net, [])
    if pins:
        res = client.connect_net(net, pins)
        print(f"Result for {net}:", res)
        time.sleep(1)

# 4. Lock Traces
js_lock = """
const lines = await eda.pcb_PrimitiveLine.getAll();
let locked = 0;
const powerNets = ['VBUS_5V', 'BOOST_SW', 'PVDD_12V', 'VCC_3V3', 'AMP_OUT_A+', 'AMP_OUT_A-', 'AMP_OUT_B+', 'AMP_OUT_B-', 'GND'];
for (const line of lines || []) {
    const net = line.net || (typeof line.getState_Net === 'function' ? line.getState_Net() : '');
    if (powerNets.includes(net)) {
        if (typeof line.setState_IsLocked === 'function') {
            await line.setState_IsLocked(true);
            if (typeof line.done === 'function') await line.done();
            locked++;
        }
    }
}
return { lockedCount: locked };
"""
try:
    print("Locking power traces...")
    lock_res = execute_js(js_lock)
    print("Lock result:", lock_res)
except Exception as e:
    print("Lock error:", e)

print("Power-First routing completed!")
