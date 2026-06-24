import json
import urllib.request
import time
from easyeda_mcp_client import EasyEDAMCPClient

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

power_nets = [
    "GND", "VBUS_5V", "BOOST_SW", "PVDD_12V", 
    "VCC_3V3", "AMP_OUT_A+", "AMP_OUT_A-", "AMP_OUT_B+", "AMP_OUT_B-"
]

signal_nets = [net for net in flow["nets"].keys() if net not in power_nets]

# 3. Route Signal Nets
for net in signal_nets:
    print(f"Routing {net}...")
    pins = flow["nets"].get(net, [])
    if pins:
        res = client.connect_net(net, pins)
        print(f"Result for {net}:", res)
        time.sleep(0.5)

print("Signal routing completed!")
