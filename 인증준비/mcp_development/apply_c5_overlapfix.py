#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""C5-1: ESP32 스트래핑 패시브 U1 겹침 해소 (R5/C17/R6 모듈 밖으로) + design_flow 동기화."""
import json, urllib.request

MM2MIL = 39.3701
NEW = {"R5": (28.0, 43.0), "C17": (28.0, 40.0), "R6": (52.0, 43.0)}

# 1) design_flow.json 갱신
d = json.load(open("mcp_design_flow.json", encoding="utf-8"))
for c in d["components"]:
    if c["designator"] in NEW:
        c["x"], c["y"] = NEW[c["designator"]]
        c["_note"] = (c.get("_note", "") + " | v1.8 C5: U1 풋프린트 겹침 해소 위해 모듈 밖으로 이동").strip(" |")
json.dump(d, open("mcp_design_flow.json", "w", encoding="utf-8"), ensure_ascii=False, indent=2)

# 2) PCB 이동
def ejs(code):
    req = urllib.request.Request("http://127.0.0.1:49620/execute",
        data=json.dumps({"code": code}).encode("utf-8"),
        headers={"Content-Type": "application/json"}, method="POST")
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.loads(r.read().decode())

moves = [{"des": k, "x": round(v[0]*MM2MIL), "y": round(v[1]*MM2MIL)} for k, v in NEW.items()]
code = """
const moves = %s;
const comps = await eda.pcb_PrimitiveComponent.getAll();
const by = {}; for (const c of comps) { try { by[c.getState_Designator()] = c; } catch(e){} }
let ok=0; const fail=[];
for (const m of moves) {
  const c = by[m.des]; if(!c){ fail.push(m.des); continue; }
  try { await eda.pcb_PrimitiveComponent.modify(c, {x:m.x, y:m.y}); ok++; } catch(e){ fail.push(m.des+':'+e.message); }
}
await eda.pcb_Document.save();
return {ok, fail};
""" % json.dumps(moves)
print(ejs(code).get("result"))
