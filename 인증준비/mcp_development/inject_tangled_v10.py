import time
import json
from easyeda_mcp_client import EasyEDAMCPClient

def main():
    client = EasyEDAMCPClient()
    if not client.connect():
        print("Failed to connect.")
        return

    # 1. Get current PCB
    pcb_info = client.execute_js("return eda.dmt_Pcb.getCurrentPcbInfo();")
    if not pcb_info or "uuid" not in pcb_info:
        print("Error: No active PCB found.")
        return
    pcb_uuid = pcb_info["uuid"]
    print(f"Active PCB: {pcb_uuid}")

    # 2. Activate document
    JS_ACTIVATE = f"""
    try {{
        await eda.dmt_EditorControl.activateDocument("{pcb_uuid}");
        return {{status: "Activated"}};
    }} catch(e) {{ return {{error: e.message}}; }}
    """
    client.execute_js(JS_ACTIVATE)
    time.sleep(1.0)

    # 3. Create dummy region to initialize attrsMap
    JS_INIT = """
    try {
        await eda.pcb_PrimitiveRegion.create({
            "layerId": "97",
            "pathStr": "M 0 0 L 10 0 L 10 10 L 0 10 Z",
            "lineWidth": 1
        });
        return {status: "Init"};
    } catch(e) { return {error: e.message}; }
    """
    client.execute_js(JS_INIT)

    # 4. Set DRC to 0.1mm
    JS_RULE = """
    try {
        let rule = await eda.pcb_Drc.getCurrentRuleConfiguration();
        rule.clearanceRules.defaultClearance = 0.1;
        rule.clearanceRules.trackToTrack = 0.1;
        rule.clearanceRules.trackToSmdPad = 0.1;
        rule.clearanceRules.trackToThPad = 0.1;
        rule.clearanceRules.trackToVia = 0.1;
        rule.clearanceRules.smdPadToSmdPad = 0.1;
        rule.clearanceRules.smdPadToThPad = 0.1;
        rule.clearanceRules.smdPadToVia = 0.1;
        await eda.pcb_Drc.overwriteCurrentRuleConfiguration(rule);
        return {status: "Rule updated"};
    } catch(e) { return {error: e.message}; }
    """
    client.execute_js(JS_RULE)

    # 5. Place components using working client method
    print("Placing components...")
    client.place_component("TYPE_C", "USB", "C165948", 50, 50, 0)
    client.place_component("SOP16", "SOP", "C84681", 60, 60, 45)
    client.place_component("C1", "CAP", "C9421", 40, 60, 90)
    client.place_component("C2", "CAP", "C9421", 70, 50, 0)

    # 6. Assign Nets
    print("Assigning Nets...")
    JS_NETS = f"""
    try {{
        let allPads = await eda.pcb_PrimitivePad.getAll();
        let comps = await eda.pcb_PrimitiveComponent.getAll();
        
        let compMap = {{}};
        for (let c of comps) {{
            let cid = c.getState_PrimitiveId ? c.getState_PrimitiveId() : (c.id || c.primitiveId);
            let des = c.designator;
            if (!des && typeof c.getState_Designator === 'function') des = c.getState_Designator();
            if (cid && des) compMap[cid] = des;
        }}
        
        let netMap = {{
            "TYPE_C": {{"A5": "NET_CC1", "B5": "NET_CC2", "A9": "NET_VBUS", "B9": "NET_VBUS", "A12": "GND", "B12": "GND"}},
            "SOP16": {{"13": "NET_CC1", "14": "NET_CC2", "1": "GND", "16": "NET_VBUS", "8": "NET_X1", "9": "NET_X2"}},
            "C1": {{"1": "NET_X1", "2": "GND"}},
            "C2": {{"1": "GND", "2": "NET_X2"}}
        }};
        
        for (let p of allPads) {{
            let cid = typeof p.getState_ComponentId === 'function' ? p.getState_ComponentId() : p.componentId;
            let pnum = p.number || (typeof p.getState_Number === 'function' ? p.getState_Number() : null);
            let des = compMap[cid];
            
            if (des && netMap[des] && netMap[des][pnum]) {{
                p.setState_Net(netMap[des][pnum]);
            }}
        }}
        return {{status: "Success"}};
    }} catch(e) {{ return {{error: e.message}}; }}
    """
    res = client.execute_js(JS_NETS)
    print("Assigned Nets:", res)
    print("Done injecting perfectly.")

if __name__ == "__main__":
    main()
