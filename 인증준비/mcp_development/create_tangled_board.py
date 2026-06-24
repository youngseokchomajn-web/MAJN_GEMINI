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
    // 1. Create a new Board
    let newBoard = await eda.dmt_Board.createBoard();
    if (!newBoard) return { error: "Failed to create board" };
    
    // 2. Find PCB in the new board
    let pcbs = await eda.dmt_Pcb.getAllPcbsInfo();
    let pcb = pcbs.find(p => p.parentProjectUuid === newBoard.parentProjectUuid);
    if (!pcb) return { error: "Failed to find PCB in new board" };
    
    // 3. Open and activate the PCB
    await eda.dmt_EditorControl.openDocument(pcb.uuid);
    await new Promise(resolve => setTimeout(resolve, 3000));
    await eda.dmt_EditorControl.activateDocument(pcb.uuid);
    await new Promise(resolve => setTimeout(resolve, 2000));
    
    // 4. Set DRC Rules to 0.1mm (since it's a new board)
    let config = await eda.pcb_Drc.getCurrentRuleConfiguration();
    if (config) {
        let tables = config.config.Spacing["Safe Spacing"].copperThickness1oz.tables["1"].content;
        for (let r = 0; r < tables.length; r++) {
            for (let c = 0; c < tables[r].length; c++) {
                tables[r][c] = 0.1;
            }
        }
        try {
            config.config.Track.Track["Track Width"].tables["1"].content[0] = 0.15;
            config.config.Track.Track["Track Width"].tables["1"].content[1] = 0.15;
        } catch(e) {}
        await eda.pcb_Drc.overwriteCurrentRuleConfiguration(config);
    }
    
    // 5. Place Components
    let compsToPlace = [
        { lcsc: "C165948", x: 4000, y: 4000, angle: 0, des: "TYPE_C" },
        { lcsc: "C84681", x: 4000, y: 4400, angle: 90, des: "SOP16" }, // 400 mil apart
        { lcsc: "C9421", x: 3800, y: 4200, angle: 0, des: "C1" },
        { lcsc: "C9421", x: 4200, y: 4200, angle: 0, des: "C2" }
    ];
    
    let placedIds = {};
    for (let c of compsToPlace) {
        let fpUrl = await eda.sys_ClientUrl.getComponentLibraryUrl(c.lcsc);
        let fpInfo = await eda.lib_Footprint.getFootprintInfo(fpUrl);
        let primId = await eda.pcb_PrimitiveComponent.place(fpInfo, c.x, c.y);
        
        // Wait for placement to take effect
        await new Promise(resolve => setTimeout(resolve, 500));
        
        let allComps = await eda.pcb_PrimitiveComponent.getAll();
        let justPlaced = allComps.find(x => (x.id || x.primitiveId || x.getState_PrimitiveId?.()) === primId);
        
        if (justPlaced) {
            await eda.pcb_PrimitiveComponent.modify(primId, {
                designator: c.des,
                rotation: c.angle
            });
            placedIds[c.des] = primId;
        }
    }
    
    // 6. Tangled Nets Assignment
    // We want to assign nets such that they cross over each other.
    let allComps = await eda.pcb_PrimitiveComponent.getAll();
    
    const getCompByDes = (des) => allComps.find(c => c.getState_Designator?.() === des || c.designator === des);
    const setNet = async (compDes, pinNum, netName) => {
        let comp = getCompByDes(compDes);
        if (!comp) return;
        let pads = await eda.pcb_PrimitiveComponent.getAllPinsByPrimitiveId(comp.getState_PrimitiveId());
        let pad = pads.find(p => p.padNumber === pinNum || p.padNumber === pinNum.toString());
        if (pad) {
            pad.net = netName;
            if (typeof pad.done === 'function') await pad.done();
        }
    };
    
    // Cross over assignments
    // Type-C has B12, B1, A1, A12 (GND) -> we ignore for simplicity
    // Let's use some data pins. A6(Dp), A7(Dn), B6(Dp), B7(Dn)
    // We connect them to SOP-16 (CH340) pins: 5(UD+), 6(UD-)
    // We will cross them: A6 -> 6(UD-), A7 -> 5(UD+)
    await setNet("TYPE_C", "A6", "NET_X1");
    await setNet("SOP16", "6", "NET_X1");
    
    await setNet("TYPE_C", "A7", "NET_X2");
    await setNet("SOP16", "5", "NET_X2");
    
    // Another cross
    // Type-C A4, A9, B4, B9 (VBUS)
    // SOP16 16 (VCC)
    // C1, C2
    await setNet("TYPE_C", "A4", "NET_VBUS");
    await setNet("SOP16", "16", "NET_VBUS");
    await setNet("C1", "1", "NET_VBUS");
    await setNet("C2", "2", "NET_VBUS");
    
    await setNet("TYPE_C", "A1", "GND");
    await setNet("SOP16", "1", "GND");
    await setNet("C1", "2", "GND");
    await setNet("C2", "1", "GND");
    
    // Extra tangling
    await setNet("TYPE_C", "A5", "NET_CC1");
    await setNet("SOP16", "13", "NET_CC1"); // DTR
    
    await setNet("TYPE_C", "B5", "NET_CC2");
    await setNet("SOP16", "14", "NET_CC2"); // RTS

    return { status: "Success", message: "Created tangled board with components and nets" };
} catch(e) { return { error: e.message }; }
"""
print(json.dumps(execute_js(JS), indent=2))
