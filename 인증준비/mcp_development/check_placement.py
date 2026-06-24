#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""C3 배치 점검: 위치 vs design_flow / 보드내 / 부품 겹침(패드 bbox)."""
import json, sys, io, urllib.request
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

def ejs(code):
    req = urllib.request.Request("http://127.0.0.1:49620/execute",
        data=json.dumps({"code": code}).encode("utf-8"),
        headers={"Content-Type": "application/json"}, method="POST")
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.loads(r.read().decode())

CODE = r"""
const comps = await eda.pcb_PrimitiveComponent.getAll();
const C=[];
for(const c of comps){
  let des='',x=0,y=0,rot=0,pid='';
  try{des=c.getState_Designator();}catch(e){}
  try{x=c.getState_X();}catch(e){}
  try{y=c.getState_Y();}catch(e){}
  try{rot=c.getState_Rotation();}catch(e){}
  try{pid=c.getState_PrimitiveId();}catch(e){}
  C.push({des,x,y,rot,pid});
}
const pads = await eda.pcb_PrimitivePad.getAll();
const P=[];
for(const p of pads){
  try{ P.push({pid:p.getState_PrimitiveId(), x:p.getState_X(), y:p.getState_Y()}); }catch(e){}
}
return {C, P};
"""

r = ejs(CODE)["result"]
comps = r["C"]; pads = r["P"]
MM = 39.3701
flow = {c["designator"]: c for c in json.load(open("mcp_design_flow.json", encoding="utf-8"))["components"]}

# 패드를 부품에 매핑 (pad.pid가 comp.pid로 시작)
b = {c["des"]: [1e9,1e9,-1e9,-1e9] for c in comps}
cpid = sorted([(c["pid"], c["des"]) for c in comps], key=lambda t:-len(t[0]))
for p in pads:
    for pid, des in cpid:
        if pid and p["pid"].startswith(pid):
            b[des][0]=min(b[des][0],p["x"]); b[des][1]=min(b[des][1],p["y"])
            b[des][2]=max(b[des][2],p["x"]); b[des][3]=max(b[des][3],p["y"])
            break

# 보드 경계
BX0,BY0,BX1,BY1 = -100, 0, 3200, 2450
print("=== 1) 위치 vs design_flow (mil, 허용오차 5mil) ===")
drift=[]
for c in comps:
    f=flow.get(c["des"])
    if not f: print("  ?", c["des"], "design_flow에 없음"); continue
    ex,ey,erot = round(f["x"]*MM), round(f["y"]*MM), f.get("angle",0)
    dx,dy=abs(c["x"]-ex),abs(c["y"]-ey)
    if dx>5 or dy>5 or (c["rot"]%360)!=(erot%360):
        drift.append(f"{c['des']}: pos({c['x']},{c['y']}) vs ({ex},{ey}) rot {c['rot']}vs{erot}")
print("  드리프트:", "없음 (전부 일치)" if not drift else drift)

print("=== 2) 보드 밖 부품 (패드 bbox 기준) ===")
off=[]
MAR=30  # 실드/바디 여유
for c in comps:
    bx=b[c["des"]]
    if bx[0]>1e8: continue
    if bx[0]<BX0-MAR or bx[1]<BY0-MAR or bx[2]>BX1+MAR or bx[3]>BY1+MAR:
        off.append(f"{c['des']}: bbox({round(bx[0])},{round(bx[1])})-({round(bx[2])},{round(bx[3])})")
print("  보드밖:", "없음" if not off else off)

print("=== 3) 부품 겹침 (패드 bbox 교차) ===")
ds=[c["des"] for c in comps if b[c["des"]][0]<1e8]
ov=[]
for i in range(len(ds)):
    for j in range(i+1,len(ds)):
        a,c2=b[ds[i]],b[ds[j]]
        if a[0]<c2[2] and c2[0]<a[2] and a[1]<c2[3] and c2[1]<a[3]:
            # 교차 면적
            ox=min(a[2],c2[2])-max(a[0],c2[0]); oy=min(a[3],c2[3])-max(a[1],c2[1])
            ov.append(f"{ds[i]}<->{ds[j]} (overlap {round(ox)}x{round(oy)}mil)")
print("  겹침:", "없음 ✓" if not ov else ov)
print(f"\n요약: 부품 {len(comps)} | 패드 {len(pads)} | 드리프트 {len(drift)} | 보드밖 {len(off)} | 겹침 {len(ov)}")
