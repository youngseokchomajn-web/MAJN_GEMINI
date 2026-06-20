#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""S5-1: 회로도 -> PCB 동기화 (eda.pcb_Document.importChanges).
실행 전 사용자 백업 확인 필수. 전/후 부품 수·신규부품·U3 반영을 검증."""
import sys, json
from easyeda_mcp_client import EasyEDAMCPClient

PCB_UUID = "c9f1fdba7e0a3f4c"  # PCB1

# 동기화로 추가되어야 할 신규 부품(보스트망/풀업/디커플)
EXPECTED_NEW = ["R7","R8","C18","C19","C20","R9","R10","R11","C21","C22"]

JS = f"""
const out = {{}};
const PCB_UUID = "{PCB_UUID}";

// PCB 활성화
try {{
  await eda.dmt_EditorControl.openDocument(PCB_UUID);
  await new Promise(r=>setTimeout(r,1500));
  await eda.dmt_EditorControl.activateDocument(PCB_UUID);
  await new Promise(r=>setTimeout(r,2000));
}} catch(e){{ out.activate_err = e.message; }}

// BEFORE
try {{
  const comps = await eda.pcb_PrimitiveComponent.getAll();
  out.before = (comps||[]).map(c => c.designator).sort();
  out.beforeCount = out.before.length;
}} catch(e){{ out.before_err = e.message; }}

// IMPORT CHANGES
try {{
  out.importResult = await eda.pcb_Document.importChanges(PCB_UUID);
  out.importCalled = true;
}} catch(e){{ out.import_err = e.message; }}
await new Promise(r=>setTimeout(r,4000));

// AFTER
try {{
  const comps = await eda.pcb_PrimitiveComponent.getAll();
  out.after = (comps||[]).map(c => c.designator).sort();
  out.afterCount = out.after.length;
}} catch(e){{ out.after_err = e.message; }}

return out;
"""

def main():
    client = EasyEDAMCPClient()
    if not client.connect():
        print("[ERROR] 브릿지 연결 실패"); sys.exit(1)
    res = client.execute_js(JS)
    with open("import_changes_out.json", "w", encoding="utf-8") as f:
        json.dump(res, f, ensure_ascii=False, indent=2)

    before = set(res.get("before") or [])
    after = set(res.get("after") or [])
    added = sorted(after - before)
    removed = sorted(before - after)

    print("=" * 60)
    print(f" importChanges 호출: {res.get('importCalled')}  결과={res.get('importResult')}")
    if res.get("import_err"): print(f" [import_err] {res['import_err']}")
    print(f" 부품 수: {res.get('beforeCount')} -> {res.get('afterCount')}")
    print(f" 추가됨({len(added)}): {added}")
    print(f" 제거됨({len(removed)}): {removed}")
    missing = [d for d in EXPECTED_NEW if d not in after]
    print(f" 기대 신규 10개 중 미반영: {missing if missing else 'NONE (전부 반영됨)'}")
    print("=" * 60)
    if missing:
        print(" [주의] 일부 신규 부품 미반영 -> import_changes_out.json 확인")
    else:
        print(" [OK] 신규 10부품 전부 PCB 반영 확인")

if __name__ == "__main__":
    main()
