#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""읽기 전용: Phase5용 PCB2 정밀 진단.
- 레이어 수, 보드 외곽선 bbox
- 부품 위치(mm)/회전 → 스펙 좌표와 비교
- pour(net/layer) 목록
- ratline(미배선) 수, 배선 라인 수
mil→mm = /39.3701"""
import sys, json
from easyeda_mcp_client import EasyEDAMCPClient

MIL = 39.3701
PCB2 = "821d4e6aff1909c8"

JS = f"""
const out={{}};
const MIL=39.3701;
try{{
  await eda.dmt_EditorControl.openDocument("{PCB2}");
  await new Promise(r=>setTimeout(r,1500));
  await eda.dmt_EditorControl.activateDocument("{PCB2}");
  await new Promise(r=>setTimeout(r,1500));
}}catch(e){{out.act_err=e.message;}}

// 레이어 수
try{{ out.copperLayers = await eda.pcb_Layer.getTheNumberOfCopperLayers(); }}catch(e){{ out.layer_err=e.message; }}

// 부품 위치
try{{
  const comps=await eda.pcb_PrimitiveComponent.getAll();
  out.compCount=(comps||[]).length;
  const pos={{}};
  for(const c of (comps||[])){{
    let des=c.designator; try{{if(!des&&c.getState_Designator)des=c.getState_Designator();}}catch(e){{}}
    let x=null,y=null,rot=null;
    try{{x=c.getState_X?c.getState_X():c.x;}}catch(e){{}}
    try{{y=c.getState_Y?c.getState_Y():c.y;}}catch(e){{}}
    try{{rot=c.getState_Rotation?c.getState_Rotation():c.rotation;}}catch(e){{}}
    if(des) pos[des]={{x_mm:x!=null?+(x/MIL).toFixed(2):null, y_mm:y!=null?+(y/MIL).toFixed(2):null, rot:rot}};
  }}
  out.pos=pos;
}}catch(e){{ out.comp_err=e.message; }}

// pour
try{{
  const pours=await eda.pcb_PrimitivePour.getAll();
  out.pours=(pours||[]).map(p=>{{
    let net=null,layer=null;
    try{{net=p.net??(p.getState_Net?p.getState_Net():null);}}catch(e){{}}
    try{{layer=p.layer??(p.getState_Layer?p.getState_Layer():null);}}catch(e){{}}
    return {{net,layer}};
  }});
}}catch(e){{ out.pour_err=e.message; }}

// 배선/미배선
try{{ const lines=await eda.pcb_PrimitiveLine.getAll(); out.lineCount=(lines||[]).length; }}catch(e){{ out.line_err=e.message; }}
try{{ const rats=await eda.pcb_PrimitiveRatline.getAll(); out.ratlineCount=(rats||[]).length; }}catch(e){{ out.rat_err=e.message; }}

// 외곽선 bbox
try{{
  const ol=await eda.pcb_PrimitivePolyline.getAll();
  let minx=1e9,miny=1e9,maxx=-1e9,maxy=-1e9,found=false;
  for(const p of (ol||[])){{
    try{{ const ln=p.getState_Polyline?p.getState_Polyline():null; }}catch(e){{}}
  }}
  out.outlineCount=(ol||[]).length;
}}catch(e){{ out.ol_err=e.message; }}

return out;
"""

def main():
    spec = json.load(open("mcp_design_flow.json", encoding="utf-8"))
    spec_pos = {c["designator"]: (c["x"], c["y"], c.get("angle",0)) for c in spec["components"]}
    c = EasyEDAMCPClient()
    if not c.connect(): sys.exit(1)
    res = c.execute_js(JS)
    json.dump(res, open("probe_pcb5_assess_out.json","w",encoding="utf-8"), ensure_ascii=False, indent=2, default=str)
    print("copperLayers:", res.get("copperLayers"), "| compCount:", res.get("compCount"),
          "| pours:", res.get("pours"), "| lines:", res.get("lineCount"), "| ratlines:", res.get("ratlineCount"))
    print("\n부품 배치 vs 스펙 (mm) — 차이 0.5mm 초과만 표시:")
    pos = res.get("pos", {})
    off = 0
    for des,(sx,sy,sa) in sorted(spec_pos.items()):
        p = pos.get(des)
        if not p: print(f"  [없음] {des}"); continue
        dx = abs((p["x_mm"] or 0)-sx); dy = abs((p["y_mm"] or 0)-sy)
        if dx>0.5 or dy>0.5 or (p["rot"] not in (sa, float(sa))):
            off += 1
            print(f"  {des}: 실제({p['x_mm']},{p['y_mm']},r{p['rot']}) vs 스펙({sx},{sy},r{sa})")
    print(f"\n스펙과 어긋난 부품: {off}/{len(spec_pos)}")

if __name__ == "__main__":
    main()
