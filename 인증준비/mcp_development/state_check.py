#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""빠른 PCB 상태 점검: 부품수/라인수/pour수/U3."""
import sys, json
from easyeda_mcp_client import EasyEDAMCPClient

PCB_UUID = "c9f1fdba7e0a3f4c"
JS = f"""
const out = {{}};
try {{
  const cd = await eda.dmt_SelectControl.getCurrentDocumentInfo();
  out.curDoc = cd ? {{type:cd.documentType, uuid:cd.uuid}} : null;
}} catch(e){{}}
try {{ const c = await eda.pcb_PrimitiveComponent.getAll(); out.compCount=(c||[]).length;
  out.des=[]; for (const x of c){{let d=null;try{{d=x.designator??x.getState_Designator?.();}}catch(e){{}} out.des.push(d);}} out.des.sort();
  out.hasU3 = out.des.includes('U3');
}} catch(e){{ out.comp_err=e.message; }}
try {{ const l = await eda.pcb_PrimitiveLine.getAll(); out.lines=(l||[]).length; }} catch(e){{ out.line_err=e.message; }}
try {{ const p = await eda.pcb_PrimitivePour.getAll(); out.pours=(p||[]).length; }} catch(e){{ out.pour_err=e.message; }}
return out;
"""

def main():
    client = EasyEDAMCPClient()
    if not client.connect():
        print("[ERROR] 브릿지 연결 실패"); sys.exit(1)
    print(json.dumps(client.execute_js(JS), ensure_ascii=False, indent=2, default=str))

if __name__ == "__main__":
    main()
