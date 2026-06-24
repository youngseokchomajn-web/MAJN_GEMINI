#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""기하기반 부품분리: design_flow 위치에서 시작, 패드 bbox 충돌을 파이썬에서 해소(DRC 무관)."""
import json, sys, io, urllib.request
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

MM2MIL = 39.3701
TARGET = 12  # mil 목표 동박 간격 (실제 패드크기 반영, DRC 6mil 여유)
BX0, BY0, BX1, BY1 = -100, 0, 3200, 2450

def ejs(code):
    req = urllib.request.Request("http://127.0.0.1:49620/execute",
        data=json.dumps({"code": code}).encode("utf-8"),
        headers={"Content-Type": "application/json"}, method="POST")
    with urllib.request.urlopen(req, timeout=120) as r:
        return json.loads(r.read().decode())

# 1) 현재 패드 bbox + 중심 + 패드수 → 풋프린트 half-extent(중심상대) 산출
GET = r"""
const comps=await eda.pcb_PrimitiveComponent.getAll();
const C={};
for(const c of comps){ try{ C[c.getState_Designator()]={pid:c.getState_PrimitiveId(),x:c.getState_X(),y:c.getState_Y()}; }catch(e){} }
const pads=await eda.pcb_PrimitivePad.getAll();
const PB={},NP={}; for(const d in C){PB[d]=[1e9,1e9,-1e9,-1e9];NP[d]=0;}
const order=Object.entries(C).sort((a,b)=>b[1].pid.length-a[1].pid.length);
for(const p of pads){ try{ const pid=p.getState_PrimitiveId(),x=p.getState_X(),y=p.getState_Y();
 let hw=15; try{ const pd=p.getState_Pad(); if(Array.isArray(pd)&&pd.length>=3&&typeof pd[1]==='number') hw=Math.max(pd[1],pd[2])/2; }catch(e){}
 for(const [d,c] of order){ if(pid.startsWith(c.pid)){ const b=PB[d];
   if(x-hw<b[0])b[0]=x-hw; if(y-hw<b[1])b[1]=y-hw; if(x+hw>b[2])b[2]=x+hw; if(y+hw>b[3])b[3]=y+hw; NP[d]++; break; } } }catch(e){} }
return {C,PB,NP};
"""
d = ejs(GET)["result"]
C, PB, NP = d["C"], d["PB"], d["NP"]
flow = {c["designator"]: c for c in json.load(open("mcp_design_flow.json", encoding="utf-8"))["components"]}

# half-extent (중심상대) + 시작위치(design_flow)
PAD = 4  # 패드 외 바디 여유
ext, pos, npad = {}, {}, {}
for des, c in C.items():
    b = PB[des]
    if b[0] > 1e8:
        continue
    ext[des] = (b[0]-c["x"]-PAD, b[1]-c["y"]-PAD, b[2]-c["x"]+PAD, b[3]-c["y"]+PAD)
    f = flow.get(des)
    pos[des] = [round(f["x"]*MM2MIL), round(f["y"]*MM2MIL)] if f else [c["x"], c["y"]]
    npad[des] = NP[des]

def box(des):
    e = ext[des]; p = pos[des]
    return (p[0]+e[0], p[1]+e[1], p[0]+e[2], p[1]+e[3])

dz = list(ext.keys())
for it in range(60):
    moved = 0
    for i in range(len(dz)):
        for j in range(i+1, len(dz)):
            A, B = dz[i], dz[j]
            a, b = box(A), box(B)
            ox = min(a[2], b[2]) - max(a[0], b[0])
            oy = min(a[3], b[3]) - max(a[1], b[1])
            if ox > -TARGET and oy > -TARGET:   # 충돌(간격<TARGET)
                mover = A if npad[A] <= npad[B] else B
                fx, fy = (pos[B] if mover == A else pos[A])
                nx = (a[2]+a[0])/2 if mover == A else (b[2]+b[0])/2
                ny = (a[3]+a[1])/2 if mover == A else (b[3]+b[1])/2
                needx, needy = ox+TARGET, oy+TARGET
                if needx <= needy:
                    pos[mover][0] += (needx if nx >= fx else -needx)
                else:
                    pos[mover][1] += (needy if ny >= fy else -needy)
                pos[mover][0] = min(BX1-30, max(BX0+30, pos[mover][0]))
                pos[mover][1] = min(BY1-30, max(BY0+30, pos[mover][1]))
                moved += 1
    if moved == 0:
        print(f"수렴: iter {it}, 충돌 0")
        break
else:
    print("미수렴(60회)")

# 최종 충돌 카운트
coll = 0
for i in range(len(dz)):
    for j in range(i+1, len(dz)):
        a, b = box(dz[i]), box(dz[j])
        if min(a[2],b[2])-max(a[0],b[0]) > -TARGET and min(a[3],b[3])-max(a[1],b[1]) > -TARGET:
            coll += 1
print("최종 기하충돌:", coll, "| 이동부품:", sum(1 for des in dz if [round(flow[des]['x']*MM2MIL),round(flow[des]['y']*MM2MIL)]!=pos[des] if des in flow))

# 적용: PCB + design_flow
moves = [{"des": des, "x": round(p[0]), "y": round(p[1])} for des, p in pos.items()]
code = """
const mv=%s; const comps=await eda.pcb_PrimitiveComponent.getAll();
const by={}; for(const c of comps){try{by[c.getState_Designator()]=c;}catch(e){}}
let ok=0; for(const m of mv){const c=by[m.des]; if(c){try{await eda.pcb_PrimitiveComponent.modify(c,{x:m.x,y:m.y});ok++;}catch(e){}}}
await eda.pcb_Document.save(); return ok;
""" % json.dumps(moves)
print("PCB 적용:", ejs(code)["result"], "/", len(moves))
dd = json.load(open("mcp_design_flow.json", encoding="utf-8"))
for c in dd["components"]:
    if c["designator"] in pos:
        c["x"] = round(pos[c["designator"]][0]/MM2MIL, 2)
        c["y"] = round(pos[c["designator"]][1]/MM2MIL, 2)
json.dump(dd, open("mcp_design_flow.json", "w", encoding="utf-8"), ensure_ascii=False, indent=2)
print("design_flow 동기화 완료")
