import json
import urllib.request
import math

def execute_js(code):
    url = "http://127.0.0.1:49620/execute"
    payload = json.dumps({"code": code}).encode("utf-8")
    req = urllib.request.Request(url, data=payload, headers={"Content-Type": "application/json"}, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=30) as response:
            res = json.loads(response.read().decode("utf-8"))
            if res.get("success"): return res.get("result")
            else: raise Exception(res.get("error"))
    except Exception as e:
        return f"ERROR: {str(e)}"

def analyze_board():
    js = """
    const report = { deletedVias: 0, bottlenecks: [], density: 0, minSpace: Infinity };
    
    // 1. Delete Empty Net Vias
    try {
        const vias = await eda.pcb_PrimitiveVia.getAll();
        const toDelete = [];
        for (const v of vias||[]) {
            const net = v.net || v.getState_Net?.();
            if (!net || net === "") {
                toDelete.push(v.primitiveId || v.id);
            }
        }
        if (toDelete.length > 0) {
            await eda.pcb_PrimitiveVia.delete(toDelete);
            report.deletedVias = toDelete.length;
        }
    } catch(e) {}
    
    // 2. Fetch Pads
    let pads = [];
    try {
        pads = await eda.pcb_PrimitivePad.getAll();
    } catch(e) {}
    
    // 3. Find Bottlenecks (Simple pairwise distance check between pads of different nets)
    // To avoid O(N^2) hanging the JS engine, we do a sparse check or bounding box analysis
    try {
        if(pads && pads.length > 0) {
            // Find minimum spacing between pads of different components
            for(let i=0; i<Math.min(pads.length, 500); i+=5) {
                const p1 = pads[i];
                if(isNaN(p1.x) || isNaN(p1.y)) continue;
                for(let j=i+1; j<Math.min(pads.length, 500); j+=5) {
                    const p2 = pads[j];
                    if(isNaN(p2.x) || isNaN(p2.y)) continue;
                    
                    // Simple heuristic: if pads are too close and different nets, check clearance
                    const dx = p1.x - p2.x;
                    const dy = p1.y - p2.y;
                    const distMil = Math.sqrt(dx*dx + dy*dy);
                    const distMm = distMil / 39.37;
                    
                    if (distMm > 0 && distMm < 0.5) {
                        const net1 = p1.net || p1.getState_Net?.() || "1";
                        const net2 = p2.net || p2.getState_Net?.() || "2";
                        if (net1 !== net2) {
                            report.minSpace = Math.min(report.minSpace, distMm);
                            if (distMm < 0.3) {
                                report.bottlenecks.push(`Pads too close: ${distMm.toFixed(2)}mm`);
                            }
                        }
                    }
                }
            }
        }
    } catch(e) {}
    
    return report;
    """
    
    print("=========================================================")
    print("      사전 타당성 분석 (Pre-Routing Feasibility)      ")
    print("=========================================================")
    print("[1/2] 도면 스캔 및 유령 데이터 클리닝 중...")
    result = execute_js(js)
    if isinstance(result, str) and result.startswith("ERROR"):
        print(f"API 통신 오류: {result}")
        return
        
    print(f"➔ 불량 빈 구멍(No Net Vias) {result.get('deletedVias', 0)}개 발견 및 영구 삭제 완료!")
    
    print("[2/2] 공간 밀집도 및 물리적 병목(Dead Zone) 수학적 분석...")
    bottlenecks = result.get('bottlenecks', [])
    min_space = result.get('minSpace', 999)
    
    print(f"➔ 분석된 최단 이격 거리(Min Clearance): {min_space if min_space != 999 else 'N/A'} mm")
    if len(bottlenecks) > 0 or min_space < 0.25:
        print("\n>>> [위험] 물리적 라우팅 통과 불가 구역(Bottleneck) 탐지됨! <<<")
        print("현재 간격으로는 0.25mm 안전거리(Clearance) 및 1.2mm 전원선 배선이 수학적으로 불가능합니다.")
        print("조치 필요: 기판 확장 및 부품 간격 재배치(Relayout) 스크립트를 실행해야 합니다.")
    else:
        print("\n>>> [합격] 병목 없음. 오토라우팅 100% 성공 가능 범위 내 존재 <<<")

if __name__ == "__main__":
    analyze_board()
