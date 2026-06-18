#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
마중 스마트배시넷 EasyEDA MCP 자동 설계 실행 및 DRC 검증 러너 (Bridge Server 연동형)

easyeda-api-skill 브릿지 서버(localhost:49620)를 매개로 하여 로컬 EasyEDA Pro 에디터와
통신하고, 설계된 데이터를 기반으로 기하학적 DRC 검증을 종합적으로 수행합니다.
"""

import json
import time
import os
from easyeda_mcp_client import EasyEDAMCPClient
from mcp_drc_engine import MCPDRCEngine

def main():
    print("=========================================================")
    print("  마중 스마트배시넷 EasyEDA MCP 자동 설계 & DRC 검증 시작  ")
    print("=========================================================\n")
    
    # 1. 설계 구성 데이터 로드
    flow_file = "mcp_design_flow.json"
    if not os.path.exists(flow_file):
        print(f"[ERROR] '{flow_file}' 파일을 찾을 수 없습니다. 경로를 확인하십시오.")
        return
        
    with open(flow_file, "r", encoding="utf-8") as f:
        flow = json.load(f)
        
    print(f"[1/4] 설계 구성 데이터 로드 완료: {flow['project_name']} (v{flow['version']})")
    
    # 2. 브릿지 클라이언트 초기화 및 연결 테스트
    client = EasyEDAMCPClient()
    if not client.connect():
        print("\n>>> 설계 흐름을 중단합니다. 브릿지 서버 상태 및 에디터 플러그인 연결을 검토하십시오. <<<\n")
        return

    try:
        # 프로젝트 생성 및 보드 구성
        client.create_project(flow["project_name"])
        board = flow["board_dimensions"]
        client.configure_pcb(board["width_mm"], board["height_mm"], board["layers"])
        
        # 부품 배치 전 온라인 라이브러리에서 로컬 캐시 자동 확보
        lcsc_ids = [comp["lcsc_id"] for comp in flow["components"]]
        client.cache_components(lcsc_ids)
        
        # 에디터 캔버스 로딩 완벽 완료를 위한 명시적 안전 대기 대기
        print("\n[API] 에디터 캔버스 동기화 대기 중 (15초)...")
        time.sleep(15.0)
        
        # 3. 부품 배치 및 Net 연결 루프 가동
        print("\n[2/4] 핵심 LCSC 부품 기하 배치 및 회로 네트 구성 중...")
        failed_components = []
        for comp in flow["components"]:
            success = client.place_component(
                comp["designator"],
                comp["name"],
                comp["lcsc_id"],
                comp["x"],
                comp["y"],
                comp["angle"]
            )
            if not success:
                failed_components.append(comp["designator"])
            time.sleep(0.05) # Small delay to avoid overloading local socket
            
        if failed_components:
            print(f"\n[ERROR] 부품 배치 실패 감지: {failed_components}")
            print("대책:")
            print("  1. EasyEDA Pro 에디터의 '라이브러리(Library)' 패널(단축키 Shift+F)을 엽니다.")
            print("  2. '立创商城(LCSC)' 또는 '온라인 라이브러리' 검색 모드에서 다음 LCSC ID들을 각각 검색합니다:")
            for comp in flow["components"]:
                if comp["designator"] in failed_components:
                    print(f"     - {comp['designator']}: {comp['lcsc_id']} ({comp['name']})")
            print("  3. 검색 결과 부품을 더블 클릭하여 캐시되게 하거나, PCB 상에 한번 마우스로 클릭해 임시 배치/삭제하여 캐시를 로드해 주십시오.")
            print("  4. 이후 스크립트를 재구동하여 자동 배치를 실행하십시오.\n")
            print(">>> 설계 흐름을 중단합니다. <<<\n")
            return
            
        # 배선 규칙 설정 (우선 등록)
        widths = flow["pcb_constraints"]["routing_widths_mm"]
        for net_name, width in widths.items():
            if net_name == "default":
                continue
            client.set_trace_width(net_name, width)
            
        # Net 연결 루프 가동
        failed_nets = []
        for net_name, pins in flow["nets"].items():
            success = client.connect_net(net_name, pins)
            if not success:
                failed_nets.append(net_name)
            time.sleep(0.05)
            
        if failed_nets:
            print(f"\n[ERROR] Net 배선 실패 감지: {failed_nets}")
            print(">>> 설계 흐름을 중단합니다. <<<\n")
            return
            
        # GND Copper Pour 주입 (4개 층 모두: Top=1, Bottom=2, Inner1=15, Inner2=16)
        print("\n[API] 4-Layer GND Solid Plane 주입 중...")
        client.inject_copper_pour("GND", 1)   # Top Layer
        client.inject_copper_pour("GND", 2)   # Bottom Layer
        client.inject_copper_pour("GND", 15)  # Inner1 Layer
        client.inject_copper_pour("GND", 16)  # Inner2 Layer
            
        # 자동 배선 및 파일 출력 실행
        print("\n[3/4] Auto-Routing & Gerber Export 실행...")
        client.auto_route()
        client.export_gerber()
        
        # 4. 자가 진단 DRC 기하 검증 엔진 구동 & 내장 DRC 연동
        print("\n[4/4] DRC Rules 기하 충돌 검사 및 에디터 내장 DRC 연동 검사 작동...")
        design_layout = client.get_layout_data()
        
        # Inject package information from flow into design_layout
        pkg_map = {c["designator"]: c.get("package", "") for c in flow["components"]}
        for c in design_layout.get("components", []):
            c["package"] = pkg_map.get(c.get("designator"), "")
            
        drc_engine = MCPDRCEngine(design_layout, flow["pcb_constraints"])
        drc_report = drc_engine.verify_all()
        
        # 에디터 내장 DRC API 호출
        try:
            native_drc = client.check_native_drc()
        except Exception as drc_ex:
            native_drc = {"success": False, "error": f"DRC API 호출 타임아웃 또는 오류: {drc_ex}"}
            
        if native_drc and native_drc.get("success"):
            err_count = native_drc.get("errorCount", 0)
            passed = native_drc.get("passed", False)
            err_list = native_drc.get("errors", [])
            
            # Convert error objects to readable string format
            err_desc = []
            for err in err_list:
                # err is typically a dict or string
                if isinstance(err, dict):
                    name = err.get("name") or err.get("type") or "Error"
                    det = err.get("detail") or err.get("message") or json.dumps(err)
                    err_desc.append(f"[{name}] {det}")
                else:
                    err_desc.append(str(err))
                    
            detail_str = f"에러 개수: {err_count}개 "
            if passed:
                detail_str += "(통과)"
            else:
                detail_str += f"(오류 내역: {', '.join(err_desc)})"
                
            drc_report.append({
                "rule": f"EasyEDA Pro 에디터 내장 DRC (검출 에러 {err_count}개)",
                "passed": passed,
                "detail": detail_str
            })
        else:
            drc_report.append({
                "rule": "EasyEDA Pro 에디터 내장 DRC 연동",
                "passed": False,
                "detail": f"내장 DRC 실행 실패: {native_drc.get('error') if native_drc else '알 수 없는 응답'}"
            })
            
        print("\n=========================================================")
        print("                [최종 DRC 검증 리포트 요약]               ")
        print("=========================================================")
        
        passed_count = 0
        for i, r in enumerate(drc_report, 1):
            status = "\033[92m[PASS]\033[0m" if r["passed"] else "\033[91m[FAIL]\033[0m"
            if r["passed"]:
                passed_count += 1
            print(f"{i}. {r['rule']}")
            print(f"   ➔ 판정: {status} | 상세: {r['detail']}")
            
        print(f"\n최종 검증 스코어: {passed_count}/{len(drc_report)}")
        if passed_count == len(drc_report):
            print("\033[92m\033[1m>>> SUCCESS: EasyEDA MCP 자동 설계 결과가 규격서 v1.1을 100% 충족합니다! <<<\033[0m\n")
        else:
            print("\033[91m\033[1m>>> FAILURE: 설계 정합성 검사 실패. Bounding Box 배치 정보를 튜닝하십시오. <<<\033[0m\n")
            
    except Exception as e:
        import traceback
        print("\n[ERROR] 설계 실행 중 런타임 에러 발생:")
        traceback.print_exc()
        print("\n")

if __name__ == "__main__":
    main()
