#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""비파괴: 메뉴/툴 API로 Update PCB(Import Changes) 명령 후보 탐색 + 넷리스트 비교."""
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
try { out.sys_HeaderMenu = methods(eda.sys_HeaderMenu); } catch(e){ out.hm_err=e.message; }
try { out.sys_Tool = methods(eda.sys_Tool); } catch(e){ out.tool_err=e.message; }
try { out.pcb_Document = methods(eda.pcb_Document); } catch(e){ out.pd_err=e.message; }
try { out.sch_Document = methods(eda.sch_Document); } catch(e){ out.sd_err=e.message; }

// netlistComparison 시그니처
try { out.netlistComparison_src = eda.sys_Tool.netlistComparison.toString().slice(0,400); } catch(e){}
try { out.pcbComparison_src = eda.sys_Tool.pcbComparison.toString().slice(0,400); } catch(e){}
return out;
"""

def main():
    client = EasyEDAMCPClient()
    if not client.connect():
        print("[ERROR] 브릿지 연결 실패"); sys.exit(1)
    res = client.execute_js(JS)
    with open("probe_menu_out.json","w",encoding="utf-8") as f:
        json.dump(res,f,ensure_ascii=False,indent=2)
    print("WROTE probe_menu_out.json")

if __name__ == "__main__":
    main()
