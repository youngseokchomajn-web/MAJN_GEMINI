#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""design_flow 플로어플랜(mm)을 PCB1에 적용 (mm->mil, 전원-우선 초기배치)."""
import json, urllib.request

MM2MIL = 39.3701
d = json.load(open("mcp_design_flow.json", encoding="utf-8"))
moves = [{"des": c["designator"],
          "x": round(c["x"] * MM2MIL),
          "y": round(c["y"] * MM2MIL),
          "rot": c.get("angle", 0)} for c in d["components"]]

def ejs(code):
    req = urllib.request.Request("http://127.0.0.1:49620/execute",
        data=json.dumps({"code": code}).encode("utf-8"),
        headers={"Content-Type": "application/json"}, method="POST")
    with urllib.request.urlopen(req, timeout=90) as r:
        return json.loads(r.read().decode())

code = """
const moves = %s;
const comps = await eda.pcb_PrimitiveComponent.getAll();
const byDes = {};
for (const c of comps) { try { byDes[c.getState_Designator()] = c; } catch(e){} }
let ok = 0; const fail = [];
for (const m of moves) {
  const c = byDes[m.des];
  if (!c) { fail.push(m.des + ':notfound'); continue; }
  try { await eda.pcb_PrimitiveComponent.modify(c, {x: m.x, y: m.y, rotation: m.rot}); ok++; }
  catch(e) { fail.push(m.des + ':' + (e.message||'err')); }
}
return {ok: ok, fail: fail};
""" % json.dumps(moves)

r = ejs(code).get("result", {})
print("moved:", r.get("ok"), "/", len(moves))
if r.get("fail"): print("fail:", r["fail"][:15])
