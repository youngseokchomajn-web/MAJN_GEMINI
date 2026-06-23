#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""읽기 전용: PCB 넷규칙/넷클래스 현재 구성 덤프 (트레이스폭 설정 스키마 파악)."""
import sys, json
from easyeda_mcp_client import EasyEDAMCPClient

PCB2 = "821d4e6aff1909c8"
JS = f"""
const out={{}};
try{{
  await eda.dmt_EditorControl.activateDocument("{PCB2}");
  await new Promise(r=>setTimeout(r,800));
}}catch(e){{out.act_err=e.message;}}
try{{ out.currentRuleName = await eda.pcb_Drc.getCurrentRuleConfigurationName(); }}catch(e){{ out.e1=e.message; }}
try{{ out.netByNetRules = await eda.pcb_Drc.getNetByNetRules(); }}catch(e){{ out.e2=e.message; }}
try{{ out.netRules = await eda.pcb_Drc.getNetRules(); }}catch(e){{ out.e3=e.message; }}
try{{ out.netClasses = await eda.pcb_Drc.getAllNetClasses(); }}catch(e){{ out.e4=e.message; }}
try{{ out.overwriteNetByNetRules_src = eda.pcb_Drc.overwriteNetByNetRules.toString().slice(0,400); }}catch(e){{}}
try{{ out.createNetClass_src = eda.pcb_Drc.createNetClass.toString().slice(0,400); }}catch(e){{}}
return out;
"""

def main():
    c = EasyEDAMCPClient()
    if not c.connect(): sys.exit(1)
    res = c.execute_js(JS)
    json.dump(res, open("probe_netrules_out.json","w",encoding="utf-8"), ensure_ascii=False, indent=2, default=str)
    # 요약 출력(긴 구조는 키만)
    for k,v in res.items():
        s = json.dumps(v, ensure_ascii=True, default=str)
        print(f"{k}: {s[:600]}")

if __name__ == "__main__":
    main()
