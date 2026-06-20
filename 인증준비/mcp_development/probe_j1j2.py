#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""비파괴: J1/J2(10핀 커넥터) 식별 + 위치 + 각 핀의 net 보유 여부 확인.
핀이 net을 내재하면 이동해도 연결 안 끊김(이동 안전)."""
import sys, json
from easyeda_mcp_client import EasyEDAMCPClient

SCHPG_UUID = "6085a53b74cfcf6b"

JS = f"""
const out = {{}};
try {{
  await eda.dmt_EditorControl.openDocument("{SCHPG_UUID}");
  await new Promise(r=>setTimeout(r,1000));
  await eda.dmt_EditorControl.activateDocument("{SCHPG_UUID}");
  await new Promise(r=>setTimeout(r,1200));
}} catch(e){{}}

const comps = await eda.sch_PrimitiveComponent.getAll();
const res = [];
for (const c of comps) {{
  let des=null; try{{ des = c.designator ?? c.getState_Designator?.(); }}catch(e){{}}
  if (des !== 'J1' && des !== 'J2') continue;
  let x=null,y=null,rot=null,sym=null;
  try{{ x=c.getState_X(); }}catch(e){{}}
  try{{ y=c.getState_Y(); }}catch(e){{}}
  try{{ rot=c.getState_Rotation(); }}catch(e){{}}
  try{{ const s=c.getState_Symbol(); sym = s? s.name : null; }}catch(e){{}}
  let pins = [];
  try {{
    const ps = await c.getAllPins();
    for (const p of (ps||[])) {{
      let pn=null, net=null, px=null, py=null;
      try{{ pn = p.pinNumber ?? p.getState_PinNumber?.() ?? p.number; }}catch(e){{}}
      try{{ net = p.net ?? p.getState_Net?.(); }}catch(e){{}}
      try{{ px = p.x ?? p.getState_X?.(); }}catch(e){{}}
      try{{ py = p.y ?? p.getState_Y?.(); }}catch(e){{}}
      pins.push({{ pn, net, px, py }});
    }}
  }} catch(e){{ pins = 'ERR:'+e.message; }}
  res.push({{ des, x, y, rot, sym, pins }});
}}
out.connectors = res;
return out;
"""

def main():
    client = EasyEDAMCPClient()
    if not client.connect():
        print("[ERROR] 브릿지 연결 실패"); sys.exit(1)
    res = client.execute_js(JS)
    with open("probe_j1j2_out.json","w",encoding="utf-8") as f:
        json.dump(res,f,ensure_ascii=False,indent=2,default=str)
    print("WROTE probe_j1j2_out.json")
    for c in res.get("connectors",[]):
        print(f"{c['des']}: pos=({c['x']},{c['y']}) rot={c['rot']} sym={c['sym']}")
        if isinstance(c['pins'], list):
            for p in c['pins']:
                print(f"    pin {p['pn']}: net={p['net']} @({p['px']},{p['py']})")
        else:
            print("    pins:", c['pins'])

if __name__ == "__main__":
    main()
