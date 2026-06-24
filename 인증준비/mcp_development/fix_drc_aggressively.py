import json
import urllib.request
from easyeda_mcp_client import EasyEDAMCPClient

client = EasyEDAMCPClient()
if not client.connect():
    print("Bridge connection failed")
    exit(1)

with open("full_drc.json", "r") as f:
    drc_data = json.load(f)

to_delete = set()
for cat in drc_data:
    for item in cat.get('list', []):
        if item.get('count', 0) > 0:
            for detail in item.get('detail', []):
                prim_id = detail.get('primitiveId')
                if prim_id:
                    to_delete.add(prim_id)

print(f"Found {len(to_delete)} primitives involved in DRC errors.")
deleted = 0
for pid in to_delete:
    if client.delete_primitive(pid):
        deleted += 1

print(f"Deleted {deleted} primitives.")
