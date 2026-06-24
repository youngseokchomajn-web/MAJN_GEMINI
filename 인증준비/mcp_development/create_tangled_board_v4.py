import time
from easyeda_mcp_client import EasyEDAMCPClient
import json
import urllib.request

client = EasyEDAMCPClient()

# 1. Create a new test project
project_name = "Test_Tangled_Board_Project"
print(f"Creating project: {project_name}")
client.create_project(project_name)

# 2. Wait for PCB to be available
time.sleep(3)

# 3. Apply DRC Rules (0.1mm) using execute_js directly
JS_DRC = """
try {
    let config = await eda.pcb_Drc.getCurrentRuleConfiguration();
    if (config) {
        let tables = config.config.Spacing["Safe Spacing"].copperThickness1oz.tables["1"].content;
        for (let r = 0; r < tables.length; r++) {
            for (let c = 0; c < tables[r].length; c++) {
                tables[r][c] = 0.1;
            }
        }
        await eda.pcb_Drc.overwriteCurrentRuleConfiguration(config);
        return true;
    }
} catch(e) {}
return false;
"""
client.execute_js(JS_DRC)
print("Applied 0.1mm DRC Rule")

# 4. Cache parts
parts = ["C165948", "C84681", "C9421"]
print("Caching parts...")
client.cache_components(parts)

# 5. Place Components
print("Placing components...")
# (designator, name, lcsc_id, x_mm, y_mm, angle)
client.place_component("TYPE_C", "USB", "C165948", 100, 100, 0)
client.place_component("SOP16", "CH340C", "C84681", 100, 110, 90) # 10mm apart
client.place_component("C1", "10uF", "C9421", 95, 105, 0)
client.place_component("C2", "10uF", "C9421", 105, 105, 0)

time.sleep(2)

# 6. Assign tangled nets
JS_NETS = """
try {
    let allComps = await eda.pcb_PrimitiveComponent.getAll();
    const getCompByDes = (des) => allComps.find(c => (c.designator || (typeof c.getState_Designator === 'function' && c.getState_Designator())) === des);
    const setNet = async (compDes, pinNum, netName) => {
        let comp = getCompByDes(compDes);
        if (!comp) return;
        let pads = [];
        try { pads = await eda.pcb_PrimitiveComponent.getAllPinsByPrimitiveId(comp.getState_PrimitiveId()); } catch(e) {}
        if (!pads || pads.length === 0 && typeof comp.getPadList === 'function') {
            pads = await comp.getPadList();
        }
        
        let pad = pads.find(p => p.padNumber === pinNum || p.padNumber === pinNum.toString());
        if (pad) {
            try { await pad.setState_Net(netName); } catch(e) {
                pad.net = netName;
            }
            if (typeof pad.done === 'function') await pad.done();
        }
    };
    
    // Cross over assignments
    await setNet("TYPE_C", "A6", "NET_X1");
    await setNet("SOP16", "6", "NET_X1");
    
    await setNet("TYPE_C", "A7", "NET_X2");
    await setNet("SOP16", "5", "NET_X2");
    
    await setNet("TYPE_C", "A4", "NET_VBUS");
    await setNet("SOP16", "16", "NET_VBUS");
    await setNet("C1", "1", "NET_VBUS");
    await setNet("C2", "2", "NET_VBUS");
    
    await setNet("TYPE_C", "A1", "GND");
    await setNet("SOP16", "1", "GND");
    await setNet("C1", "2", "GND");
    await setNet("C2", "1", "GND");
    
    await setNet("TYPE_C", "A5", "NET_CC1");
    await setNet("SOP16", "13", "NET_CC1"); 
    
    await setNet("TYPE_C", "B5", "NET_CC2");
    await setNet("SOP16", "14", "NET_CC2"); 

    return { status: "Success" };
} catch(e) { return { error: e.message }; }
"""
res = client.execute_js(JS_NETS)
print("Assigned Nets:", res)

