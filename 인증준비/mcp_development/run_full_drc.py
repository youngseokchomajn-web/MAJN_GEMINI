#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
마중 스마트배시넷 EasyEDA DRC 종합 검증 러너 (run_full_drc.py)
"""

import json
import os
import sys
from easyeda_mcp_client import EasyEDAMCPClient
from mcp_drc_engine import MCPDRCEngine

def main():
    print("=========================================================")
    print("      마중 스마트배시넷 EasyEDA DRC 종합 검증 시작      ")
    print("=========================================================\n")
    
    # 1. 설계 구성 데이터 로드
    flow_file = "mcp_design_flow.json"
    if not os.path.exists(flow_file):
        print(f"[ERROR] '{flow_file}' 파일을 찾을 수 없습니다. 경로를 확인하십시오.")
        sys.exit(1)
        
    with open(flow_file, "r", encoding="utf-8") as f:
        flow = json.load(f)
        
    print(f"설계 데이터 로드 완료: {flow['project_name']} (v{flow['version']})")
    
    # 2. 브릿지 클라이언트 초기화 및 연결
    client = EasyEDAMCPClient()
    if not client.connect():
        print("[ERROR] 브릿지 서버 및 에디터 연결 실패")
        sys.exit(1)

    # 3. project_data 구성 (기하학적 검증 엔진을 위해 flow 데이터 적용)
    client.project_data["name"] = flow["project_name"]
    client.project_data["components"] = flow["components"]
    client.project_data["nets"] = flow["nets"]
    client.project_data["pcb_settings"]["dimensions"] = (flow["board_dimensions"]["width_mm"], flow["board_dimensions"]["height_mm"])
    client.project_data["pcb_settings"]["layers"] = flow["board_dimensions"]["layers"]
    client.project_data["pcb_settings"]["traces"] = flow["pcb_constraints"]["routing_widths_mm"]

    # 4. 자체 DRC 검증 엔진 구동
    print("\n[1/2] 자체 기하학적 규칙 검사 구동 중...")
    drc_engine = MCPDRCEngine(client.project_data, flow["pcb_constraints"])
    drc_report = drc_engine.verify_all()

    # 5. 에디터 내장 DRC 연동 검사
    print("[2/2] EasyEDA Pro 에디터 내장 DRC 실행 중...")
    try:
        native_drc = client.check_native_drc()
    except Exception as drc_ex:
        native_drc = {"success": False, "error": f"DRC API 호출 타임아웃 또는 오류: {drc_ex}"}

    if native_drc and native_drc.get("success"):
        err_count = native_drc.get("errorCount", 0)
        passed = native_drc.get("passed", False)
        err_list = native_drc.get("errors", [])
        
        err_desc = []
        for err in err_list:
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
    print("                [DRC 검증 리포트 요약]               ")
    print("=========================================================")
    
    passed_count = 0
    for i, r in enumerate(drc_report, 1):
        status = "[PASS]" if r["passed"] else "[FAIL]"
        if r["passed"]:
            passed_count += 1
        print(f"{i}. {r['rule']}")
        print(f"   ➔ 판정: {status} | 상세: {r['detail']}")
        
    print(f"\n최종 검증 스코어: {passed_count}/{len(drc_report)}")
    if passed_count == len(drc_report):
        print("\n>>> SUCCESS: EasyEDA MCP 자동 설계 결과가 규격서 v1.1을 100% 충족합니다! <<<\n")
    else:
        print("\n>>> FAILURE: 일부 설계 정합성 검사 실패. <<<\n")
        sys.exit(1)

if __name__ == "__main__":
    main()
