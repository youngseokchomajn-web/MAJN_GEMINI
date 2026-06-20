#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""읽기 전용: No-Connect 깃발 부착 API + 회로도 페이지 삭제 API 탐색."""
import sys, json
from easyeda_mcp_client import EasyEDAMCPClient

JS = r"""
const out={};
function methods(o){let m=[];try{m=Object.getOwnPropertyNames(o).filter(k=>{try{return typeof o[k]==='function'}catch(e){return false}});}catch(e){}
  try{const p=Object.getPrototypeOf(o);if(p)m=m.concat(Object.getOwnPropertyNames(p).filter(k=>{try{return typeof o[k]==='function'}catch(e){return false}}));}catch(e){}
  return Array.from(new Set(m)).sort();}

// 활성화
try{const pages=await eda.dmt_Schematic.getAllSchematicPagesInfo();
  if(pages&&pages.length){await eda.dmt_EditorControl.activateDocument(pages[0].uuid);await new Promise(r=>setTimeout(r,800));}
}catch(e){out.act_err=e.message;}

// sch_PrimitiveComponent 전체 메서드 + NC 관련
try{ const m=methods(eda.sch_PrimitiveComponent); out.comp_nc = m.filter(x=>/noconn|nc|connect|flag/i.test(x)); out.comp_all=m; }catch(e){out.comp_err=e.message;}

// 핀 객체 setState 메서드 (NoConnected 세터 존재?)
try{
  const cs=await eda.sch_PrimitiveComponent.getAll();
  let part=null; for(const c of (cs||[])){let t='?';try{t=c.getState_ComponentType&&c.getState_ComponentType();}catch(e){} if(t==='part'){part=c;break;}}
  if(part){
    const pins=await eda.sch_PrimitiveComponent.getAllPinsByPrimitiveId(part.getState_PrimitiveId());
    if(pins&&pins.length){ out.pin_methods = methods(pins[0]).filter(x=>/set|noconn|connect/i.test(x)); }
  }
}catch(e){out.pin_err=e.message;}

// dmt_Schematic / dmt_EditorControl 페이지 삭제 메서드
try{ out.dmtSch = methods(eda.dmt_Schematic).filter(x=>/del|remove|page/i.test(x)); }catch(e){out.dmtSch_err=e.message;}
try{ out.dmtEd = methods(eda.dmt_EditorControl).filter(x=>/del|remove|page|close|doc/i.test(x)); }catch(e){out.dmtEd_err=e.message;}

return out;
"""

def main():
    client = EasyEDAMCPClient()
    if not client.connect():
        print("[ERROR] bridge connect failed"); sys.exit(1)
    res = client.execute_js(JS)
    with open("probe_nc_delete_out.json","w",encoding="utf-8") as f:
        json.dump(res,f,ensure_ascii=False,indent=2,default=str)
    print(json.dumps({k:v for k,v in res.items() if k!='comp_all'}, ensure_ascii=True, indent=2, default=str))
    print("\ncomp_all:", res.get("comp_all"))

if __name__ == "__main__":
    main()
