import json

with open('/Users/youngseok/Desktop/majn/인증준비/mcp_development/Recovered_Schematic.json', 'r') as f:
    data = json.load(f)

comps = {}
for p in data.get('parts', []):
    des = p.get('des', 'Unknown')
    lcsc = p.get('lcsc', 'unknown')
    if lcsc != 'unknown':
        comps[des] = lcsc

print("Components found in Schematic:")
for des, lcsc in sorted(comps.items()):
    print(f"- {des}: LCSC {lcsc}")

