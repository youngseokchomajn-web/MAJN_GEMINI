#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""라이브 회로도에서 실제 넷리스트 + 부품/핀 메타를 추출(읽기 전용).
- getNetlist("JLCEDA") 우선, 실패 시 다른 포맷
- 각 part의 핀(number/name) 맵 → 스펙 핀이름 대조에 사용
파일로 저장 (콘솔 cp949 인코딩 회피)."""
import sys, json
from easyeda_mcp_client import EasyEDAMCPClient

JS_NET = r"""
const out = {};
try {
  const pages = await eda.dmt_Schematic.getAllSchematicPagesInfo();
  out.pageCount = (pages||[]).length;
  if (pages && pages.length){
    await eda.dmt_EditorControl.openDocument(pages[0].uuid);
    await new Promise(r=>setTimeout(r,1200));
    await eda.dmt_EditorControl.activateDocument(pages[0].uuid);
    await new Promise(r=>setTimeout(r,1500));
    out.activated = pages[0].uuid;
  }
} catch(e){ out.activate_err = e.message; }

out.netlistFmt = null;
out.netlist = null;
for (const fmt of ["JLCEDA","EasyEDA"]) {
  try {
    const r = await eda.sch_Netlist.getNetlist(fmt);
    if (r && typeof r === 'string' && r.length > 2){ out.netlistFmt = fmt; out.netlist = r; break; }
    if (r && typeof r === 'object'){ out.netlistFmt = fmt; out.netlist = JSON.stringify(r); break; }
  } catch(e){ out["err_"+fmt] = e.message; }
}
return out;
"""

def main():
    client = EasyEDAMCPClient()
    if not client.connect():
        print("[ERROR] bridge connect failed"); sys.exit(1)
    res = client.execute_js(JS_NET)
    nl = res.pop("netlist", None)
    with open("fetch_sch_meta.json","w",encoding="utf-8") as f:
        json.dump(res,f,ensure_ascii=False,indent=2,default=str)
    if nl:
        with open("netlist_sch_live.json","w",encoding="utf-8") as f:
            f.write(nl)
        print("[OK] netlist_sch_live.json len=%d fmt=%s" % (len(nl), res.get("netlistFmt")))
    else:
        print("[WARN] netlist extract failed. meta:", json.dumps({k:v for k,v in res.items()}, ensure_ascii=True)[:400])

if __name__ == "__main__":
    main()
