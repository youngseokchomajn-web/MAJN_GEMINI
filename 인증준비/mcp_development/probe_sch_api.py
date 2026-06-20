#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Phase 1a: 회로도 연결/넷리스트 관련 EDA API 표면 정밀 조사 (읽기 전용).
- eda.sch_Netlist 의 메서드 목록 (setNetlist 존재 여부 = 직접주입 가능성)
- 네트포트/네트플래그/네트라벨 생성 API 목록
- 핀별 net 읽기 가능 메서드(getState_Net 등) 탐색
- getNetlist 가 받는 포맷 후보 시도 결과
PCB/회로도 어느 것도 수정하지 않음."""
import sys, json
from easyeda_mcp_client import EasyEDAMCPClient

PROBE_JS = r"""
const out = {};
function methodsOf(obj){
  const set = new Set();
  let o = obj;
  for (let i=0;i<3 && o;i++){
    try { Object.getOwnPropertyNames(o).forEach(m=>{ try{ if(typeof obj[m]==='function') set.add(m);}catch(e){} }); }
    catch(e){}
    o = Object.getPrototypeOf(o);
  }
  return Array.from(set).sort();
}

// 1) sch_Netlist 메서드
try { out.sch_Netlist_methods = eda.sch_Netlist ? methodsOf(eda.sch_Netlist) : "MISSING"; }
catch(e){ out.sch_Netlist_err = e.message; }

// 2) sch_PrimitiveComponent 메서드 (netport/netflag/netlabel 생성 API)
try {
  const m = eda.sch_PrimitiveComponent ? methodsOf(eda.sch_PrimitiveComponent) : "MISSING";
  out.sch_PrimitiveComponent_net_methods = Array.isArray(m)
    ? m.filter(x=>/net|flag|port|label|pin/i.test(x)) : m;
} catch(e){ out.sch_PrimComp_err = e.message; }

// 3) netlabel/netport 전용 네임스페이스 존재?
out.has_NetLabel_ns = !!eda.sch_PrimitiveNetLabel;
out.has_NetPort_ns  = !!eda.sch_PrimitiveNetPort;
out.has_NetFlag_ns  = !!eda.sch_PrimitiveNetFlag;
if (eda.sch_PrimitiveNetLabel) out.NetLabel_methods = methodsOf(eda.sch_PrimitiveNetLabel);
if (eda.sch_PrimitiveNetPort)  out.NetPort_methods  = methodsOf(eda.sch_PrimitiveNetPort);

// 4) 핀 객체에서 net 읽기 가능한가 — 첫 part 1개의 첫 핀 메서드 조사
try {
  const comps = await eda.sch_PrimitiveComponent.getAll();
  out.totalPrimitives = (comps||[]).length;
  let sampleParts = (comps||[]).filter(c=>{ try{return c.getState_ComponentType&&c.getState_ComponentType()==='part';}catch(e){return false;} });
  out.partCount = sampleParts.length;
  if (sampleParts.length){
    const c = sampleParts[0];
    out.sampleDes = c.getState_Designator ? c.getState_Designator() : null;
    const pins = await eda.sch_PrimitiveComponent.getAllPinsByPrimitiveId(c.getState_PrimitiveId());
    if (pins && pins.length){
      out.pin_methods = methodsOf(pins[0]).filter(x=>/net|state/i.test(x));
    }
  }
} catch(e){ out.pinprobe_err = e.message; }

// 5) getNetlist 포맷 후보 시도 (현재 회로도가 깨져 throw 날 수 있음 — 메시지만 수집)
out.getNetlist_try = {};
for (const fmt of ["JLCEDA","EasyEDA","Spice","Protel","Protel2","PADS","Allegro"]) {
  try { const r = await eda.sch_Netlist.getNetlist(fmt); out.getNetlist_try[fmt] = (typeof r==='string')? ("OK len="+r.length) : ("OK type="+typeof r); }
  catch(e){ out.getNetlist_try[fmt] = "ERR:"+e.message; }
}
return out;
"""

def main():
    client = EasyEDAMCPClient()
    if not client.connect():
        print("[ERROR] 브릿지 연결 실패"); sys.exit(1)
    res = client.execute_js(PROBE_JS)
    with open("probe_sch_api_out.json","w",encoding="utf-8") as f:
        json.dump(res,f,ensure_ascii=False,indent=2,default=str)
    print(json.dumps(res, ensure_ascii=False, indent=2, default=str))

if __name__ == "__main__":
    main()
