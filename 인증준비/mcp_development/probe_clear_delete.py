#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""비파괴: clearRouting 시그니처 + 컴포넌트 삭제 메서드 탐색 + pour/track API 확인."""
import sys, json
from easyeda_mcp_client import EasyEDAMCPClient

JS = r"""
const out = {};
try { out.clearRouting_src = eda.pcb_Document.clearRouting.toString().slice(0,300); } catch(e){ out.cr_err=e.message; }

// 컴포넌트 인스턴스 메서드 (삭제 후보)
try {
  const comps = await eda.pcb_PrimitiveComponent.getAll();
  if (comps && comps.length) {
    const c = comps[0];
    let methods = [];
    try { methods = Object.getOwnPropertyNames(Object.getPrototypeOf(c)).filter(m=>typeof c[m]==='function'); } catch(e){}
    out.compMethods = methods;
  }
} catch(e){ out.comp_err=e.message; }

// pcb_PrimitiveComponent 정적 메서드
function statics(obj){ try{ return Object.getOwnPropertyNames(obj).filter(k=>typeof obj[k]==='function'); }catch(e){ return []; } }
out.pcb_PrimitiveComponent_static = statics(eda.pcb_PrimitiveComponent);
out.pcb_PrimitivePour_static = statics(eda.pcb_PrimitivePour);
out.pcb_PrimitiveLine_static = statics(eda.pcb_PrimitiveLine);
out.pcb_PrimitiveVia_static = statics(eda.pcb_PrimitiveVia);
out.pcb_SelectControl = statics(eda.pcb_SelectControl);
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
