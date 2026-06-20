#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""회로도 저장 + 최종 ERC 확정 + J1/J2 위치 확인."""
import sys, json
from easyeda_mcp_client import EasyEDAMCPClient

SCHPG_UUID = "939d8ca4c7bf9626"

JS = f"""
const out = {{}};
try {{
  await eda.dmt_EditorControl.openDocument("{SCHPG_UUID}");
  await new Promise(r=>setTimeout(r,1000));
  await eda.dmt_EditorControl.activateDocument("{SCHPG_UUID}");
  await new Promise(r=>setTimeout(r,1200));
}} catch(e){{}}

// 저장
try {{ out.saved = await eda.sch_Document.save(); }} catch(e){{ out.save_err = e.message; }}
await new Promise(r=>setTimeout(r,1500));

// 최종 ERC
try {{ out.erc = await eda.sch_Drc.check(true, false, true); }} catch(e){{ out.erc_err = e.message; }}

// J1/J2 위치
const comps = await eda.sch_PrimitiveComponent.getAll();
out.pos = {{}};
for (const c of comps) {{
  let des=null; try{{ des = c.designator ?? c.getState_Designator?.(); }}catch(e){{}}
  if (des === 'J1' || des === 'J2') out.pos[des] = [c.getState_X(), c.getState_Y()];
}}
return out;
"""

def main():
    client = EasyEDAMCPClient()
    if not client.connect():
        print("[ERROR] 브릿지 연결 실패"); sys.exit(1)
    res = client.execute_js(JS)
    print(json.dumps(res, ensure_ascii=False, indent=2, default=str))

if __name__ == "__main__":
    main()
