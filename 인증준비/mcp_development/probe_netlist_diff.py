#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""비파괴: 회로도 넷리스트 vs PCB 넷리스트 추출 + importChanges 시그니처 확인.
PCB를 수정하지 않음. importChanges가 무엇을 바꿀지 미리 파악."""
import sys, json
from easyeda_mcp_client import EasyEDAMCPClient

PROBE_JS = r"""
const out = {};
// importChanges 시그니처
try {
  out.importChanges_argc = eda.pcb_Document.importChanges.length;
} catch(e){ out.importChanges_err = e.message; }

// 회로도 넷리스트
try {
  const sn = await eda.sch_Netlist.getNetlist();
  // 형태 파악
  if (sn) {
    out.schNetlistType = Array.isArray(sn) ? 'array' : typeof sn;
    if (Array.isArray(sn)) {
      out.schNetCount = sn.length;
      out.schNetSample = sn.slice(0,3);
      // 넷이름 목록
      out.schNetNames = sn.map(n => n.name || n.netName || n.net || JSON.stringify(Object.keys(n))).slice(0,80);
    } else {
      out.schNetKeys = Object.keys(sn).slice(0,40);
    }
  } else { out.schNetlist = null; }
} catch(e){ out.schNet_err = e.message; }

// PCB 넷리스트
try {
  const pn = await eda.pcb_Net.getNetlist();
  if (pn) {
    out.pcbNetlistType = Array.isArray(pn) ? 'array' : typeof pn;
    if (Array.isArray(pn)) {
      out.pcbNetCount = pn.length;
      out.pcbNetSample = pn.slice(0,3);
      out.pcbNetNames = pn.map(n => n.name || n.netName || n.net || JSON.stringify(Object.keys(n))).slice(0,80);
    } else {
      out.pcbNetKeys = Object.keys(pn).slice(0,40);
    }
  } else { out.pcbNetlist = null; }
} catch(e){ out.pcbNet_err = e.message; }

return out;
"""

def main():
    client = EasyEDAMCPClient()
    if not client.connect():
        print("[ERROR] 브릿지 연결 실패"); sys.exit(1)
    res = client.execute_js(PROBE_JS)
    print(json.dumps(res, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()
