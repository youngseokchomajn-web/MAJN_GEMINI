#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""비파괴: delete 메서드 시그니처 확인."""
import sys, json
from easyeda_mcp_client import EasyEDAMCPClient

JS = r"""
const out = {};
try { out.comp_delete = eda.pcb_PrimitiveComponent.delete.toString().slice(0,300); } catch(e){}
try { out.pour_delete = eda.pcb_PrimitivePour.delete.toString().slice(0,300); } catch(e){}
try { out.line_delete = eda.pcb_PrimitiveLine.delete.toString().slice(0,300); } catch(e){}
try { out.pour_getAll = eda.pcb_PrimitivePour.getAll.toString().slice(0,200); } catch(e){}
return out;
"""

def main():
    client = EasyEDAMCPClient()
    if not client.connect():
        print("[ERROR] 브릿지 연결 실패"); sys.exit(1)
    print(json.dumps(client.execute_js(JS), ensure_ascii=False, indent=2, default=str))

if __name__ == "__main__":
    main()
