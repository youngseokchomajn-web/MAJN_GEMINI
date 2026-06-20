#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""비파괴: 라이브 회로도의 부품 목록/수 직접 확인 (PCB와 대조)."""
import sys, json
from easyeda_mcp_client import EasyEDAMCPClient

SCHPG_UUID = "6085a53b74cfcf6b"

JS = f"""
const out = {{}};
// 회로도 페이지 활성화
try {{
  await eda.dmt_EditorControl.openDocument("{SCHPG_UUID}");
  await new Promise(r=>setTimeout(r,1500));
  await eda.dmt_EditorControl.activateDocument("{SCHPG_UUID}");
  await new Promise(r=>setTimeout(r,2000));
}} catch(e){{ out.activate_err = e.message; }}

// 회로도 부품
try {{
  const comps = await eda.sch_PrimitiveComponent.getAll();
  const list = [];
  for (const c of (comps||[])) {{
    let des = c.designator;
    try {{ if (!des && typeof c.getState_Designator==='function') des = await c.getState_Designator(); }} catch(e){{}}
    list.push(des);
  }}
  out.schComps = list.filter(Boolean).sort();
  out.schCount = out.schComps.length;
}} catch(e){{ out.sch_err = e.message; }}

return out;
"""

def main():
    client = EasyEDAMCPClient()
    if not client.connect():
        print("[ERROR] 브릿지 연결 실패"); sys.exit(1)
    res = client.execute_js(JS)
    print(json.dumps(res, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()
