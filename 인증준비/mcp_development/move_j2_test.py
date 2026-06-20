#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""S5 수정 테스트: J2를 +300mil 이동 후 ERC 재검증.
- 이동 전/후 ERC fatal 수 비교 -> 네트라벨이 함께 움직였는지(끊김 여부) 판정.
- 원좌표(800) 기록. 결과 나쁘면 revert 스크립트로 되돌림."""
import sys, json
from easyeda_mcp_client import EasyEDAMCPClient

SCHPG_UUID = "6085a53b74cfcf6b"
NEW_X = 1100  # 800 -> 1100 (오른쪽 300mil)

JS = f"""
const out = {{}};
try {{
  await eda.dmt_EditorControl.openDocument("{SCHPG_UUID}");
  await new Promise(r=>setTimeout(r,1000));
  await eda.dmt_EditorControl.activateDocument("{SCHPG_UUID}");
  await new Promise(r=>setTimeout(r,1200));
}} catch(e){{}}

async function erc() {{
  try {{
    const r = await eda.sch_Drc.check(true, false, true);
    return r;
  }} catch(e){{ return {{error:e.message}}; }}
}}

// BEFORE ERC
out.before = await erc();

// J2 찾아 이동
const comps = await eda.sch_PrimitiveComponent.getAll();
let j2 = null;
for (const c of comps) {{
  let des=null; try{{ des = c.designator ?? c.getState_Designator?.(); }}catch(e){{}}
  if (des === 'J2') {{ j2 = c; break; }}
}}
if (!j2) {{ out.err = 'J2 not found'; return out; }}
out.j2_before_x = j2.getState_X();
out.j2_before_y = j2.getState_Y();
try {{
  await j2.setState_X({NEW_X});
  if (typeof j2.done === 'function') await j2.done();
  out.moved = true;
}} catch(e){{ out.move_err = e.message; }}
await new Promise(r=>setTimeout(r,2000));

// 이동 확인
const comps2 = await eda.sch_PrimitiveComponent.getAll();
for (const c of comps2) {{
  let des=null; try{{ des = c.designator ?? c.getState_Designator?.(); }}catch(e){{}}
  if (des === 'J2') {{ out.j2_after_x = c.getState_X(); out.j2_after_y = c.getState_Y(); break; }}
}}

// AFTER ERC
out.after = await erc();
return out;
"""

def summarize(erc):
    if not isinstance(erc, dict):
        return f"raw={erc}"
    # 다양한 형태 대응
    keys = list(erc.keys())
    return json.dumps(erc, ensure_ascii=False)[:600]

def main():
    client = EasyEDAMCPClient()
    if not client.connect():
        print("[ERROR] 브릿지 연결 실패"); sys.exit(1)
    res = client.execute_js(JS)
    with open("move_j2_test_out.json","w",encoding="utf-8") as f:
        json.dump(res,f,ensure_ascii=False,indent=2,default=str)
    print("J2 before:", res.get("j2_before_x"), res.get("j2_before_y"))
    print("J2 after :", res.get("j2_after_x"), res.get("j2_after_y"))
    print("moved:", res.get("moved"), res.get("move_err"))
    print("--- ERC BEFORE ---")
    print(summarize(res.get("before")))
    print("--- ERC AFTER ---")
    print(summarize(res.get("after")))

if __name__ == "__main__":
    main()
