#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""C5/C7: SMD 패드끼리 클리어런스 위반 자동분리 (가벼운 부품을 IC에서 떼어냄). 반복."""
import json, sys, io, urllib.request, math
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

TARGET = 18  # mil 목표 클리어런스
BX0, BY0, BX1, BY1 = -100, 0, 3200, 2450

def ejs(code):
    req = urllib.request.Request("http://127.0.0.1:49620/execute",
        data=json.dumps({"code": code}).encode("utf-8"),
        headers={"Content-Type": "application/json"}, method="POST")
    with urllib.request.urlopen(req, timeout=120) as r:
        return json.loads(r.read().decode())

def desig(suffix):
    t = suffix.split(":")[-1].strip()       # "(GND): C3_2" -> "C3_2"
    return "_".join(t.split("_")[:-1]) or t  # "C3_2"->"C3", "USB_C_3"->"USB_C"

GET = r"""
const comps = await eda.pcb_PrimitiveComponent.getAll();
const C={};
for(const c of comps){ try{ const d=c.getState_Designator(); C[d]={pid:c.getState_PrimitiveId(),x:c.getState_X(),y:c.getState_Y()}; }catch(e){} }
const pads = await eda.pcb_PrimitivePad.getAll();
const PB={}; const NP={};
for(const d in C){ PB[d]=[1e9,1e9,-1e9,-1e9]; NP[d]=0; }
const order=Object.entries(C).sort((a,b)=>b[1].pid.length-a[1].pid.length);
for(const p of pads){ try{ const pid=p.getState_PrimitiveId(),x=p.getState_X(),y=p.getState_Y();
  for(const [d,c] of order){ if(pid.startsWith(c.pid)){ const b=PB[d]; if(x<b[0])b[0]=x; if(y<b[1])b[1]=y; if(x>b[2])b[2]=x; if(y>b[3])b[3]=y; NP[d]++; break; } } }catch(e){} }
const res = await eda.pcb_Drc.check(true,false,true);
const clr=[];
for(const cat of res||[]) if((cat.name||'').includes('Clearance'))
  for(const sub of cat.list||[]) for(const e of sub.list||[]){
    const ot=(e.errorObjType||'');
    if(ot.includes('Pad')||ot.includes('Hole')){
      const s1=(e.obj1&&e.obj1.suffix)||(e.errData&&e.errData.obj1Suffix)||'';
      const s2=(e.obj2&&e.obj2.suffix)||(e.errData&&e.errData.obj2Suffix)||'';
      clr.push([s1,s2]);
    }
  }
return {C, PB, NP, clr};
"""

def apply(moves):
    code = """
    const mv = %s;
    const comps = await eda.pcb_PrimitiveComponent.getAll();
    const by={}; for(const c of comps){ try{by[c.getState_Designator()]=c;}catch(e){} }
    let ok=0; for(const m of mv){ const c=by[m.des]; if(c){ try{ await eda.pcb_PrimitiveComponent.modify(c,{x:m.x,y:m.y}); ok++; }catch(e){} } }
    await eda.pcb_Document.save();
    return ok;
    """ % json.dumps(moves)
    return ejs(code)["result"]

orig = {}
for it in range(7):
    d = ejs(GET)["result"]
    C, PB, NP, clr = d["C"], d["PB"], d["NP"], d["clr"]
    if not orig:
        orig = {k: (v["x"], v["y"]) for k, v in C.items()}
    # 부품쌍으로 집계
    pairs = set()
    for a, b in clr:
        da, db = desig(a), desig(b)
        if da in C and db in C and da != db:
            pairs.add(tuple(sorted((da, db))))
    print(f"[iter {it}] pad-clearance pairs: {len(pairs)}")
    if not pairs:
        break
    push = {}  # des -> [dx,dy]
    for da, db in pairs:
        # 가벼운(패드 적은) 쪽 이동
        mover, fixed = (da, db) if NP.get(da, 0) <= NP.get(db, 0) else (db, da)
        bM, bF = PB[mover], PB[fixed]
        if bM[0] > 1e8 or bF[0] > 1e8:
            continue
        cMx, cMy = (bM[0]+bM[2])/2, (bM[1]+bM[3])/2
        cFx, cFy = (bF[0]+bF[2])/2, (bF[1]+bF[3])/2
        ox = min(bM[2], bF[2]) - max(bM[0], bF[0])
        oy = min(bM[3], bF[3]) - max(bM[1], bF[1])
        mvx = max(0, ox + TARGET); mvy = max(0, oy + TARGET)
        # 더 싼 축으로 분리
        if mvx <= mvy and mvx > 0:
            sgn = 1 if cMx >= cFx else -1
            p = push.setdefault(mover, [0, 0]);
            if abs(mvx) > abs(p[0]): p[0] = sgn*mvx
        elif mvy > 0:
            sgn = 1 if cMy >= cFy else -1
            p = push.setdefault(mover, [0, 0])
            if abs(mvy) > abs(p[1]): p[1] = sgn*mvy
    moves = []
    for des, (dx, dy) in push.items():
        nx = min(BX1-30, max(BX0+30, round(C[des]["x"] + dx)))
        ny = min(BY1-30, max(BY0+30, round(C[des]["y"] + dy)))
        moves.append({"des": des, "x": nx, "y": ny})
    print(f"          moving {len(moves)} comps")
    apply(moves)

print("최종 pad-clearance pairs:", len(pairs) if 'pairs' in dir() else '?')
