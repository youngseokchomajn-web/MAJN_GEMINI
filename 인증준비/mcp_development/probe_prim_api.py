#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""읽기 전용: 회로도 프리미티브의 state getter API + 샘플값 1개씩 덤프.
- wire: 꼭짓점/좌표 getter
- netport: 이름/좌표 getter
- netflag: 종류/이름/좌표 getter
- pin: 연결점 좌표/번호/이름
union-find 기하 재구성을 위해 필요한 메서드 확정용."""
import sys, json
from easyeda_mcp_client import EasyEDAMCPClient

JS = r"""
const out = {};
function getters(obj){
  const set=new Set(); let o=obj;
  for(let i=0;i<4&&o;i++){ try{Object.getOwnPropertyNames(o).forEach(m=>{try{if(typeof obj[m]==='function'&&/^getState_/.test(m))set.add(m);}catch(e){}});}catch(e){} o=Object.getPrototypeOf(o); }
  return Array.from(set).sort();
}
async function callAll(obj, names){
  const r={};
  for(const m of names){ try{ let v=obj[m](); if(v&&typeof v.then==='function') v=await v; r[m]=v; }catch(e){ r[m]='ERR:'+e.message; } }
  return r;
}

try{
  const pages=await eda.dmt_Schematic.getAllSchematicPagesInfo();
  if(pages&&pages.length){ await eda.dmt_EditorControl.activateDocument(pages[0].uuid); await new Promise(r=>setTimeout(r,800)); }
}catch(e){out.act_err=e.message;}

// WIRE 샘플
try{
  const w=await eda.sch_PrimitiveWire.getAll();
  if(w&&w.length){ const g=getters(w[0]); out.wire_getters=g; out.wire_sample=await callAll(w[0],g); }
}catch(e){out.wire_err=e.message;}

// 컴포넌트들 중 netport/netflag 샘플
try{
  const cs=await eda.sch_PrimitiveComponent.getAll();
  let port=null, flag=null, part=null;
  for(const c of (cs||[])){
    let t='?'; try{t=c.getState_ComponentType&&c.getState_ComponentType();}catch(e){}
    if(t==='netport'&&!port)port=c;
    else if(t==='netflag'&&!flag)flag=c;
    else if(t==='part'&&!part)part=c;
  }
  if(port){ const g=getters(port); out.netport_getters=g; out.netport_sample=await callAll(port,g); }
  if(flag){ const g=getters(flag); out.netflag_getters=g; out.netflag_sample=await callAll(flag,g); }
  if(part){
    out.part_des = part.getState_Designator&&part.getState_Designator();
    const pins=await eda.sch_PrimitiveComponent.getAllPinsByPrimitiveId(part.getState_PrimitiveId());
    if(pins&&pins.length){ const g=getters(pins[0]); out.pin_getters=g; out.pin_sample=await callAll(pins[0],g); }
  }
}catch(e){out.comp_err=e.message;}

return out;
"""

def main():
    client = EasyEDAMCPClient()
    if not client.connect():
        print("[ERROR] bridge connect failed"); sys.exit(1)
    res = client.execute_js(JS)
    with open("probe_prim_api_out.json","w",encoding="utf-8") as f:
        json.dump(res,f,ensure_ascii=False,indent=2,default=str)
    print("[OK] wrote probe_prim_api_out.json")

if __name__ == "__main__":
    main()
