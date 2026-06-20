#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""S5-1 재시도 v3: 회로도 저장 -> PCB 저장 -> importChanges.
저장이 선행되어야 EasyEDA가 변경분을 인식할 수 있다는 가설 검증."""
import sys, json
from easyeda_mcp_client import EasyEDAMCPClient

PCB_UUID   = "c9f1fdba7e0a3f4c"
SCHPG_UUID = "6085a53b74cfcf6b"

JS = f"""
const out = {{ steps: [] }};
const PCB_UUID="{PCB_UUID}", SCHPG_UUID="{SCHPG_UUID}";
async function act(uid){{
  try{{ await eda.dmt_EditorControl.openDocument(uid); await new Promise(r=>setTimeout(r,1200));
        await eda.dmt_EditorControl.activateDocument(uid); await new Promise(r=>setTimeout(r,1500)); }}catch(e){{}}
}}
async function pcbCount(){{ try{{const c=await eda.pcb_PrimitiveComponent.getAll(); return (c||[]).length;}}catch(e){{return -1;}} }}

// 1. 회로도 활성화 + 저장
await act(SCHPG_UUID);
try {{ const r = await eda.sch_Document.save(); out.steps.push(["sch.save", r]); }} catch(e){{ out.steps.push(["sch.save_err", e.message]); }}
await new Promise(r=>setTimeout(r,2000));

// 2. PCB 활성화 + 저장
await act(PCB_UUID);
out.beforeCount = await pcbCount();
try {{ const r = await eda.pcb_Document.save(); out.steps.push(["pcb.save", r]); }} catch(e){{ out.steps.push(["pcb.save_err", e.message]); }}
await new Promise(r=>setTimeout(r,2000));

// 3. importChanges
try {{ const r = await eda.pcb_Document.importChanges(PCB_UUID); out.steps.push(["importChanges", r]); }} catch(e){{ out.steps.push(["importChanges_err", e.message]); }}
await new Promise(r=>setTimeout(r,4000));
out.afterCount = await pcbCount();
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
