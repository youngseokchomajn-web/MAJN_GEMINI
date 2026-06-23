#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""읽기 전용: 자동배선(JRouter) API 경로 정밀 조사.
- pcb_Document / pcb_ManufactureData 전체 메서드
- autoroute/jrouter/route 관련 메서드 소스
- 전체 eda 네임스페이스에서 route/auto/jrouter 검색"""
import sys, json
from easyeda_mcp_client import EasyEDAMCPClient

PCB2 = "821d4e6aff1909c8"
JS = f"""
const out={{}};
function meths(o){{let m=[];try{{m=Object.getOwnPropertyNames(o).filter(k=>{{try{{return typeof o[k]==='function'}}catch(e){{return false}}}});}}catch(e){{}}
  try{{const p=Object.getPrototypeOf(o);if(p)m=m.concat(Object.getOwnPropertyNames(p).filter(k=>{{try{{return typeof o[k]==='function'}}catch(e){{return false}}}}));}}catch(e){{}}
  return Array.from(new Set(m)).sort();}}
try{{ await eda.dmt_EditorControl.activateDocument("{PCB2}"); await new Promise(r=>setTimeout(r,800)); }}catch(e){{out.act_err=e.message;}}

out.pcb_Document = meths(eda.pcb_Document);
out.pcb_ManufactureData = meths(eda.pcb_ManufactureData);

// 전체 네임스페이스에서 route/auto/jrouter
out.hits={{}};
for(const ns of Object.keys(eda)){{
  let m=[];
  try{{const o=eda[ns]; if(o){{ m=meths(o); }}}}catch(e){{}}
  const hit=m.filter(k=>/rout|jrouter|autoroute|auto_route/i.test(k));
  if(hit.length) out.hits[ns]=hit;
}}

// 소스 일부
const srcOf=(o,n)=>{{try{{return o[n].toString().slice(0,500);}}catch(e){{return 'ERR:'+e.message;}}}};
out.src={{}};
out.src.getAutoRouteJsonFileForJRouter = srcOf(eda.pcb_ManufactureData,'getAutoRouteJsonFileForJRouter');
out.src.getAutoRouteJsonFile = srcOf(eda.pcb_ManufactureData,'getAutoRouteJsonFile');
out.src.importAutoRouteJsonFile = srcOf(eda.pcb_Document,'importAutoRouteJsonFile');
out.src.importAutoRouteSesFile = srcOf(eda.pcb_Document,'importAutoRouteSesFile');
return out;
"""

def main():
    c = EasyEDAMCPClient()
    if not c.connect(): sys.exit(1)
    res = c.execute_js(JS)
    json.dump(res, open("probe_autoroute_api_out.json","w",encoding="utf-8"), ensure_ascii=False, indent=2, default=str)
    print("=== hits (route/auto/jrouter) ===")
    print(json.dumps(res.get("hits",{}), ensure_ascii=True, indent=2))
    print("\n=== pcb_Document methods ===")
    print(res.get("pcb_Document"))
    print("\n=== pcb_ManufactureData methods ===")
    print(res.get("pcb_ManufactureData"))
    print("\n=== sources ===")
    for k,v in res.get("src",{}).items():
        print(f"--- {k} ---\n{v}\n")

if __name__ == "__main__":
    main()
