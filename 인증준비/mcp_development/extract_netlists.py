#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""비파괴: 회로도 넷리스트(정답) + PCB 넷리스트(현재) 추출 -> 파일 저장.
이후 diff로 importChanges가 적용할 변경분 미리 파악."""
import sys, json
from easyeda_mcp_client import EasyEDAMCPClient

JS = r"""
const out = {};
try { out.sch = await eda.sch_Netlist.getNetlist("JLCEDA"); } catch(e){ out.sch_err = e.message; }
try { out.pcb = await eda.pcb_Net.getNetlist("JLCEDA"); } catch(e){ out.pcb_err = e.message; }
return out;
"""

def main():
    client = EasyEDAMCPClient()
    if not client.connect():
        print("[ERROR] 브릿지 연결 실패"); sys.exit(1)
    res = client.execute_js(JS)
    if res.get("sch"):
        with open("netlist_sch.json", "w", encoding="utf-8") as f:
            f.write(res["sch"])
        print(f"[OK] netlist_sch.json ({len(res['sch'])} chars)")
    else:
        print("[WARN] sch netlist:", res.get("sch_err"))
    if res.get("pcb"):
        with open("netlist_pcb.json", "w", encoding="utf-8") as f:
            f.write(res["pcb"])
        print(f"[OK] netlist_pcb.json ({len(res['pcb'])} chars)")
    else:
        print("[WARN] pcb netlist:", res.get("pcb_err"))

if __name__ == "__main__":
    main()
