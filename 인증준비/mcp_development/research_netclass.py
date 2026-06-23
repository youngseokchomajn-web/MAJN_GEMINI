#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""연구: 넷클래스 생성 시 트랙폭이 어디에/어떻게 저장되는지 실증 조사.
테스트 클래스 1개 생성 → 구조 덤프 → (조사 후 별도로 삭제)."""
import sys, json
from easyeda_mcp_client import EasyEDAMCPClient

PCB2 = "821d4e6aff1909c8"
JS = f"""
const out={{}};
try{{ await eda.dmt_EditorControl.activateDocument("{PCB2}"); await new Promise(r=>setTimeout(r,800)); }}catch(e){{out.act_err=e.message;}}

// createNetClass 시그니처
try{{ out.createNetClass_src = eda.pcb_Drc.createNetClass.toString().slice(0,300); }}catch(e){{}}
try{{ out.addNetToNetClass_src = eda.pcb_Drc.addNetToNetClass.toString().slice(0,300); }}catch(e){{}}

// 생성 전 상태
try{{ out.before_classes = await eda.pcb_Drc.getAllNetClasses(); }}catch(e){{ out.bc_err=e.message; }}

// 테스트 클래스 생성
try{{ out.createRet = await eda.pcb_Drc.createNetClass("PWR_TEST", ["VBUS_5V"], "#FF8800"); }}catch(e){{ out.create_err=e.message; }}
await new Promise(r=>setTimeout(r,500));

// 생성 후 상태 — 클래스/넷규칙/룰구성에서 폭 흔적 찾기
try{{ out.after_classes = await eda.pcb_Drc.getAllNetClasses(); }}catch(e){{ out.ac_err=e.message; }}
try{{
  const nr = await eda.pcb_Drc.getNetRules();
  out.vbus_rule = nr.find(r=>r.name==="VBUS_5V") || null;
  // 넷클래스 타입 엔트리 있나?
  out.classRuleEntries = nr.filter(r=>r.type && r.type!=="net").slice(0,5);
}}catch(e){{ out.nr_err=e.message; }}
try{{
  const cfg = await eda.pcb_Drc.getCurrentRuleConfiguration();
  // Track 규칙에 PWR_TEST 관련 생겼나?
  out.trackKeys = Object.keys(cfg.config.Physics.Track);
}}catch(e){{ out.cfg_err=e.message; }}
return out;
"""

def main():
    c = EasyEDAMCPClient()
    if not c.connect(): sys.exit(1)
    res = c.execute_js(JS)
    json.dump(res, open("research_netclass_out.json","w",encoding="utf-8"), ensure_ascii=False, indent=2, default=str)
    print(json.dumps(res, ensure_ascii=True, indent=2, default=str)[:2500])

if __name__ == "__main__":
    main()
