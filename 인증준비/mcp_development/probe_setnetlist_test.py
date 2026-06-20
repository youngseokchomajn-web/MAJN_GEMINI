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
        // 1. Get current netlist
        const file = await eda.sch_ManufactureData.getNetlistFile("sch_net", "JLCEDA");
        if (!file) return { success: false, error: "No netlist file" };
        
        const netlistStr = await file.text();
        const netlist = JSON.parse(netlistStr);
        
        // 2. Modify netlist - connect R1 pin 1 and R2 pin 1 to TEST_NET
        if (netlist.components.link_R1 && netlist.components.link_R2) {
            netlist.components.link_R1.pinInfoMap["1"].net = "TEST_NET";
            netlist.components.link_R2.pinInfoMap["1"].net = "TEST_NET";
        } else {
            return { success: false, error: "R1 or R2 not found in netlist. Run probe_setnetlist_connect.py first to create them." };
        }
        
        // 3. Set modified netlist
        const modifiedStr = JSON.stringify(netlist);
        await eda.sch_Netlist.setNetlist("JLCEDA", modifiedStr);
        
        // 4. Retrieve netlist again to verify
        const fileVerify = await eda.sch_ManufactureData.getNetlistFile("sch_net_verify", "JLCEDA");
        const verifyStr = await fileVerify.text();
        const verifyJson = JSON.parse(verifyStr);
        
        const r1Net = verifyJson.components.link_R1.pinInfoMap["1"].net;
        const r2Net = verifyJson.components.link_R2.pinInfoMap["1"].net;
        
        return { 
            success: true, 
            r1Net, 
            r2Net, 
            match: r1Net === "TEST_NET" && r2Net === "TEST_NET"
        };
    } catch(e) {
        return { success: false, error: e.message, stack: e.stack };
    }
    """
    
    res = client.execute_js(js)
    print(json.dumps(res, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()
