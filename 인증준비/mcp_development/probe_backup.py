#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""비파괴: 백업 프로젝트/보드 존재 여부 확인."""
import sys, json
from easyeda_mcp_client import EasyEDAMCPClient

JS = r"""
const out = {};
try {
  const cur = await eda.dmt_Project.getCurrentProjectInfo();
  out.currentProject = cur ? {uuid: cur.uuid, name: cur.name} : null;
} catch(e){ out.curProj_err = e.message; }
try {
  const boards = await eda.dmt_Board.getAllBoardsInfo();
  out.boards = (boards||[]).map(b => ({uuid:b.uuid, name:b.name}));
} catch(e){ out.boards_err = e.message; }
try {
  const pcbs = await eda.dmt_Pcb.getAllPcbsInfo();
  out.pcbs = (pcbs||[]).map(p => ({uuid:p.uuid, name:p.name}));
} catch(e){ out.pcbs_err = e.message; }
return out;
"""

def main():
    client = EasyEDAMCPClient()
    if not client.connect():
        print("[ERROR] 브릿지 연결 실패"); sys.exit(1)
    res = client.execute_js(JS)
    print(json.dumps(res, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()
