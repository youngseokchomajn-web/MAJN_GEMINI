#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import json
import time
from easyeda_mcp_client import EasyEDAMCPClient

def main():
    client = EasyEDAMCPClient()
    if not client.connect():
        print("[ERROR] 브릿지 연결 실패")
        sys.exit(1)
        
    js = """
    try {
        // 1. Clear schematic canvas
        const oldComps = await eda.sch_PrimitiveComponent.getAll();
        if (oldComps && oldComps.length > 0) {
            const ids = oldComps.filter(c => c.getState_ComponentType() !== 'sheet').map(c => c.getState_PrimitiveId());
            if (ids.length > 0) await eda.sch_PrimitiveComponent.delete(ids);
        }
        const oldWires = await eda.sch_PrimitiveWire.getAll();
        if (oldWires && oldWires.length > 0) {
            const ids = oldWires.map(w => w.getState_PrimitiveId());
            await eda.sch_PrimitiveWire.delete(ids);
        }
        
        // 2. Create two resistors R1, R2
        // Find C22817 (150k resistor) uuid from online/local library if we can, or just get from libraries list.
        // For testing, let's use the device uuid of C22817. If not found, search it.
        const devs = await eda.lib_Device.getByLcscIds(["C22817"]);
        if (!devs || devs.length === 0 || !devs[0]) {
            return { success: false, error: "C22817 not cached. Please cache it or search it in EasyEDA first." };
        }
        const dev = devs[0];
        
        const r1 = await eda.sch_PrimitiveComponent.create({ libraryUuid: dev.libraryUuid, uuid: dev.uuid }, 100, 100);
        await r1.setState_Designator("R1");
        if (typeof r1.setState_UniqueId === 'function') await r1.setState_UniqueId("link_R1");
        if (typeof r1.done === 'function') await r1.done();
        
        const r2 = await eda.sch_PrimitiveComponent.create({ libraryUuid: dev.libraryUuid, uuid: dev.uuid }, 200, 100);
        await r2.setState_Designator("R2");
        if (typeof r2.setState_UniqueId === 'function') await r2.setState_UniqueId("link_R2");
        if (typeof r2.done === 'function') await r2.done();
        
        await new Promise(r => setTimeout(r, 1000));
        
        // 3. Get original netlist
        const netlistStr = await eda.sch_Netlist.getNetlist("JLCEDA");
        const netlist = JSON.parse(netlistStr);
        
        // 4. Print original netlist components
        const origComps = JSON.stringify(netlist.components);
        
        // 5. Inject a net in JLCEDA netlist structure
        // Let's modify netlist JSON. We want to connect R1 pin 1 and R2 pin 1 to "TEST_NET".
        // Let's inspect JLCEDA netlist format from our SKILL references or by printing it.
        return { success: true, origNetlist: netlist, R1_uuid: r1.getState_PrimitiveId(), R2_uuid: r2.getState_PrimitiveId() };
        
    } catch(e) {
        return { success: false, error: e.message, stack: e.stack };
    }
    """
    
    res = client.execute_js(js)
    print(json.dumps(res, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()
