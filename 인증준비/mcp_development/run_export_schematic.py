#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import base64
import os
import sys
from easyeda_mcp_client import EasyEDAMCPClient

def main():
    print("=========================================================")
    print("      마중 스마트배시넷 회로도(Schematic) PDF 출력 시작  ")
    print("=========================================================\n")
    
    client = EasyEDAMCPClient()
    if not client.connect():
        print("[ERROR] 브릿지 서버 및 에디터 연결 실패")
        sys.exit(1)
        
    print("[1/2] 에디터 연결 성공. 회로도 PDF 변환 API 호출 중...")
    
    js = """
    try {
        try {
            const pages = await eda.dmt_Project.getCurrentSchematicAllSchematicPagesInfo();
            if (pages && pages.length > 0) {
                const schUuid = pages[0].uuid;
                await eda.dmt_EditorControl.openDocument(schUuid);
                await new Promise(resolve => setTimeout(resolve, 1500));
                await eda.dmt_EditorControl.activateDocument(schUuid);
                await new Promise(resolve => setTimeout(resolve, 1500));
            }
        } catch(schErr) {
            console.warn("Failed to activate schematic page: " + schErr.message);
        }
        
        const file = await eda.sch_ManufactureData.getExportDocumentFile('Schematic_Output', 'PDF');
        if (file) {
            return new Promise((resolve) => {
                const reader = new FileReader();
                reader.onloadend = () => {
                    const base64 = reader.result.split(',')[1];
                    resolve({ success: true, filename: file.name || 'Schematic_Output.pdf', data: base64 });
                };
                reader.onerror = () => {
                    resolve({ success: false, error: 'FileReader error' });
                };
                reader.readAsDataURL(file);
            });
        }
    } catch(e) {
        return { success: false, error: e.message };
    }
    return { success: false, error: 'Schematic File not found' };
    """
    
    res = client.execute_js(js)
    if res and res.get("success"):
        file_data = base64.b64decode(res["data"])
        filename = res.get("filename", "Schematic_Output.pdf")
        output_path = os.path.join(os.getcwd(), filename)
        with open(output_path, "wb") as f:
            f.write(file_data)
        print("\n=========================================================")
        print(" 회로도 PDF 내보내기 성공! ")
        print(f" 저장 경로: {output_path}")
        print("=========================================================")
    else:
        err = res.get("error") if res else "Unknown response"
        print(f"\n[ERROR] 회로도 내보내기 실패: {err}")
        sys.exit(1)

if __name__ == "__main__":
    main()
