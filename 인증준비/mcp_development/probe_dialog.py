#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""비파괴: 현재 화면 모달/다이얼로그 점검 + importChanges 관련 API 후보 탐색."""
import sys, json
from easyeda_mcp_client import EasyEDAMCPClient

JS = r"""
const out = {};
// 열린 모달/다이얼로그 텍스트 수집
try {
  const sels = ['[class*="modal"]','[class*="dialog"]','[class*="Dialog"]','[role="dialog"]','[class*="lc_modal"]'];
  const found = [];
  for (const s of sels) {
    document.querySelectorAll(s).forEach(el => {
      const t = (el.innerText||'').trim();
      if (t && el.offsetParent !== null) found.push({sel:s, text:t.slice(0,300)});
    });
  }
  out.openDialogs = found.slice(0,10);
} catch(e){ out.dlg_err = e.message; }

// 버튼 텍스트 수집 (다이얼로그 확인버튼 후보)
try {
  const btns = [];
  document.querySelectorAll('button').forEach(b => {
    const t=(b.innerText||'').trim();
    if (t && b.offsetParent!==null) btns.push(t);
  });
  out.visibleButtons = Array.from(new Set(btns)).slice(0,40);
} catch(e){ out.btn_err = e.message; }

// importChanges 시그니처(양쪽)
try { out.pcb_importChanges_argc = eda.pcb_Document.importChanges.length; } catch(e){}
try { out.sch_importChanges_src = eda.sch_Document.importChanges.toString().slice(0,400); } catch(e){ out.sch_ic_err = e.message; }

// 현재 문서
try {
  const doc = await eda.dmt_SelectControl.getCurrentDocumentInfo();
  out.currentDoc = doc ? {type:doc.documentType, uuid:doc.uuid} : null;
} catch(e){}
return out;
"""

def main():
    client = EasyEDAMCPClient()
    if not client.connect():
        print("[ERROR] 브릿지 연결 실패"); sys.exit(1)
    res = client.execute_js(JS)
    with open("probe_dialog_out.json","w",encoding="utf-8") as f:
        json.dump(res,f,ensure_ascii=False,indent=2)
    print("WROTE probe_dialog_out.json")

if __name__ == "__main__":
    main()
