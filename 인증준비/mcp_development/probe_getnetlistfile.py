#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import json
from easyeda_mcp_client import EasyEDAMCPClient

def main():
    client = EasyEDAMCPClient()
    if not client.connect():
        print("[ERROR] 브릿지 연결 실패")
        sys.exit(1)
        
    js = """
    try {
        const pages = await eda.dmt_Schematic.getAllSchematicPagesInfo();
        if (pages && pages.length > 0) {
            await eda.dmt_EditorControl.openDocument(pages[0].uuid);
            await new Promise(r => setTimeout(r, 1500));
            await eda.dmt_EditorControl.activateDocument(pages[0].uuid);
            await new Promise(r => setTimeout(r, 1500));
        } else {
            return { success: false, error: "No schematic pages" };
        }
        
        // Try getNetlistFile with JLCEDA_PRO (which is "JLCEDA")
        // Check if ESYS_NetlistType is available. Let's use string "JLCEDA" directly or ESYS_NetlistType.JLCEDA_PRO.
        // E.g. eda.sch_ManufactureData.getNetlistFile("sch_net", "JLCEDA")
        const file = await eda.sch_ManufactureData.getNetlistFile("sch_net", "JLCEDA");
        if (!file) {
            return { success: false, error: "getNetlistFile returned null/undefined" };
        }
        
        const content = await file.text();
        return { success: true, name: file.name, size: file.size, contentSnippet: content.substring(0, 300), content };
    } catch(e) {
        return { success: false, error: e.message, stack: e.stack };
    }
    """
    
    res = client.execute_js(js)
    if res and res.get("success"):
        print("[OK] Netlist File Extracted successfully!")
        print(f"File Name: {res.get('name')}, Size: {res.get('size')} bytes")
        # Save to file
        with open("netlist_sch_file.json", "w", encoding="utf-8") as f:
            f.write(res.get("content"))
        print("Saved to netlist_sch_file.json")
    else:
        print("[ERROR]", res)

if __name__ == "__main__":
    main()
