#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""S5-1 재시도: importChanges에 여러 uuid 후보를 순차 시도.
각 시도 후 부품 수 변화를 확인하고, 변화가 생기면 즉시 중단."""
import sys, json
from easyeda_mcp_client import EasyEDAMCPClient

PCB_UUID   = "c9f1fdba7e0a3f4c"  # PCB1
SCH_UUID   = "1b82f42f112ab63b"  # schematic1
SCHPG_UUID = "6085a53b74cfcf6b"  # schematic page p1
BOARD_UUID = "c27b1a78b7762b95"  # Board1

JS = f"""
const out = {{ attempts: [] }};
const PCB_UUID="{PCB_UUID}", SCH_UUID="{SCH_UUID}", SCHPG_UUID="{SCHPG_UUID}", BOARD_UUID="{BOARD_UUID}";

async function activatePcb() {{
  try {{
    await eda.dmt_EditorControl.openDocument(PCB_UUID);
    await new Promise(r=>setTimeout(r,1200));
    await eda.dmt_EditorControl.activateDocument(PCB_UUID);
    await new Promise(r=>setTimeout(r,1500));
  }} catch(e){{}}
}}
async function compCount() {{
  try {{ const c = await eda.pcb_PrimitiveComponent.getAll(); return (c||[]).length; }} catch(e){{ return -1; }}
}}

await activatePcb();
out.startCount = await compCount();

const candidates = [
  ["SCH_UUID", SCH_UUID],
  ["BOARD_UUID", BOARD_UUID],
  ["SCHPG_UUID", SCHPG_UUID],
];

for (const [label, uid] of candidates) {{
  let r = null, err = null;
  await activatePcb();
  try {{ r = await eda.pcb_Document.importChanges(uid); }} catch(e){{ err = e.message; }}
  await new Promise(res=>setTimeout(res,3000));
  const cnt = await compCount();
  out.attempts.push({{ label, uid, result: r, err, countAfter: cnt }});
  if (cnt > out.startCount) {{ out.changedBy = label; break; }}
}}
out.endCount = await compCount();
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
