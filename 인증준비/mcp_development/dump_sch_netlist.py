#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""save() + sch_ManufactureData.getNetlistFile 로 회로도 실제 넷리스트를 파일로 덤프.
(getNetlist 는 hang 하므로 getNetlistFile 경로 사용 — verify_sch_netlist.py 와 동일.)"""
import sys, json
from easyeda_mcp_client import EasyEDAMCPClient

JS = r"""
try {
  const pages = await eda.dmt_Schematic.getAllSchematicPagesInfo();
  if (!pages || !pages.length) return {success:false,error:"no pages"};
  await eda.dmt_EditorControl.openDocument(pages[0].uuid);
  await new Promise(r=>setTimeout(r,1200));
  await eda.dmt_EditorControl.activateDocument(pages[0].uuid);
  await new Promise(r=>setTimeout(r,1200));
  await eda.sch_Document.save();
  await new Promise(r=>setTimeout(r,1500));
  const file = await eda.sch_ManufactureData.getNetlistFile("sch_net","JLCEDA");
  if (!file) return {success:false,error:"netlist file null"};
  const content = await file.text();
  return {success:true, content:content, pageCount:pages.length};
} catch(e){ return {success:false,error:e.message}; }
"""

def main():
    client = EasyEDAMCPClient()
    if not client.connect():
        print("[ERROR] bridge connect failed"); sys.exit(2)
    res = client.execute_js(JS)
    if not res or not res.get("success"):
        print("[ERROR] dump failed:", res.get("error") if res else "no resp"); sys.exit(1)
    content = res["content"]
    with open("netlist_sch_live.json","w",encoding="utf-8") as f:
        f.write(content)
    print(f"[OK] netlist_sch_live.json ({len(content)} chars), pageCount={res.get('pageCount')}")

if __name__ == "__main__":
    main()
