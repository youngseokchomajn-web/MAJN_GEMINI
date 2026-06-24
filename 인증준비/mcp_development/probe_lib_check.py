#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""A1 라이브 심볼 검증: lib_Device로 핵심 부품의 심볼 핀/풋프린트 패드 조회 (읽기전용)."""
import sys, json
from easyeda_mcp_client import EasyEDAMCPClient

JS = r"""
try {
  const out = {};
  out.lib_methods = Object.getOwnPropertyNames(Object.getPrototypeOf(eda.lib_Device)||{}).filter(x=>typeof eda.lib_Device[x]==='function');
  let r = null;
  try { r = await eda.lib_Device.getByLcscIds(['C2909511','C51118','C8678','C83329']); }
  catch(e){ out.gbl_err = e.message; }
  if (r){
    out.type = Array.isArray(r)?('array['+r.length+']'):typeof r;
    out.top = JSON.stringify(r).slice(0,1500);
  }
  return {success:true, out};
} catch(e){ return {success:false, error:e.message, stack:(e.stack||'').slice(0,400)}; }
"""

def main():
    c = EasyEDAMCPClient()
    if not c.connect():
        print(json.dumps({"connect": False})); sys.exit(2)
    r = c.execute_js(JS)
    print(json.dumps(r, ensure_ascii=False, indent=1)[:4500])

if __name__ == "__main__":
    main()
