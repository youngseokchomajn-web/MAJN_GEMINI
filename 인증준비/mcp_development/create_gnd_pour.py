#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""C6: Inner1(layer15)에 솔리드 GND pour 생성. 보드 20mil 인셋."""
import json, urllib.request

def ejs(code):
    req = urllib.request.Request("http://127.0.0.1:49620/execute",
        data=json.dumps({"code": code}).encode("utf-8"),
        headers={"Content-Type": "application/json"}, method="POST")
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.loads(r.read().decode())

# 보드 X[-100,3200] Y[0,2450] → 20mil 인셋: 'R' [left, top, w, h]
CODE = r"""
const out = {};
out.before = (await eda.pcb_PrimitivePour.getAll()).length;
let poly;
try { poly = eda.pcb_MathPolygon.createPolygon(['R', -80, 2430, 3260, 2410, 0, 0]); out.poly='ok'; }
catch(e){ out.poly_err = e.message; }
try { await eda.pcb_PrimitivePour.create('GND', 15, poly); out.created=true; }
catch(e){ out.create_err = e.message; }
const all = await eda.pcb_PrimitivePour.getAll();
out.after = all.length;
out.pours = [];
for (const p of all) {
  try { out.pours.push({net: p.getState_Net ? p.getState_Net() : '?', layer: p.getState_Layer ? p.getState_Layer() : '?'}); }
  catch(e){ out.pours.push('?'); }
}
await eda.pcb_Document.save();
return out;
"""
print(json.dumps(ejs(CODE).get("result", {}), ensure_ascii=False, indent=1)[:1200])
