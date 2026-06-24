#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""C5/C6/C7 점검: 배치(보드내·겹침) / GND평면 / 전원pour 패드연결."""
import json, sys, io, urllib.request
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

BX0, BY0, BX1, BY1 = -100, 0, 3200, 2450
# pour 폴리곤 (생성시 값)
VBUS_POLY = (158, 1027, 2442, 1556)   # x0,y0,x1,y1
PVDD_POLY = (2036, 393, 2745, 1281)

def ejs(code):
    req = urllib.request.Request("http://127.0.0.1:49620/execute",
        data=json.dumps({"code": code}).encode("utf-8"),
        headers={"Content-Type": "application/json"}, method="POST")
    with urllib.request.urlopen(req, timeout=150) as r:
        return json.loads(r.read().decode())

CODE = r"""
const out={};
// 부품 + 패드 bbox(실제크기)
const comps=await eda.pcb_PrimitiveComponent.getAll();
const C={}; for(const c of comps){try{C[c.getState_Designator()]={pid:c.getState_PrimitiveId(),x:c.getState_X(),y:c.getState_Y()};}catch(e){}}
const pads=await eda.pcb_PrimitivePad.getAll();
const PB={}; for(const d in C)PB[d]=[1e9,1e9,-1e9,-1e9];
const order=Object.entries(C).sort((a,b)=>b[1].pid.length-a[1].pid.length);
const netpads={VBUS_5V:[],PVDD_12V:[]};
for(const p of pads){try{const pid=p.getState_PrimitiveId(),x=p.getState_X(),y=p.getState_Y();
 let hw=15;try{const pd=p.getState_Pad();if(Array.isArray(pd)&&typeof pd[1]==='number')hw=Math.max(pd[1],pd[2])/2;}catch(e){}
 const n=p.getState_Net?p.getState_Net():''; if(netpads[n])netpads[n].push([Math.round(x),Math.round(y),Math.round(hw)]);
 for(const [d,c] of order){if(pid.startsWith(c.pid)){const b=PB[d];if(x-hw<b[0])b[0]=x-hw;if(y-hw<b[1])b[1]=y-hw;if(x+hw>b[2])b[2]=x+hw;if(y+hw>b[3])b[3]=y+hw;break;}}}catch(e){}}
out.C=C; out.PB=PB; out.netpads=netpads;
// pour + poured
out.pours=(await eda.pcb_PrimitivePour.getAll()).map(p=>{try{return p.getState_Net()+'@L'+p.getState_Layer();}catch(e){return '?';}});
try{out.poured=(await eda.pcb_PrimitivePoured.getAll()).length;}catch(e){out.poured='?';}
// DRC connection by net
const res=await eda.pcb_Drc.check(true,false,true);
out.conn={};
for(const cat of res||[]) if((cat.name||'').includes('Connection'))
 for(const s of cat.list||[]) for(const e of s.list||[]){
   const nm=(e.netName||(e.errData&&e.errData.netName)||(e.obj1&&e.obj1.suffix||'').split(':')[0].replace(/[()]/g,'').trim())||'?';
   out.conn[nm]=(out.conn[nm]||0)+1;
 }
return out;
"""
r = ejs(CODE)["result"]
C, PB, netpads = r["C"], r["PB"], r["netpads"]

print("=== C5 배치 ===")
off = [d for d in C if PB[d][0] < 1e8 and (PB[d][0] < BX0-20 or PB[d][1] < BY0-20 or PB[d][2] > BX1+20 or PB[d][3] > BY1+20)]
print("  보드밖:", off or "없음 (전부 보드내)")
ds = [d for d in C if PB[d][0] < 1e8]
ov = []
for i in range(len(ds)):
    for j in range(i+1, len(ds)):
        a, b = PB[ds[i]], PB[ds[j]]
        ox = min(a[2],b[2])-max(a[0],b[0]); oy = min(a[3],b[3])-max(a[1],b[1])
        if ox > 6 and oy > 6:  # 실제 패드 동박 6mil 이상 겹침
            ov.append(f"{ds[i]}<->{ds[j]}")
print("  패드동박 겹침(>6mil):", ov or "없음 ✓")

print("=== C6 GND 평면 ===")
print("  pours:", r["pours"], "| poured(충전):", r["poured"])

print("=== C7 전원 pour — 패드가 pour 안에 있나 ===")
def inside(poly, pads):
    out_pads = []
    for x, y, hw in pads:
        if not (poly[0] <= x <= poly[2] and poly[1] <= y <= poly[3]):
            out_pads.append((x, y))
    return out_pads
vo = inside(VBUS_POLY, netpads["VBUS_5V"])
po = inside(PVDD_POLY, netpads["PVDD_12V"])
print(f"  VBUS 패드 {len(netpads['VBUS_5V'])}개 중 pour 밖: {len(vo)} {vo if vo else '(전부 안)'}")
print(f"  PVDD 패드 {len(netpads['PVDD_12V'])}개 중 pour 밖: {len(po)} {po if po else '(전부 안)'}")

print("=== Connection 에러 넷별 ===")
conn = sorted(r["conn"].items(), key=lambda t: -t[1])
for nm, n in conn[:25]:
    flag = " ★전원!" if nm in ("VBUS_5V", "PVDD_12V") else ""
    print(f"  {nm}: {n}{flag}")
print("  총 넷:", len(conn), "| 합:", sum(r['conn'].values()))
