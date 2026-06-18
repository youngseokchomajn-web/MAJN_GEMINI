#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import sys
from easyeda_mcp_client import EasyEDAMCPClient

def main():
    client = EasyEDAMCPClient()
    if not client.connect():
        print("[ERROR] 브릿지 서버 및 에디터 연결 실패")
        sys.exit(1)
        
    js = """
    try {
        const pours = await eda.pcb_PrimitivePour.getAll();
        if (pours) {
            return pours.map(p => ({
                id: p.id || (typeof p.getState_PrimitiveId === 'function' ? p.getState_PrimitiveId() : 'unknown'),
                net: p.net,
                layer: p.layer || 'unknown'
            }));
        }
    } catch(e) {
        return { error: e.message };
    }
    return [];
    """
    res = client.execute_js(js)
    print("=========================================================")
    print("           [실시간 동박(Copper Pour) 점검 결과]          ")
    print("=========================================================")
    if isinstance(res, dict) and "error" in res:
        print(f"[ERROR] 동박 정보 조회 실패: {res['error']}")
    else:
        print(f"총 발견된 동박(Pour) 개수: {len(res)}개")
        for i, p in enumerate(res, 1):
            print(f"  {i}. ID: {p['id']} | Net: {p['net']} | Layer ID: {p['layer']}")
    print("=========================================================")

if __name__ == "__main__":
    main()
