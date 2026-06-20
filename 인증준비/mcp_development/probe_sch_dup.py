#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""비파괴: 회로도 전체 부품(빈 designator 포함)을 id/designator/위치와 함께 조회.
같은 위치에 겹친 중복 부품을 찾는다."""
import sys, json
from easyeda_mcp_client import EasyEDAMCPClient

SCHPG_UUID = "6085a53b74cfcf6b"

JS = f"""
const out = {{}};
try {{
  await eda.dmt_EditorControl.openDocument("{SCHPG_UUID}");
  await new Promise(r=>setTimeout(r,1200));
  await eda.dmt_EditorControl.activateDocument("{SCHPG_UUID}");
  await new Promise(r=>setTimeout(r,1500));
}} catch(e){{ out.activate_err = e.message; }}

try {{
  const comps = await eda.sch_PrimitiveComponent.getAll();
  const list = [];
  for (const c of (comps||[])) {{
    let des=null, x=null, y=null, id=null, name=null;
    try {{ des = c.designator ?? (typeof c.getState_Designator==='function' ? await c.getState_Designator() : null); }} catch(e){{}}
    try {{ x = c.x ?? (typeof c.getState_X==='function' ? c.getState_X() : null); }} catch(e){{}}
    try {{ y = c.y ?? (typeof c.getState_Y==='function' ? c.getState_Y() : null); }} catch(e){{}}
    try {{ id = (typeof c.getState_PrimitiveId==='function' ? c.getState_PrimitiveId() : (c.primitiveId ?? c.id)); }} catch(e){{}}
    try {{ name = c.name ?? (typeof c.getState_Name==='function' ? c.getState_Name() : null); }} catch(e){{}}
    list.push({{ id, des, x, y, name }});
  }}
  out.total = list.length;
  out.comps = list;
  // 위치 중복 탐지
  const byPos = {{}};
  for (const c of list) {{
    const k = `${{c.x}},${{c.y}}`;
    (byPos[k] = byPos[k] || []).push(c);
  }}
  out.overlaps = Object.entries(byPos).filter(([k,v])=>v.length>1).map(([k,v])=>({{pos:k, items:v}}));
  // designator 없는 부품
  out.noDesignator = list.filter(c => !c.des);
}} catch(e){{ out.err = e.message; }}
return out;
"""

def main():
    client = EasyEDAMCPClient()
    if not client.connect():
        print("[ERROR] 브릿지 연결 실패"); sys.exit(1)
    res = client.execute_js(JS)
    with open("probe_sch_dup_out.json","w",encoding="utf-8") as f:
        json.dump(res,f,ensure_ascii=False,indent=2)
    print(f"total={res.get('total')}")
    print(f"overlaps={len(res.get('overlaps') or [])}")
    print(f"noDesignator={len(res.get('noDesignator') or [])}")
    for o in (res.get('overlaps') or []):
        print("  OVERLAP @", o['pos'], "->", [(i['id'], i['des'], i['name']) for i in o['items']])
    for c in (res.get('noDesignator') or []):
        print("  NO-DES:", c)

if __name__ == "__main__":
    main()
