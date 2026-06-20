#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""비파괴: 회로도 부품 1개의 전체 상태/메서드 덤프 -> 정확한 위치 읽기/쓰기 API 파악."""
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
// J2 또는 첫 designator 있는 부품 찾기
let target = null;
for (const c of comps) {{
  let des=null; try{{ des = c.designator ?? (c.getState_Designator?.()); }}catch(e){{}}
  if (des === 'J2') {{ target = c; break; }}
  if (!target && des) target = c;
}}
if (target) {{
  // 메서드 목록
  let methods = [];
  try {{ methods = Object.getOwnPropertyNames(Object.getPrototypeOf(target)).filter(m=>typeof target[m]==='function'); }} catch(e){{}}
  out.methods = methods;
  // getState_* 호출 결과
  const state = {{}};
  for (const m of methods) {{
    if (m.startsWith('getState_') && m !== 'getState_PrimitiveId') {{
      try {{ let v = target[m](); if (v && typeof v.then==='function') v = await v; state[m] = v; }} catch(e){{ state[m] = 'ERR:'+e.message; }}
    }}
  }}
  out.state = state;
  try {{ out.designator = target.designator ?? target.getState_Designator?.(); }} catch(e){{}}
}}
return out;
"""

def main():
    client = EasyEDAMCPClient()
    if not client.connect():
        print("[ERROR] 브릿지 연결 실패"); sys.exit(1)
    res = client.execute_js(JS)
    with open("probe_comp_state_out.json","w",encoding="utf-8") as f:
        json.dump(res,f,ensure_ascii=False,indent=2,default=str)
    print("WROTE probe_comp_state_out.json")
    print("methods:", res.get("methods"))
    print("designator:", res.get("designator"))
    st = res.get("state",{})
    for k in st:
        if any(t in k.lower() for t in ['x','y','rot','pos']):
            print(f"  {k} = {st[k]}")

if __name__ == "__main__":
    main()
