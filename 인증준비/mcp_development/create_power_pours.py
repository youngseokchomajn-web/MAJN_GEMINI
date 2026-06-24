#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""C7: VBUS_5V·PVDD_12V Top(layer1) 구리 pour 생성. 패드영역+여유."""
import json, urllib.request

def ejs(code):
    req = urllib.request.Request("http://127.0.0.1:49620/execute",
        data=json.dumps({"code": code}).encode("utf-8"),
        headers={"Content-Type": "application/json"}, method="POST")
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.loads(r.read().decode())

# 'R' [left, top(maxY), width, height]
# VBUS bbox[218,1087,2382,1496]+60 -> left158 top1556 w2284 h529
# PVDD bbox[2096,453,2685,1221]+60 -> left2036 top1281 w709 h888
CODE = r"""
const out={before:(await eda.pcb_PrimitivePour.getAll()).length, mk:[]};
const mk = async (net, rect) => {
  let poly=null, err='';
  try { poly = eda.pcb_MathPolygon.createPolygon(['R', rect[0], rect[1], rect[2], rect[3], 0, 0]); } catch(e){ err='poly:'+e.message; }
  try { await eda.pcb_PrimitivePour.create(net, 1, poly); } catch(e){ err += ' create:'+e.message; }
  out.mk.push({net, err: err||'ok'});
};
await mk('VBUS_5V', [158, 1556, 2284, 529]);
await mk('PVDD_12V', [2036, 1281, 709, 888]);
const all = await eda.pcb_PrimitivePour.getAll();
out.after = all.length;
out.pours = all.map(p=>{ try{return p.getState_Net()+'@L'+p.getState_Layer();}catch(e){return '?';} });
await eda.pcb_Document.save();
return out;
"""
print(json.dumps(ejs(CODE).get("result", {}), ensure_ascii=False, indent=1)[:1200])
