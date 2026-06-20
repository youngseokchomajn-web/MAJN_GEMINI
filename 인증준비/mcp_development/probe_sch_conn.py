#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""비파괴: 회로도 전기적 연결성 진단.
- 와이어/네트라벨/네트포트 개수
- 회로도 넷리스트(가능하면) -> C12/C1 등 핵심 핀의 실제 net
- PCB는 손대지 않음."""
import sys, json
from easyeda_mcp_client import EasyEDAMCPClient

SCHPG_UUID = "6085a53b74cfcf6b"

JS = f"""
const out = {{}};
try {{
  await eda.dmt_EditorControl.openDocument("{SCHPG_UUID}");
  await new Promise(r=>setTimeout(r,1000));
  await eda.dmt_EditorControl.activateDocument("{SCHPG_UUID}");
  await new Promise(r=>setTimeout(r,1200));
}} catch(e){{}}

async function cnt(ns){{
  try {{ if (eda[ns] && eda[ns].getAll) {{ const a = await eda[ns].getAll(); return (a||[]).length; }} }} catch(e){{ return 'ERR:'+e.message; }}
  return 'no_getAll';
}}
out.wires = await cnt('sch_PrimitiveWire');
out.components = await cnt('sch_PrimitiveComponent');

// sch_Net 네임스페이스로 넷 목록 시도
try {{
  if (eda.sch_Net && eda.sch_Net.getNetlist) {{
    const nl = await eda.sch_Net.getNetlist();
    out.sch_Net_type = typeof nl;
    if (Array.isArray(nl)) {{
      out.netCount = nl.length;
      out.netNames = nl.map(n => (n.name||n.netName||n.net||Object.keys(n)[0])).slice(0,60);
    }} else if (typeof nl === 'string') {{
      out.netlistStr_len = nl.length;
      out.netlistStr_head = nl.slice(0,500);
    }} else if (nl) {{
      out.netKeys = Object.keys(nl).slice(0,60);
    }}
  }} else {{ out.sch_Net = 'no getNetlist'; }}
}} catch(e){{ out.sch_Net_err = e.message; }}

// 와이어 샘플 (있으면 net 확인)
try {{
  if (eda.sch_PrimitiveWire && eda.sch_PrimitiveWire.getAll) {{
    const ws = await eda.sch_PrimitiveWire.getAll();
    out.wireSample = (ws||[]).slice(0,5).map(w => {{
      let net=null; try{{ net = w.net ?? w.getState_Net?.(); }}catch(e){{}}
      return {{ net }};
    }});
  }}
}} catch(e){{}}

return out;
"""

def main():
    client = EasyEDAMCPClient()
    if not client.connect():
        print("[ERROR] 브릿지 연결 실패"); sys.exit(1)
    res = client.execute_js(JS)
    with open("probe_sch_conn_out.json","w",encoding="utf-8") as f:
        json.dump(res,f,ensure_ascii=False,indent=2,default=str)
    print(json.dumps(res, ensure_ascii=False, indent=2, default=str)[:1500])

if __name__ == "__main__":
    main()
