#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""비파괴: C2909511의 footprintName + 그 풋프린트의 패드 수 확인."""
import sys, json
from easyeda_mcp_client import EasyEDAMCPClient

JS = r"""
const out = {};
const LCSC = "C2909511";
const devs = await eda.lib_Device.getByLcscIds([LCSC]);
if (!devs || !devs.length || !devs[0]) { out.err='device not found'; return out; }
const d = devs[0];
out.footprintName = d.footprintName;
out.footprintUuid = d.footprintUuid;
out.symbolName = d.symbolName;
out.deviceName = d.name;

// 풋프린트 로드 후 패드 수
try {
  if (eda.lib_Footprint && eda.lib_Footprint.getByUuids) {
    const fps = await eda.lib_Footprint.getByUuids([d.footprintUuid]);
    if (fps && fps.length && fps[0]) {
      const fp = fps[0];
      out.fpKeys = Object.keys(fp).slice(0,30);
      // 패드 수 추정: pads 배열 또는 primitives
      if (fp.pads) out.padCount = fp.pads.length;
    }
  }
} catch(e){ out.fp_err = e.message; }
return out;
"""

def main():
    client = EasyEDAMCPClient()
    if not client.connect():
        print("[ERROR] 브릿지 연결 실패"); sys.exit(1)
    res = client.execute_js(JS)
    print(json.dumps(res, ensure_ascii=False, indent=2, default=str))

if __name__ == "__main__":
    main()
