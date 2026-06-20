#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""비파괴: sch_Drc(ERC) API 메서드/시그니처 확인."""
import sys, json
from easyeda_mcp_client import EasyEDAMCPClient

JS = r"""
const out = {};
function methods(obj){
  let m=[];
  try{ m=Object.getOwnPropertyNames(obj).filter(k=>typeof obj[k]==='function'); }catch(e){}
  try{ const p=Object.getPrototypeOf(obj); if(p) m=m.concat(Object.getOwnPropertyNames(p).filter(k=>typeof obj[k]==='function')); }catch(e){}
  return Array.from(new Set(m));
}
try { out.sch_Drc = methods(eda.sch_Drc); } catch(e){ out.err=e.message; }
try { out.check_src = eda.sch_Drc.check.toString().slice(0,500); } catch(e){}
return out;
"""

def main():
    client = EasyEDAMCPClient()
    if not client.connect():
        print("[ERROR] 브릿지 연결 실패"); sys.exit(1)
    res = client.execute_js(JS)
    print(json.dumps(res, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()
