#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Phase0 선행: 현재 프로젝트/문서/보드/PCB/회로도 상태를 읽기전용으로 덤프."""
import sys, json
from easyeda_mcp_client import EasyEDAMCPClient

PROBE_JS = r"""
const out = {};
try { out.project = await eda.dmt_Project.getCurrentProjectInfo(); } catch(e){ out.project_err = e.message; }
try { out.currentDoc = await eda.dmt_SelectControl.getCurrentDocumentInfo(); } catch(e){ out.currentDoc_err = e.message; }
try {
  const boards = await eda.dmt_Board.getAllBoardsInfo();
  out.boards = (boards||[]).map(b => ({ name: b.name, uuid: b.uuid, type: b.documentType }));
} catch(e){ out.boards_err = e.message; }
try {
  const pcbs = await eda.dmt_Pcb.getAllPcbsInfo();
  out.pcbs = (pcbs||[]).map(p => ({ name: p.name, uuid: p.uuid }));
} catch(e){ out.pcbs_err = e.message; }
// schematic docs — try a few known namespaces
try {
  if (eda.dmt_Schematic && eda.dmt_Schematic.getAllSchematicsInfo) {
    const s = await eda.dmt_Schematic.getAllSchematicsInfo();
    out.schematics = (s||[]).map(x => ({ name: x.name, uuid: x.uuid }));
  }
} catch(e){ out.sch_err = e.message; }
// dump dmt_Project methods to find a document-tree accessor
try {
  const proto = Object.getPrototypeOf(eda.dmt_Project);
  out.dmt_Project_methods = Object.getOwnPropertyNames(proto).filter(m => m !== 'constructor');
} catch(e){}
try {
  out.dmt_namespaces = Object.keys(eda).filter(k => k.startsWith('dmt_'));
} catch(e){}
return out;
"""

def main():
    client = EasyEDAMCPClient()
    if not client.connect():
        print("[ERROR] bridge connect failed"); sys.exit(1)
    res = client.execute_js(PROBE_JS)
    print(json.dumps(res, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()
