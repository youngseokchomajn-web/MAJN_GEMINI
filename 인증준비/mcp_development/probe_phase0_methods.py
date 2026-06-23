#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Phase0: 보드/PCB 생성·회로도→PCB import 관련 API 메서드 덤프 (읽기전용)."""
import sys, json
from easyeda_mcp_client import EasyEDAMCPClient

PROBE_JS = r"""
const out = {};
function methodsOf(ns){
  try {
    const obj = eda[ns];
    if (!obj) return null;
    let m = Object.getOwnPropertyNames(obj).filter(x => { try { return typeof obj[x] === 'function'; } catch(e){ return false; } });
    const proto = Object.getPrototypeOf(obj);
    if (proto) m = m.concat(Object.getOwnPropertyNames(proto).filter(x => x !== 'constructor'));
    return Array.from(new Set(m));
  } catch(e){ return 'ERR:'+e.message; }
}
out.dmt_Board   = methodsOf('dmt_Board');
out.dmt_Pcb     = methodsOf('dmt_Pcb');
out.dmt_Schematic = methodsOf('dmt_Schematic');
out.dmt_EditorControl = methodsOf('dmt_EditorControl');
out.pcb_Document = methodsOf('pcb_Document');
out.sch_Document = methodsOf('sch_Document');
// pcb_ namespaces that might do netlist import
out.pcb_namespaces = Object.keys(eda).filter(k => k.startsWith('pcb_'));
out.sch_namespaces = Object.keys(eda).filter(k => k.startsWith('sch_'));
return out;
"""

def main():
    client = EasyEDAMCPClient()
    if not client.connect():
        print("[ERROR] bridge connect failed"); sys.exit(1)
    res = client.execute_js(PROBE_JS)
    print(json.dumps(res, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()
