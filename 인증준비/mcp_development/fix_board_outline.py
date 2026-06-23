#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""보드 외곽선과 부품의 export-공간 정합 수정.
export 에서 외곽선 Y가 부호반전되어 부품(+Y)과 안 겹침 → 외곽선을 createPolygon 음수 Y로
재생성하면 export 에서 +Y 로 뒤집혀 부품과 겹침. U1 복구 포함.
검증: 재export 한 ar.json 의 boardOutline 이 부품을 포함하는지 확인."""
import urllib.request, json

WIN='89c31f97-6650-4e5d-a332-fa024a0072b5'
def exec_win(js):
    payload=json.dumps({'code':js,'windowId':WIN}).encode()
    req=urllib.request.Request('http://127.0.0.1:49620/execute',data=payload,headers={'Content-Type':'application/json'},method='POST')
    with urllib.request.urlopen(req,timeout=120) as r:
        res=json.loads(r.read().decode())
    if not res.get('success'): raise RuntimeError(res.get('error'))
    return res.get('result')

# 1) U1 복구 + 외곽선 삭제 + 재생성
js1='''
const out={};
const pcbs=await eda.dmt_Pcb.getAllPcbsInfo();
const p2=(pcbs||[]).find(p=>p.name==="PCB2");
await eda.dmt_EditorControl.activateDocument(p2.uuid);
await new Promise(r=>setTimeout(r,800));
// U1 복구
const comps=await eda.pcb_PrimitiveComponent.getAll();
const u1=comps.find(c=>(c.getState_Designator?c.getState_Designator():c.designator)==="U1");
await eda.pcb_PrimitiveComponent.modify(u1.getState_PrimitiveId(), {x:1574.804, y:1850.3947});
// 기존 외곽선(layer 11) 삭제
const ids=await eda.pcb_PrimitivePolyline.getAllPrimitiveId(undefined, 11);
out.oldOutlineIds=ids;
if(ids&&ids.length){ await eda.pcb_PrimitivePolyline.delete(ids); }
await new Promise(r=>setTimeout(r,500));
// 외곽선 재생성: createPolygon y +2362.2~+4724.4 → export y 0~60 (부품과 정합)
const pts=['R', 0, 2362.206, 3149.608, 2362.206, 0, 0];
const poly=eda.pcb_MathPolygon.createPolygon(pts);
await eda.pcb_PrimitivePolyline.create('', 11, poly, 10);
await new Promise(r=>setTimeout(r,500));
try{ await eda.pcb_Document.save(); out.saved=true; }catch(e){ out.save_err=e.message; }
return out;
'''
print("[1] U1 복구 + 외곽선 재생성...")
print(json.dumps(exec_win(js1), ensure_ascii=True, default=str))

# 2) 재export 하여 boardOutline 이 부품을 포함하는지 검증
js2='''
const f=await eda.pcb_ManufactureData.getAutoRouteJsonFile("ar2.json");
return await f.text();
'''
print("[2] 재export 검증...")
txt=exec_win(js2)
j=json.loads(txt)
bo=j['boardOutline']['bbox']  # [x?, ...]
comps=j['components']
# 부품 위치 범위
xs=[c['location'][0] for c in comps.values()]; ys=[c['location'][1] for c in comps.values()]
print("boardOutline bbox:", bo)
print("boardOutline path:", j['boardOutline']['path'])
print("components x:[%.1f,%.1f] y:[%.1f,%.1f] mm"%(min(xs),max(xs),min(ys),max(ys)))
# 판정: 외곽선 y범위가 부품 y범위를 포함?
import json as _j
open('ar2.json','w',encoding='utf-8').write(txt)
print("[OK] ar2.json saved")
