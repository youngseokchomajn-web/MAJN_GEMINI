#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ERC 경고 2건의 상세 추출 시도(읽기 전용).
- sch_ManufactureData 메서드 목록(ERC/DRC 리포트 파일 가능성)
- sch_Drc.check 의 반환 구조를 그대로 깊게 덤프
- includeVerboseError 조합 시도"""
import sys, json
from easyeda_mcp_client import EasyEDAMCPClient

JS = r"""
const out={};
function methods(o){let m=[];try{m=Object.getOwnPropertyNames(o).filter(k=>{try{return typeof o[k]==='function'}catch(e){return false}});}catch(e){}
  try{const p=Object.getPrototypeOf(o);if(p)m=m.concat(Object.getOwnPropertyNames(p).filter(k=>{try{return typeof o[k]==='function'}catch(e){return false}}));}catch(e){}
  return Array.from(new Set(m)).sort();}
try{
  const pages=await eda.dmt_Schematic.getAllSchematicPagesInfo();
  if(pages&&pages.length){await eda.dmt_EditorControl.activateDocument(pages[0].uuid);await new Promise(r=>setTimeout(r,800));}
}catch(e){out.act_err=e.message;}
try{ out.manu_methods = methods(eda.sch_ManufactureData); }catch(e){ out.manu_err=e.message; }
// verbose ERC 전체 구조 그대로
try{ out.erc_verbose = await eda.sch_Drc.check(true, false, true); }catch(e){ out.erc_err=e.message; }
// ERC 리포트 파일 시도(있으면)
try{
  if(eda.sch_ManufactureData && eda.sch_ManufactureData.getDrcReport){
    const f=await eda.sch_ManufactureData.getDrcReport(); if(f&&f.text){ out.drcReport=(await f.text()).slice(0,4000); }
  }
}catch(e){ out.drcReport_err=e.message; }
return out;
"""

def main():
    client = EasyEDAMCPClient()
    if not client.connect():
        print("[ERROR] bridge connect failed"); sys.exit(1)
    res = client.execute_js(JS)
    with open("probe_erc_detail_out.json","w",encoding="utf-8") as f:
        json.dump(res,f,ensure_ascii=False,indent=2,default=str)
    print(json.dumps(res, ensure_ascii=True, indent=2, default=str)[:3000])

if __name__ == "__main__":
    main()
