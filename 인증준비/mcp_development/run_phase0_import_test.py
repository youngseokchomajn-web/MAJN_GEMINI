#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Phase0-1b: 빈 독립 PCB4에 importChanges가 회로도 넷리스트를 주입하는지 테스트."""
import sys, json
from easyeda_mcp_client import EasyEDAMCPClient

JS = r"""
const out = {};
const PCB4 = "9c729d7a12ead349";
try {
  await eda.dmt_EditorControl.openDocument(PCB4);
  await new Promise(r=>setTimeout(r,1500));
  await eda.dmt_EditorControl.activateDocument(PCB4);
  await new Promise(r=>setTimeout(r,2000));
} catch(e){ out.activate_err = e.message; }

async function counts(){
  let comps=-1, lines=-1;
  try { comps = (await eda.pcb_PrimitiveComponent.getAll()||[]).length; } catch(e){ comps='ERR:'+e.message; }
  try { lines = (await eda.pcb_PrimitiveLine.getAll()||[]).length; } catch(e){ lines='ERR:'+e.message; }
  return { comps, lines };
}
try { const cd = await eda.dmt_SelectControl.getCurrentDocumentInfo(); out.activeNow = cd ? cd.uuid : null; } catch(e){}
out.before = await counts();
try { out.importResult = await eda.pcb_Document.importChanges(PCB4); } catch(e){ out.import_err = e.message; }
await new Promise(r=>setTimeout(r,4000));
out.after = await counts();
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
