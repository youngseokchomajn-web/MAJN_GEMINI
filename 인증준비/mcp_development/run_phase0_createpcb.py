#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Phase0-1: 새 PCB 생성 후 회로도 링크/보드 연결 확인 (deletePcb로 롤백 가능)."""
import sys, json
from easyeda_mcp_client import EasyEDAMCPClient

JS = r"""
const out = { steps: [] };
const before = await eda.dmt_Pcb.getAllPcbsInfo();
out.before = (before||[]).map(p=>({name:p.name,uuid:p.uuid}));
try { const cb = await eda.dmt_Board.getCurrentBoardInfo(); out.curBoard = cb ? {name:cb.name, uuid:cb.uuid} : null; } catch(e){ out.curBoard_err=e.message; }

let created = null;
try { created = await eda.dmt_Pcb.createPcb(); } catch(e){ out.create_err = e.message; }
out.createResult = created;
await new Promise(r=>setTimeout(r,2500));

const after = await eda.dmt_Pcb.getAllPcbsInfo();
out.after = (after||[]).map(p=>({name:p.name,uuid:p.uuid}));

// identify the newly created pcb uuid
const beforeSet = new Set(out.before.map(p=>p.uuid));
out.newPcbs = out.after.filter(p=>!beforeSet.has(p.uuid));

// board -> schematic/pcb mapping after creation
function boardMap(proj){
  const m=[];
  if(proj && proj.data){
    for(const d of proj.data){
      if(d.itemType==='Board'){
        m.push({type:'Board', name:d.name,
                schematic: d.schematic? {name:d.schematic.name,uuid:d.schematic.uuid}:null,
                pcb: d.pcb? {name:d.pcb.name,uuid:d.pcb.uuid}:null});
      } else if(d.itemType==='PCB'){
        m.push({type:'PCB_standalone', name:d.name, uuid:d.uuid, parentBoardName:d.parentBoardName});
      } else {
        m.push({type:d.itemType, name:d.name||null});
      }
    }
  }
  return m;
}
const proj = await eda.dmt_Project.getCurrentProjectInfo();
out.boardMap = boardMap(proj);
try { const cd = await eda.dmt_SelectControl.getCurrentDocumentInfo(); out.currentDoc = cd ? {uuid:cd.uuid, documentType:cd.documentType} : null; } catch(e){}
return out;
"""

def main():
    client = EasyEDAMCPClient()
    if not client.connect():
        print("[ERROR] bridge connect failed"); sys.exit(1)
    res = client.execute_js(JS)
    print(json.dumps(res, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()
