#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""비파괴: U3 스펙 LCSC(C2909511)가 14핀 풋프린트를 주는지 검증.
+ 현재 PCB의 U3 패드 수 확인."""
import sys, json
from easyeda_mcp_client import EasyEDAMCPClient

JS = r"""
const out = {};
const LCSC = "C2909511";
// 1. 디바이스 조회
try {
  const devs = await eda.lib_Device.getByLcscIds([LCSC]);
  if (devs && devs.length && devs[0]) {
    const d = devs[0];
    out.deviceFound = true;
    // 풋프린트 정보
    try {
      const fp = d.footprint ?? (d.getState_Footprint?.());
      out.footprintRaw = fp ? (fp.name || fp.title || JSON.stringify(fp).slice(0,200)) : null;
    } catch(e){ out.fp_err = e.message; }
    // 디바이스 키 덤프
    try { out.deviceKeys = Object.keys(d).slice(0,40); } catch(e){}
  } else {
    out.deviceFound = false;
  }
} catch(e){ out.dev_err = e.message; }

// 2. 현재 PCB U3 패드 수
try {
  const pcbs = await eda.dmt_Pcb.getAllPcbsInfo();
  if (pcbs && pcbs.length) {
    await eda.dmt_EditorControl.openDocument(pcbs[0].uuid);
    await new Promise(r=>setTimeout(r,1200));
    await eda.dmt_EditorControl.activateDocument(pcbs[0].uuid);
    await new Promise(r=>setTimeout(r,1500));
  }
  const comps = await eda.pcb_PrimitiveComponent.getAll();
  for (const c of (comps||[])) {
    let des=null; try{ des = c.designator ?? c.getState_Designator?.(); }catch(e){}
    if (des === 'U3') {
      try {
        const pads = await eda.pcb_PrimitiveComponent.getAllPinsByPrimitiveId(c.getState_PrimitiveId());
        out.pcb_U3_padCount = (pads||[]).length;
        out.pcb_U3_padNumbers = (pads||[]).map(p=>p.padNumber);
      } catch(e){ out.u3pad_err = e.message; }
      try { out.pcb_U3_lcsc = c.getState_SupplierId?.() ?? c.getState_Supplier?.(); } catch(e){}
      break;
    }
  }
} catch(e){ out.pcb_err = e.message; }

return out;
"""

def main():
    client = EasyEDAMCPClient()
    if not client.connect():
        print("[ERROR] 브릿지 연결 실패"); sys.exit(1)
    res = client.execute_js(JS)
    with open("verify_u3_out.json","w",encoding="utf-8") as f:
        json.dump(res,f,ensure_ascii=False,indent=2,default=str)
    print(json.dumps(res, ensure_ascii=False, indent=2, default=str))

if __name__ == "__main__":
    main()
