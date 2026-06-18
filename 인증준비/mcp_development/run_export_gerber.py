#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
from easyeda_mcp_client import EasyEDAMCPClient

def main():
    print("=========================================================")
    print("  마중 스마트배시넷 Gerber 파일 내보내기 시작  ")
    print("=========================================================\n")
    
    # 브릿지 클라이언트 초기화 및 연결 테스트
    client = EasyEDAMCPClient()
    if not client.connect():
        print("\n[ERROR] 브릿지 서버 및 에디터 플러그인 연결 실패")
        sys.exit(1)
        
    print("[1/2] 에디터 연결 성공. Gerber 내보내기 API 호출 중...")
    
    # Gerber 내보내기
    success = client.export_gerber()
    if success:
        print("\n=========================================================")
        print(" Gerber 파일 내보내기 성공! ")
        print(f" 저장 경로: {os.path.join(os.getcwd(), 'Gerber_Output.zip')}")
        print("=========================================================")
    else:
        print("\n[ERROR] Gerber 내보내기 실패. 에디터 상태를 확인하십시오.")
        sys.exit(1)

if __name__ == "__main__":
    main()
