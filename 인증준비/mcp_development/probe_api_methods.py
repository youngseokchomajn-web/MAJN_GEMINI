#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""회로도->PCB 동기화(Update PCB) 관련 EDA API 탐색. 읽기 전용."""
import sys, json
from easyeda_mcp_client import EasyEDAMCPClient

PROBE_JS = r"""
const out = { namespaces: [], matches: {} };
const KEYS = ['update','convert','import','netlist','sync','changenet','transfer','schematic','sch','design','pcb'];
for (const ns of Object.keys(eda)) {
  out.namespaces.push(ns);
  let methods = [];
  try {
    const obj = eda[ns];
    if (obj) {
      methods = Object.getOwnPropertyNames(obj).filter(m => typeof obj[m] === 'function');
      // also prototype
      const proto = Object.getPrototypeOf(obj);
      if (proto) methods = methods.concat(Object.getOwnPropertyNames(proto).filter(m => typeof obj[m] === 'function'));
    }
  } catch(e){}
  const hit = methods.filter(m => KEYS.some(k => m.toLowerCase().includes(k)));
  if (hit.length) out.matches[ns] = Array.from(new Set(hit));
}
return out;
"""

def main():
    client = EasyEDAMCPClient()
    if not client.connect():
        print("[ERROR] 브릿지 연결 실패"); sys.exit(1)
    res = client.execute_js(PROBE_JS)
    print(json.dumps(res, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()
