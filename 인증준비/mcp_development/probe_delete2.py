#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""비파괴: 삭제/선택 API(프로토타입 포함) + setState_Component 시그니처 탐색."""
import sys, json
from easyeda_mcp_client import EasyEDAMCPClient

JS = r"""
const out = {};
function allMethods(obj){
  const s = new Set();
  let o = obj;
  for (let i=0;i<4 && o;i++){
    try { Object.getOwnPropertyNames(o).forEach(k=>{ try{ if(typeof obj[k]==='function') s.add(k); }catch(e){} }); } catch(e){}
    o = Object.getPrototypeOf(o);
  }
  return Array.from(s);
}
out.pcb_SelectControl = allMethods(eda.pcb_SelectControl);
out.pcb_PrimitiveComponent_ns = allMethods(eda.pcb_PrimitiveComponent);
out.pcb_Primitive = allMethods(eda.pcb_Primitive);
out.pcb_PrimitiveObject = eda.pcb_PrimitiveObject ? allMethods(eda.pcb_PrimitiveObject) : 'none';

// setState_Component / delete 관련 소스
try {
  const comps = await eda.pcb_PrimitiveComponent.getAll();
  const c = comps[0];
  try { out.setState_Component_src = c.setState_Component.toString().slice(0,300); } catch(e){}
  try { out.reset_src = c.reset.toString().slice(0,200); } catch(e){}
  // delete 류 메서드 있는지
  let dele = [];
  let o = c;
  for (let i=0;i<4 && o;i++){ Object.getOwnPropertyNames(o).forEach(k=>{ if(/delete|remove|destroy/i.test(k)) dele.push(k); }); o=Object.getPrototypeOf(o); }
  out.comp_delete_like = dele;
} catch(e){ out.comp_err=e.message; }

// 전역 delete 관련
let g = [];
for (const ns of Object.keys(eda)) {
  try { const m = allMethods(eda[ns]); m.forEach(x=>{ if(/^delete|^remove|deletePrimitive|removePrimitive/i.test(x)) g.push(ns+'.'+x); }); } catch(e){}
}
out.global_delete_like = g.slice(0,40);
return out;
"""

def main():
    client = EasyEDAMCPClient()
    if not client.connect():
        print("[ERROR] 브릿지 연결 실패"); sys.exit(1)
    res = client.execute_js(JS)
    print(json.dumps(res, ensure_ascii=False, indent=2, default=str))

if __name__ == "__main__":
    main()
