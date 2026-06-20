#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""읽기 전용: No-Connect 깃발 생성 API 정밀 탐색.
- createNetFlag / createShortCircuitFlag 소스(허용 type 문자열)
- 전체 eda 네임스페이스에서 noconnect/noconn 관련 메서드
- modify 소스"""
import sys, json
from easyeda_mcp_client import EasyEDAMCPClient

JS = r"""
const out={};
try{ out.createNetFlag_src = eda.sch_PrimitiveComponent.createNetFlag.toString().slice(0,700); }catch(e){out.e1=e.message;}
try{ out.createShortCircuitFlag_src = eda.sch_PrimitiveComponent.createShortCircuitFlag.toString().slice(0,700); }catch(e){out.e2=e.message;}
try{ out.modify_src = eda.sch_PrimitiveComponent.modify.toString().slice(0,500); }catch(e){out.e3=e.message;}
// 전체 네임스페이스에서 noconnect 관련
out.nc_methods={};
for(const ns of Object.keys(eda)){
  let m=[];
  try{ const o=eda[ns]; if(o){ m=Object.getOwnPropertyNames(o).filter(k=>{try{return typeof o[k]==='function'}catch(e){return false}});
    const proto=Object.getPrototypeOf(o); if(proto) m=m.concat(Object.getOwnPropertyNames(proto).filter(k=>{try{return typeof o[k]==='function'}catch(e){return false}})); } }catch(e){}
  const hit=m.filter(k=>/noconn|no_connect|nonconnect|connect/i.test(k));
  if(hit.length) out.nc_methods[ns]=Array.from(new Set(hit));
}
// NoConnect 전용 네임스페이스?
out.ns_with_nc = Object.keys(eda).filter(k=>/noconn|connect/i.test(k));
return out;
"""

def main():
    client = EasyEDAMCPClient()
    if not client.connect(): sys.exit(1)
    res = client.execute_js(JS)
    with open("probe_ncflag_api_out.json","w",encoding="utf-8") as f:
        json.dump(res,f,ensure_ascii=False,indent=2,default=str)
    print(json.dumps(res, ensure_ascii=True, indent=2, default=str))

if __name__ == "__main__":
    main()
