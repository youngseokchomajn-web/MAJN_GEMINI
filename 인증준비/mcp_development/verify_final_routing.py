#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import urllib.request

def execute_js(code):
    url = "http://127.0.0.1:49620/execute"
    payload = json.dumps({"code": code}).encode("utf-8")
    req = urllib.request.Request(url, data=payload, headers={"Content-Type": "application/json"}, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=45) as response:
            res = json.loads(response.read().decode("utf-8"))
            if res.get("success"): return res.get("result")
            else: raise Exception(res.get("error"))
    except Exception as e:
        return {"error": str(e)}

JS = """
const out = {
    lines: { total: 0, locked: 0, unlocked: 0, target_nets: {} },
    vias: { total: 0, locked: 0, unlocked: 0, target_nets: {} }
};
const target_nets = ["VBUS_5V", "BOOST_SW", "PVDD_12V", "GND"];

try {
    const lines = await eda.pcb_PrimitiveLine.getAll();
    if (lines) {
        out.lines.total = lines.length;
        for (const line of lines) {
            let locked = false;
            try { locked = line.getState_PrimitiveLock(); } catch(e){}
            if (locked) out.lines.locked++;
            else out.lines.unlocked++;

            let net = "";
            try { net = line.getState_Net(); } catch(e){}
            
            if (target_nets.includes(net)) {
                if (!out.lines.target_nets[net]) out.lines.target_nets[net] = { locked: 0, unlocked: 0, count: 0 };
                out.lines.target_nets[net].count++;
                if (locked) out.lines.target_nets[net].locked++;
                else out.lines.target_nets[net].unlocked++;
            }
        }
    }
} catch(e) {
    out.lines.error = e.message;
}

try {
    const vias = await eda.pcb_PrimitiveVia.getAll();
    if (vias) {
        out.vias.total = vias.length;
        for (const via of vias) {
            let locked = false;
            try { locked = via.getState_PrimitiveLock(); } catch(e){}
            if (locked) out.vias.locked++;
            else out.vias.unlocked++;

            let net = "";
            try { net = via.getState_Net(); } catch(e){}
            
            if (target_nets.includes(net)) {
                if (!out.vias.target_nets[net]) out.vias.target_nets[net] = { locked: 0, unlocked: 0, count: 0 };
                out.vias.target_nets[net].count++;
                if (locked) out.vias.target_nets[net].locked++;
                else out.vias.target_nets[net].unlocked++;
            }
        }
    }
} catch(e) {
    out.vias.error = e.message;
}

return out;
"""

def main():
    print("PCB 파워 라우팅 상태 최종 점검 중...")
    result = execute_js(JS)
    if isinstance(result, dict) and "error" in result:
        print(f"[오류] EasyEDA와 통신 실패: {result['error']}")
        return
        
    print("\n--- 배선 (Trace) 상태 ---")
    lines = result.get('lines', {})
    print(f"전체 트레이스: {lines.get('total')}개 (Locked: {lines.get('locked')}, Unlocked: {lines.get('unlocked')})")
    
    for net, info in lines.get('target_nets', {}).items():
        status = "✅ 완벽" if info['unlocked'] == 0 else "❌ 잠금 해제됨"
        print(f" - [{net}] 트레이스 수: {info['count']}개 (Locked: {info['locked']}, Unlocked: {info['unlocked']}) -> {status}")

    print("\n--- 비아 (Via) 상태 ---")
    vias = result.get('vias', {})
    print(f"전체 비아: {vias.get('total')}개 (Locked: {vias.get('locked')}, Unlocked: {vias.get('unlocked')})")
    
    for net, info in vias.get('target_nets', {}).items():
        status = "✅ 완벽" if info['unlocked'] == 0 else "❌ 잠금 해제됨"
        print(f" - [{net}] 비아 수: {info['count']}개 (Locked: {info['locked']}, Unlocked: {info['unlocked']}) -> {status}")

    print("\n✅ 점검 완료! 파워 트레이스와 비아가 모두 올바르게 Locked 상태인지 확인하세요.")

if __name__ == "__main__":
    main()
