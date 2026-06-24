import json
from easyeda_mcp_client import EasyEDAMCPClient

client = EasyEDAMCPClient()
if not client.connect():
    print("Bridge connection failed")
    exit(1)

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
