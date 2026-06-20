#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""S5 사전 점검: 현재 라이브 PCB 상태를 읽기 전용으로 조회.
- 현재 문서 타입, PCB 부품 개수/데지그네이터, U3 패드 수, 라인(배선)/팟 수, ratline 존재 여부.
아무것도 수정하지 않음."""
import sys, json
from easyeda_mcp_client import EasyEDAMCPClient

PROBE_JS = r"""
const out = {};
try {
  const doc = await eda.dmt_SelectControl.getCurrentDocumentInfo();
  out.currentDoc = doc ? { type: doc.documentType, uuid: doc.uuid, name: doc.name } : null;
} catch(e) { out.currentDoc_err = e.message; }

// PCB 문서 활성화 (있으면)
try {
  const pcbs = await eda.dmt_Pcb.getAllPcbsInfo();
  out.pcbList = (pcbs||[]).map(p => ({uuid:p.uuid, name:p.name}));
  if (pcbs && pcbs.length) {
    await eda.dmt_EditorControl.openDocument(pcbs[0].uuid);
    await new Promise(r=>setTimeout(r,1500));
    await eda.dmt_EditorControl.activateDocument(pcbs[0].uuid);
    await new Promise(r=>setTimeout(r,2000));
  }
} catch(e) { out.pcb_err = e.message; }

// 부품
try {
  const comps = await eda.pcb_PrimitiveComponent.getAll();
  out.componentCount = (comps||[]).length;
  const list = [];
  for (const c of (comps||[])) {
    let des = c.designator;
    try { if (!des && typeof c.getState_Designator==='function') des = await c.getState_Designator(); } catch(e){}
    let padCount = null;
    try {
      if (typeof c.getPads === 'function') { const pads = await c.getPads(); padCount = (pads||[]).length; }
    } catch(e){}
    list.push({ des: des, pads: padCount });
  }
  out.components = list;
  const u3 = list.find(x => x.des === 'U3');
  out.U3 = u3 || 'NOT_FOUND';
} catch(e) { out.comp_err = e.message; }

// 배선(라인) / 팟 / pour
try {
  if (eda.pcb_PrimitiveLine && typeof eda.pcb_PrimitiveLine.getAll === 'function') {
    const lines = await eda.pcb_PrimitiveLine.getAll();
    out.routedLineCount = (lines||[]).length;
  }
} catch(e) { out.line_err = e.message; }
try {
  if (eda.pcb_PrimitivePour && typeof eda.pcb_PrimitivePour.getAll === 'function') {
    const pours = await eda.pcb_PrimitivePour.getAll();
    out.pourCount = (pours||[]).length;
  }
} catch(e) { out.pour_err = e.message; }
try {
  if (eda.pcb_PrimitiveRatline && typeof eda.pcb_PrimitiveRatline.getAll === 'function') {
    const rats = await eda.pcb_PrimitiveRatline.getAll();
    out.ratlineCount = (rats||[]).length;
  }
} catch(e) { out.rat_err = e.message; }

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
