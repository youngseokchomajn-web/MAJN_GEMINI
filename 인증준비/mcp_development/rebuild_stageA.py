#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Path B 재빌드 Stage A: clearRouting + pour 삭제 + U3(2패드) 삭제 + 전 부품(45) 재배치.
스펙(mcp_design_flow.json) 기준. U3는 C2909511로 새로 생성 -> DFN-14(14핀+EP).
이후 Stage B(넷 연결)에서 검증."""
import sys, json, time
from easyeda_mcp_client import EasyEDAMCPClient

PCB_UUID = "c9f1fdba7e0a3f4c"

PREP_JS = f"""
const out = {{}};
// PCB 활성화
await eda.dmt_EditorControl.openDocument("{PCB_UUID}");
await new Promise(r=>setTimeout(r,1500));
await eda.dmt_EditorControl.activateDocument("{PCB_UUID}");
await new Promise(r=>setTimeout(r,2000));

// BEFORE
let comps = await eda.pcb_PrimitiveComponent.getAll();
out.before_compCount = (comps||[]).length;
try {{ const ls = await eda.pcb_PrimitiveLine.getAll(); out.before_lines = (ls||[]).length; }} catch(e){{}}
try {{ const ps = await eda.pcb_PrimitivePour.getAll(); out.before_pours = (ps||[]).length; }} catch(e){{}}

// 1. clearRouting
try {{ await eda.pcb_Document.clearRouting("all"); out.clearRouting = true; }} catch(e){{ out.clearRouting_err = e.message; }}
await new Promise(r=>setTimeout(r,2000));

// 2. pour 전부 삭제
try {{
  const pours = await eda.pcb_PrimitivePour.getAll();
  if (pours && pours.length) {{ await eda.pcb_PrimitivePour.delete(pours); out.deletedPours = pours.length; }}
  else out.deletedPours = 0;
}} catch(e){{ out.pour_del_err = e.message; }}
await new Promise(r=>setTimeout(r,1500));

// 3. U3 삭제
try {{
  comps = await eda.pcb_PrimitiveComponent.getAll();
  let u3 = null;
  for (const c of comps) {{ let d=null; try{{d=c.designator??c.getState_Designator?.();}}catch(e){{}} if(d==='U3'){{u3=c;break;}} }}
  if (u3) {{ await eda.pcb_PrimitiveComponent.delete(u3); out.deletedU3 = true; }}
  else out.deletedU3 = 'not found';
}} catch(e){{ out.u3_del_err = e.message; }}
await new Promise(r=>setTimeout(r,1500));

// AFTER prep
comps = await eda.pcb_PrimitiveComponent.getAll();
out.after_prep_compCount = (comps||[]).length;
try {{ const ls = await eda.pcb_PrimitiveLine.getAll(); out.after_lines = (ls||[]).length; }} catch(e){{}}
try {{ const ps = await eda.pcb_PrimitivePour.getAll(); out.after_pours = (ps||[]).length; }} catch(e){{}}
return out;
"""

def main():
    with open("mcp_design_flow.json","r",encoding="utf-8") as f:
        flow = json.load(f)

    client = EasyEDAMCPClient()
    if not client.connect():
        print("[ERROR] 브릿지 연결 실패"); sys.exit(1)

    print("=== PREP: clearRouting + pour 삭제 + U3 삭제 ===")
    prep = client.execute_js(PREP_JS)
    print(json.dumps(prep, ensure_ascii=False, indent=2, default=str))

    # 캐시
    lcsc_ids = [c["lcsc_id"] for c in flow["components"]]
    print("\n=== 캐시 ===")
    client.cache_components(lcsc_ids)
    time.sleep(8)

    # 배치
    print("\n=== 배치 (45개) ===")
    failed = []
    for c in flow["components"]:
        ok = client.place_component(c["designator"], c["name"], c["lcsc_id"], c["x"], c["y"], c["angle"])
        if not ok:
            failed.append(c["designator"])
        time.sleep(0.05)
    print("배치 실패:", failed if failed else "없음")

    # 검증: 부품 수 + U3 패드 수
    VERIFY_JS = """
    const out = {};
    const comps = await eda.pcb_PrimitiveComponent.getAll();
    out.compCount = (comps||[]).length;
    out.designators = [];
    for (const c of comps) {
      let d=null; try{d=c.designator??c.getState_Designator?.();}catch(e){}
      out.designators.push(d);
      if (d==='U3') {
        try { const pads = await eda.pcb_PrimitiveComponent.getAllPinsByPrimitiveId(c.getState_PrimitiveId());
              out.U3_padCount = (pads||[]).length;
              out.U3_pads = (pads||[]).map(p=>p.padNumber); } catch(e){ out.u3_err=e.message; }
        try { out.U3_lcsc = c.getState_SupplierId?.(); } catch(e){}
      }
    }
    out.designators.sort();
    return out;
    """
    print("\n=== 검증 ===")
    verify = client.execute_js(VERIFY_JS)
    with open("rebuild_stageA_out.json","w",encoding="utf-8") as f:
        json.dump({"prep":prep,"placeFailed":failed,"verify":verify}, f, ensure_ascii=False, indent=2, default=str)
    print(f"부품 수: {verify.get('compCount')}")
    print(f"U3 패드 수: {verify.get('U3_padCount')} (pads={verify.get('U3_pads')}) lcsc={verify.get('U3_lcsc')}")
    print(f"designators: {verify.get('designators')}")

if __name__ == "__main__":
    main()
