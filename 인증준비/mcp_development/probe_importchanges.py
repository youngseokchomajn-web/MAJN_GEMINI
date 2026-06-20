#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""비파괴: importChanges 함수 소스 + 회로도 넷리스트 추출 방법 확인."""
import sys, json
from easyeda_mcp_client import EasyEDAMCPClient

PROBE_JS = r"""
const out = {};
try { out.importChanges_src = eda.pcb_Document.importChanges.toString().slice(0, 1200); } catch(e){ out.ic_err = e.message; }
try { out.getNetlist_pcb_src = eda.pcb_Net.getNetlist.toString().slice(0, 600); } catch(e){}
try { out.getNetlist_sch_src = eda.sch_Netlist.getNetlist.toString().slice(0, 600); } catch(e){}

// 회로도 페이지 정보 (getNetlist에 넘길 후보)
try {
  const pages = await eda.dmt_Schematic.getCurrentSchematicAllSchematicPagesInfo();
  out.schPages = pages;
} catch(e){ out.schPages_err = e.message; }

// PCB 넷리스트 문자열 전체 길이/앞부분
try {
  const pn = await eda.pcb_Net.getNetlist();
  out.pcbNetlist_len = (pn||'').length;
  out.pcbNetlist_head = (pn||'').slice(0, 800);
} catch(e){ out.pcbNet_err = e.message; }

return out;
"""

def main():
    client = EasyEDAMCPClient()
    if not client.connect():
        print("[ERROR] 브릿지 연결 실패"); sys.exit(1)
    res = client.execute_js(PROBE_JS)
    with open("probe_importchanges_out.json", "w", encoding="utf-8") as f:
        json.dump(res, f, ensure_ascii=False, indent=2)
    print("WROTE probe_importchanges_out.json")

if __name__ == "__main__":
    main()
