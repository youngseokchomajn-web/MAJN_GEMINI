#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ERC를 userInterface=true 로 실행 → EasyEDA ERC 결과 패널에 2건 표시(사용자 확인용)."""
import sys, json
from easyeda_mcp_client import EasyEDAMCPClient

JS = r"""
const out={};
try{
  const pages=await eda.dmt_Schematic.getAllSchematicPagesInfo();
  if(pages&&pages.length){await eda.dmt_EditorControl.activateDocument(pages[0].uuid);await new Promise(r=>setTimeout(r,800));}
}catch(e){out.act_err=e.message;}
try{ out.erc = await eda.sch_Drc.check(true, true, true); }catch(e){ out.erc_err=e.message; }
return out;
"""

def main():
    client = EasyEDAMCPClient()
    if not client.connect():
        print("[ERROR] bridge connect failed"); sys.exit(1)
    print(json.dumps(client.execute_js(JS), ensure_ascii=True, indent=2, default=str))

if __name__ == "__main__":
    main()
