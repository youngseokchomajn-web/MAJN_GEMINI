#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""비파괴: 회로도를 활성화한 뒤 회로도 넷리스트 추출."""
import sys, json
from easyeda_mcp_client import EasyEDAMCPClient

JS = r"""
const out = {};
// 회로도 문서 찾기 + 활성화
try {
  const schs = await eda.dmt_Schematic.getAllSchematicsInfo();
  out.schInfo = schs;
  // 활성화는 페이지 문서 uuid 필요할 수 있음 -> 현재 문서 정보로 시도
} catch(e){ out.schInfo_err = e.message; }
try {
  const pages = await eda.dmt_Schematic.getAllSchematicPagesInfo
    ? await eda.dmt_Schematic.getAllSchematicPagesInfo()
    : null;
  out.pages = pages;
  if (pages && pages.length && pages[0].uuid) {
    await eda.dmt_EditorControl.openDocument(pages[0].uuid);
    await new Promise(r=>setTimeout(r,1500));
    await eda.dmt_EditorControl.activateDocument(pages[0].uuid);
    await new Promise(r=>setTimeout(r,2000));
    out.activated = pages[0].uuid;
  }
} catch(e){ out.pages_err = e.message; }

let netlist = null;
for (const fmt of ["JLCEDA","Protel2","PADS"]) {
  try { netlist = await eda.sch_Netlist.getNetlist(fmt); if (netlist) { out.usedFormat = fmt; break; } }
  catch(e){ out["err_"+fmt] = e.message; }
}
out.netlist = netlist;
return out;
"""

def main():
    client = EasyEDAMCPClient()
    if not client.connect():
        print("[ERROR] 브릿지 연결 실패"); sys.exit(1)
    res = client.execute_js(JS)
    nl = res.pop("netlist", None)
    with open("probe_sch_meta.json", "w", encoding="utf-8") as f:
        json.dump(res, f, ensure_ascii=False, indent=2)
    if nl:
        with open("netlist_sch.json", "w", encoding="utf-8") as f:
            f.write(nl)
        print(f"[OK] netlist_sch.json ({len(nl)} chars), format={res.get('usedFormat')}")
    else:
        print("[WARN] 회로도 넷리스트 추출 실패. probe_sch_meta.json 확인")

if __name__ == "__main__":
    main()
