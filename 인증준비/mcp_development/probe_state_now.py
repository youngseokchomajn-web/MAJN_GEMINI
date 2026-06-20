#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""읽기 전용 · 빠름(getNetlist 미사용): 현재 라이브 회로도 특성화.
- 현재 schematic page uuid
- 프리미티브 분류: part / netflag / netport / wire / 기타
- part designator 목록 + 중복(겹침) 검출
- 와이어 수
결과 파일 저장."""
import sys, json
from easyeda_mcp_client import EasyEDAMCPClient

JS = r"""
const out = {};
try {
  const pages = await eda.dmt_Schematic.getAllSchematicPagesInfo();
  out.pages = (pages||[]).map(p=>({uuid:p.uuid,name:p.name}));
  if (pages && pages.length){
    await eda.dmt_EditorControl.openDocument(pages[0].uuid);
    await new Promise(r=>setTimeout(r,800));
    await eda.dmt_EditorControl.activateDocument(pages[0].uuid);
    await new Promise(r=>setTimeout(r,1000));
  }
} catch(e){ out.activate_err = e.message; }

try {
  const comps = await eda.sch_PrimitiveComponent.getAll();
  out.totalPrimComp = (comps||[]).length;
  const byType = {};
  const partDes = {};   // designator -> count (중복 검출)
  const netFlagNames = {};
  const netPortNames = {};
  for (const c of (comps||[])){
    let t = '?';
    try { t = c.getState_ComponentType ? c.getState_ComponentType() : '?'; } catch(e){}
    byType[t] = (byType[t]||0)+1;
    if (t === 'part'){
      let d=null; try{ d=c.getState_Designator&&c.getState_Designator(); }catch(e){}
      if (d) partDes[d] = (partDes[d]||0)+1;
    } else {
      // netflag/netport 이름 수집
      let nm=null;
      try { nm = c.getState_Name ? c.getState_Name() : null; } catch(e){}
      if (nm==null){ try { nm = c.getState_NetName ? c.getState_NetName() : null; } catch(e){} }
      if (t && /flag/i.test(t)) netFlagNames[nm] = (netFlagNames[nm]||0)+1;
      else if (t && /port/i.test(t)) netPortNames[nm] = (netPortNames[nm]||0)+1;
    }
  }
  out.byType = byType;
  out.partCount = Object.keys(partDes).length;
  out.partDes = Object.keys(partDes).sort();
  out.dupDes = Object.entries(partDes).filter(([k,v])=>v>1);
  out.netFlagNames = netFlagNames;
  out.netPortNames = netPortNames;
} catch(e){ out.comp_err = e.message; }

try { const w = await eda.sch_PrimitiveWire.getAll(); out.wireCount=(w||[]).length; }
catch(e){ out.wire_err = e.message; }

return out;
"""

def main():
    client = EasyEDAMCPClient()
    if not client.connect():
        print("[ERROR] bridge connect failed"); sys.exit(1)
    res = client.execute_js(JS)
    with open("probe_state_now_out.json","w",encoding="utf-8") as f:
        json.dump(res,f,ensure_ascii=False,indent=2,default=str)
    print("[OK] wrote probe_state_now_out.json")
    print("partCount=", res.get("partCount"), "totalPrimComp=", res.get("totalPrimComp"),
          "wires=", res.get("wireCount"), "byType=", res.get("byType"))
    if res.get("dupDes"):
        print("DUP designators:", res.get("dupDes"))

if __name__ == "__main__":
    main()
