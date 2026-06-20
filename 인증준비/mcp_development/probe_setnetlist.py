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
    const out = {};
    try {
        const pages = await eda.dmt_Schematic.getAllSchematicPagesInfo();
        if (pages && pages.length > 0) {
            await eda.dmt_EditorControl.openDocument(pages[0].uuid);
            await new Promise(r => setTimeout(r, 1500));
            await eda.dmt_EditorControl.activateDocument(pages[0].uuid);
            await new Promise(r => setTimeout(r, 1500));
            out.activated = pages[0].uuid;
        } else {
            return { success: false, error: "No schematic pages found" };
        }
        
        // 1. Get netlist using BETA/obsolete API
        let origNetlist = "";
        try {
            origNetlist = await eda.sch_Netlist.getNetlist("JLCEDA");
            out.origNetlistLength = origNetlist.length;
            out.origNetlistSnippet = origNetlist.substring(0, 300);
        } catch(e) {
            out.getNetlist_err = e.message;
        }
        
        // 2. Try setNetlist with same netlist or modified one
        if (origNetlist) {
            try {
                await eda.sch_Netlist.setNetlist("JLCEDA", origNetlist);
                out.setNetlist_success = true;
            } catch(e) {
                out.setNetlist_err = e.message;
            }
        }
        
        return { success: true, details: out };
    } catch(e) {
        return { success: false, error: e.message };
    }
    """
    
    res = client.execute_js(js)
    print(json.dumps(res, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()
