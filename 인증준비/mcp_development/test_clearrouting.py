#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""clearRouting 단독 테스트 (PCB 활성화는 별도 호출). 라인수 변화 확인."""
import sys, json
from easyeda_mcp_client import EasyEDAMCPClient

PCB_UUID = "c9f1fdba7e0a3f4c"

ACT_JS = f"""
await eda.dmt_EditorControl.openDocument("{PCB_UUID}");
await new Promise(r=>setTimeout(r,1500));
await eda.dmt_EditorControl.activateDocument("{PCB_UUID}");
await new Promise(r=>setTimeout(r,2000));
const l = await eda.pcb_PrimitiveLine.getAll();
return {{lines:(l||[]).length}};
"""

CLEAR_JS = """
const t0 = Date.now();
let res = null, err = null;
try { res = await eda.pcb_Document.clearRouting("all"); } catch(e){ err = e.message; }
return { result: res, err, elapsedMs: Date.now()-t0 };
"""

def main():
    client = EasyEDAMCPClient()
    if not client.connect():
        print("[ERROR] 브릿지 연결 실패"); sys.exit(1)
    print("activate:", client.execute_js(ACT_JS))
    print("clearRouting (단독)...")
    try:
        print("result:", client.execute_js(CLEAR_JS))
    except Exception as e:
        print("clearRouting FAILED:", e)
    # 라인 수 확인
    chk = client.execute_js("const l=await eda.pcb_PrimitiveLine.getAll(); return {lines:(l||[]).length};")
    print("after lines:", chk)

if __name__ == "__main__":
    main()
