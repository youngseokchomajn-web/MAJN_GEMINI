#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""PCB2 활성화 후 PCB 넷리스트 추출 → netlist_pcb2.json (읽기 전용)."""
import sys, json
from easyeda_mcp_client import EasyEDAMCPClient

PCB2 = "821d4e6aff1909c8"
JS = f"""
try{{
  await eda.dmt_EditorControl.openDocument("{PCB2}");
  await new Promise(r=>setTimeout(r,1500));
  await eda.dmt_EditorControl.activateDocument("{PCB2}");
  await new Promise(r=>setTimeout(r,1500));
  const nl = await eda.pcb_Net.getNetlist("JLCEDA");
  return {{success:true, content:nl}};
}}catch(e){{ return {{success:false, error:e.message}}; }}
"""

def main():
    c = EasyEDAMCPClient()
    if not c.connect(): sys.exit(2)
    r = c.execute_js(JS)
    if not r or not r.get("success"):
        print("[ERROR]", r.get("error") if r else "no resp"); sys.exit(1)
    content = r["content"]
    if isinstance(content, list):
        if content and all(isinstance(x, str) for x in content):
            content = "\n".join(content)
        else:
            content = json.dumps(content, ensure_ascii=False)
    open("netlist_pcb2.json","w",encoding="utf-8").write(content)
    print(f"[OK] netlist_pcb2.json ({len(content)} chars), type was {type(r['content']).__name__}")

if __name__ == "__main__":
    main()
