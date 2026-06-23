#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""전원 넷 트레이스폭 규칙 설정 (스펙 routing_widths_mm 기준).
Track 규칙 추가 → 넷에 할당 → 읽기로 검증. read-modify-write 원자적 수행."""
import sys, json
from easyeda_mcp_client import EasyEDAMCPClient

PCB2 = "821d4e6aff1909c8"
# 스펙 routing_widths_mm
WIDTHS = {"VBUS_5V": 1.2, "PVDD_12V": 1.0, "BOOST_SW": 0.8, "VCC_3V3": 0.25}

JS = f"""
const out={{}};
const WIDTHS = {json.dumps(WIDTHS)};
try{{
  await eda.dmt_EditorControl.activateDocument("{PCB2}");
  await new Promise(r=>setTimeout(r,800));
}}catch(e){{out.act_err=e.message;}}

function mkTrack(name,w){{
  return {{editName:name, unit:"mm", isSetDefault:false,
    form:{{status:1, data:{{"1":{{minValue:w, defaultValue:w, maxValue:2.54}}}}}}}};
}}
const ruleNameOf = {{}};  // net -> trackRuleName

try{{
  // 1) Track 규칙 추가
  const cfg = await eda.pcb_Drc.getCurrentRuleConfiguration();
  const trackRules = cfg.config.Physics.Track;
  for(const net of Object.keys(WIDTHS)){{
    const rn = "W_"+net;
    ruleNameOf[net]=rn;
    trackRules[rn] = mkTrack(rn, WIDTHS[net]);
  }}
  await eda.pcb_Drc.overwriteCurrentRuleConfiguration(cfg);
  out.addedTrackRules = Object.keys(ruleNameOf).map(n=>ruleNameOf[n]);

  // 2) 넷에 Track 규칙 할당
  const nr = await eda.pcb_Drc.getNetRules();
  let assigned=[];
  for(const r of nr){{
    if(r.name && WIDTHS[r.name]!==undefined){{
      r.Track = ruleNameOf[r.name];
      assigned.push(r.name+"->"+r.Track);
    }}
  }}
  await eda.pcb_Drc.overwriteNetRules(nr);
  out.assigned = assigned;

  // 3) 검증: 되읽기
  const cfg2 = await eda.pcb_Drc.getCurrentRuleConfiguration();
  const tr2 = cfg2.config.Physics.Track;
  out.verify_rules = {{}};
  for(const net of Object.keys(WIDTHS)){{
    const rn = ruleNameOf[net];
    const d = tr2[rn] && tr2[rn].form && tr2[rn].form.data && tr2[rn].form.data["1"];
    out.verify_rules[rn] = d ? d.defaultValue : "MISSING";
  }}
  const nr2 = await eda.pcb_Drc.getNetRules();
  out.verify_assign = {{}};
  for(const r of nr2){{ if(WIDTHS[r.name]!==undefined) out.verify_assign[r.name]=r.Track; }}
}}catch(e){{ out.err=e.message; out.stack=e.stack; }}
return out;
"""

def main():
    c = EasyEDAMCPClient()
    if not c.connect(): sys.exit(1)
    res = c.execute_js(JS)
    json.dump(res, open("set_power_widths_out.json","w",encoding="utf-8"), ensure_ascii=False, indent=2, default=str)
    print(json.dumps(res, ensure_ascii=True, indent=2, default=str))

if __name__ == "__main__":
    main()
