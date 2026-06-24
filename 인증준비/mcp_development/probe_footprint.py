#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""MP3426 풋프린트/심볼 라이브 검증 (read-only, doc 전환 없음)."""
import json, urllib.request

def ejs(code):
    req = urllib.request.Request("http://127.0.0.1:49620/execute",
        data=json.dumps({"code": code}).encode("utf-8"),
        headers={"Content-Type": "application/json"}, method="POST")
    with urllib.request.urlopen(req, timeout=20) as r:
        return json.loads(r.read().decode("utf-8"))

CODE = r"""
const out = {};
out.libs = Object.keys(eda).filter(k => k.startsWith('lib_'));
for (const ns of ['lib_Footprint','lib_Symbol']) {
  if (eda[ns]) out[ns+'_m'] = Object.getOwnPropertyNames(Object.getPrototypeOf(eda[ns])).filter(x => typeof eda[ns][x]==='function');
}
// MP3426 footprint pads (uuid from lib_Device)
try {
  if (eda.lib_Footprint && eda.lib_Footprint.get) {
    const fp = await eda.lib_Footprint.get('1422f161dfdb47e99a72005b5d8d3ad2');
    out.fp_keys = fp ? Object.keys(fp) : null;
    out.fp = JSON.stringify(fp).slice(0, 2000);
  }
} catch(e){ out.fp_err = e.message; }
// MP3426 symbol pins
try {
  if (eda.lib_Symbol && eda.lib_Symbol.get) {
    const sy = await eda.lib_Symbol.get('030e12550a334f1b8efd5dbee031d985');
    out.sym = JSON.stringify(sy).slice(0, 1800);
  }
} catch(e){ out.sym_err = e.message; }
return out;
"""

if __name__ == "__main__":
    try:
        print(json.dumps(ejs(CODE), ensure_ascii=False, indent=1)[:5000])
    except Exception as e:
        print("ERR", e)
