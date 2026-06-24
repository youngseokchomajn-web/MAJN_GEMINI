import sys
sys.path.append("/Users/youngseok/Desktop/majn/인증준비/mcp_development")
from easyeda_mcp_client import EasyEDAMCPClient
import pprint

def main():
    client = EasyEDAMCPClient()
    if not client.connect():
        print("Failed to connect")
        return
        
    js = """
    try {
        const comps = await eda.pcb_PrimitiveComponent.getAll();
        const u4 = comps.find(c => c.getState_Designator() === 'U4');
        if (!u4) return "U4 NOT FOUND";
        
        const pads = await eda.pcb_PrimitiveComponent.getAllPinsByPrimitiveId(u4.getState_PrimitiveId());
        
        return {
            designator: 'U4',
            padCount: pads.length,
            pads: pads.map(p => ({ 
                padNumber: p.padNumber, 
                net: p.net || p.getState_Net?.() || "",
                x: p.x, 
                y: p.y 
            }))
        };
    } catch(e) {
        return { error: e.message, stack: e.stack };
    }
    """
    
    print("Inspecting U4 pads on PCB...")
    res = client.execute_js(js)
    pprint.pprint(res)

if __name__ == "__main__":
    main()
