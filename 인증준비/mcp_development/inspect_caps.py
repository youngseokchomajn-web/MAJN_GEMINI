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
        const result = {};
        for (const des of ['C8', 'C9', 'C6', 'C7']) {
            const comp = comps.find(c => c.getState_Designator() === des);
            if (comp) {
                const pads = await eda.pcb_PrimitiveComponent.getAllPinsByPrimitiveId(comp.getState_PrimitiveId());
                result[des] = pads.map(p => ({
                    padNumber: p.padNumber,
                    net: p.net || p.getState_Net?.() || "",
                    x: p.x,
                    y: p.y
                }));
            }
        }
        return result;
    } catch(e) {
        return { error: e.message, stack: e.stack };
    }
    """
    
    res = client.execute_js(js)
    pprint.pprint(res)

if __name__ == "__main__":
    main()
