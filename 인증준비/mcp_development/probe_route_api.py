#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""읽기 전용: PCB 라우팅/오토라우터/넷규칙(트레이스폭) API 탐색."""
import sys, json
from easyeda_mcp_client import EasyEDAMCPClient

JS = r"""
const out={namespaces:{}, hits:{}};
const KEYS=['route','autorout','width','rule','clearance','net','ratline','drc','design'];
for(const ns of Object.keys(eda)){
  if(!/pcb/i.test(ns)) continue;
  let m=[];
  try{const o=eda[ns]; if(o){ m=Object.getOwnPropertyNames(o).filter(k=>{try{return typeof o[k]==='function'}catch(e){return false}});
    const p=Object.getPrototypeOf(o); if(p)m=m.concat(Object.getOwnPropertyNames(p).filter(k=>{try{return typeof o[k]==='function'}catch(e){return false}}));}}catch(e){}
  m=Array.from(new Set(m));
  const hit=m.filter(k=>KEYS.some(x=>k.toLowerCase().includes(x)));
  if(hit.length) out.hits[ns]=hit;
}
// 라우팅 전용 네임스페이스 후보
out.routeNamespaces = Object.keys(eda).filter(k=>/rout|wir|track|trace/i.test(k));
// pcb_Drc 메서드
try{ out.pcb_Drc = Object.getOwnPropertyNames(Object.getPrototypeOf(eda.pcb_Drc)).filter(k=>typeof eda.pcb_Drc[k]==='function'); }catch(e){ out.pcbDrc_err=e.message; }
// design rule 네임스페이스
out.ruleNamespaces = Object.keys(eda).filter(k=>/rule|design|setting|spec/i.test(k));
return out;
"""

def main():
    c = EasyEDAMCPClient()
    if not c.connect(): sys.exit(1)
    res = c.execute_js(JS)
    json.dump(res, open("probe_route_api_out.json","w",encoding="utf-8"), ensure_ascii=False, indent=2, default=str)
    print(json.dumps(res, ensure_ascii=True, indent=2, default=str))

if __name__ == "__main__":
    main()
