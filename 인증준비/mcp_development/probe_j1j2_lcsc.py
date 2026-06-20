#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""C124372(J1/J2 스펙 LCSC) 실제 라이브러리 심볼 정체 + P2 페이지 내용 확인(읽기 전용)."""
import sys, json
from easyeda_mcp_client import EasyEDAMCPClient

JS = r"""
const out={};
try{
  const devs = await eda.lib_Device.getByLcscIds(["C124372"]);
  out.devs = (devs||[]).map(d=>({
    supplierId:d.supplierId, name:d.name,
    deviceName:d.deviceName, footprintName:d.footprintName,
    symbolName: d.symbolName, libraryUuid:d.libraryUuid, uuid:d.uuid
  }));
}catch(e){ out.dev_err=e.message; }

// P2 페이지 내용 점검
try{
  const pages = await eda.dmt_Schematic.getAllSchematicPagesInfo();
  out.pages = (pages||[]).map(p=>({uuid:p.uuid,name:p.name}));
  if(pages && pages.length>1){
    await eda.dmt_EditorControl.openDocument(pages[1].uuid);
    await new Promise(r=>setTimeout(r,1000));
    await eda.dmt_EditorControl.activateDocument(pages[1].uuid);
    await new Promise(r=>setTimeout(r,1200));
    const cs = await eda.sch_PrimitiveComponent.getAll();
    const byType={};
    for(const c of (cs||[])){ let t='?'; try{t=c.getState_ComponentType&&c.getState_ComponentType();}catch(e){} byType[t]=(byType[t]||0)+1; }
    out.p2_byType = byType;
    const ws = await eda.sch_PrimitiveWire.getAll(); out.p2_wires=(ws||[]).length;
  }
  // 다시 P1 활성화
  if(pages && pages.length){ await eda.dmt_EditorControl.activateDocument(pages[0].uuid); }
}catch(e){ out.page_err=e.message; }
return out;
"""

def main():
    client = EasyEDAMCPClient()
    if not client.connect():
        print("[ERROR] bridge connect failed"); sys.exit(1)
    res = client.execute_js(JS)
    with open("probe_j1j2_lcsc_out.json","w",encoding="utf-8") as f:
        json.dump(res,f,ensure_ascii=False,indent=2,default=str)
    print(json.dumps(res, ensure_ascii=True, indent=2, default=str))

if __name__ == "__main__":
    main()
