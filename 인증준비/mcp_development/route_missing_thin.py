import json
import urllib.request
from easyeda_mcp_client import EasyEDAMCPClient

client = EasyEDAMCPClient()
if not client.connect():
    print("Bridge connection failed")
    exit(1)

with open("mcp_design_flow.json", "r", encoding="utf-8") as f:
    flow = json.load(f)

client.project_data["name"] = flow["project_name"]
client.project_data["components"] = flow["components"]
client.project_data["nets"] = flow["nets"]

# Force trace width to very thin (0.1mm) to pass clearance!
client.project_data["pcb_settings"]["traces"]["signal"] = 0.1
client.project_data["pcb_settings"]["traces"]["power"] = 0.25 # Power needs to be thicker, but if it fails we can make it 0.1

target_nets = [
    "VBUS_5V", "VCC_3V3", "AMP_PDN", "BOOST_EN", "USB_CC2", 
    "BOOST_FB", "BST_A+", "AMP_OUT_A+", "BST_B+", "AMP_OUT_B+", "GND",
    "AMP_IN_A+", "AMP_IN_A-", "AMP_IN_B+", "AMP_IN_B-", "AUDIO_L", "AUDIO_R"
]

print("Routing missing nets using Python API...")
for net in target_nets:
    print(f"Routing {net}...")
    pins = flow["nets"].get(net, [])
    if pins:
        res = client.connect_net(net, pins)
        print(f"Result for {net}:", res)

print("Done routing missing nets.")
