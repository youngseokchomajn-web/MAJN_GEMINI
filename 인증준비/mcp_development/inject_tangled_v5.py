import json
import urllib.request
def execute_js(code):
    url = "http://127.0.0.1:49620/execute"
    payload = json.dumps({"code": code}).encode("utf-8")
    req = urllib.request.Request(url, data=payload, headers={"Content-Type": "application/json"}, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=90) as response:
            res = json.loads(response.read().decode("utf-8"))
            if res.get("success"): return res.get("result")
            return {"error": res.get("error")}
    except Exception as e:
        return {"error": str(e)}

JS = """
try {
    let result = [];
    
    // 1. Set DRC Rules
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
            result.push("DRC updated");
        }
    } catch(e) {}
    
    let compsToPlace = [
        { lcsc: "C165948", x: 4000, y: 4000, angle: 0, des: "TYPE_C" },
        { lcsc: "C84681", x: 4000, y: 4400, angle: 90, des: "SOP16" },
        { lcsc: "C9421", x: 3800, y: 4200, angle: 0, des: "C1" },
        { lcsc: "C9421", x: 4200, y: 4200, angle: 0, des: "C2" }
    ];
    
    for (let c of compsToPlace) {
        try {
            // FORCE hydrate device by searching and getting it
            const searchRes = await eda.lib_Search.search([{ "keyword": c.lcsc }]);
            if (searchRes && searchRes.length > 0) {
                const item = searchRes[0];
                const uuid = item.uuid;
                const fpUuid = item.attributes?.["Footprint UUID"];
                const symUuid = item.attributes?.["Symbol UUID"];
                
                const path = "/LCSC/" + item.title;
                if (symUuid) await eda.lib_Symbol.get(symUuid, path);
                if (fpUuid) await eda.lib_Footprint.get(fpUuid, path);
                let dev = await eda.lib_Device.get(uuid, path);
                
                if (dev) {
                    const primId = await eda.pcb_PrimitiveComponent.create(dev, 1, c.x, c.y, c.angle);
                    if (primId) {
                        let allComps = await eda.pcb_PrimitiveComponent.getAll();
                        let comp = allComps.find(x => x.getState_PrimitiveId() === primId || x.id === primId);
                        if (comp) {
                            try { await comp.setState_Designator(c.des); } catch(e) { comp.designator = c.des; }
                            try { await comp.setState_Rotation(c.angle); } catch(e) { comp.rotation = c.angle; }
                            if (typeof comp.done === 'function') await comp.done();
                            result.push("Placed " + c.des);
                        }
                    } else {
                        result.push("Failed to place " + c.des);
                    }
                }
            } else {
                result.push("Search failed for " + c.lcsc);
            }
        } catch(e) { result.push("Place error for " + c.des + ": " + e.message); }
    }
    
    // 3. Assign Nets
    let allComps = await eda.pcb_PrimitiveComponent.getAll();
    const getCompByDes = (des) => allComps.find(c => (c.getState_Designator ? c.getState_Designator() : c.designator) === des);
    const setNet = async (compDes, pinNum, netName) => {
        try {
            let comp = getCompByDes(compDes);
            if (!comp) return;
            let pads = await eda.pcb_PrimitiveComponent.getAllPinsByPrimitiveId(comp.getState_PrimitiveId());
            let pad = pads.find(p => p.padNumber === pinNum || p.padNumber === pinNum.toString());
            if (pad) {
                try { await pad.setState_Net(netName); } catch(e) { pad.net = netName; }
                if (typeof pad.done === 'function') await pad.done();
            }
        } catch(e) {}
    };
    
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

    return { status: "Done", log: result };
} catch(e) { return { error: e.message }; }
"""
print(json.dumps(execute_js(JS), indent=2))
