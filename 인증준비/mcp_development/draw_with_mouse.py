import json, urllib.request, subprocess, time

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

def run_cmd(cmd):
    subprocess.run(cmd, shell=True)

# 1. Bring EasyEDA-Pro to front
print("Activating EasyEDA-Pro...")
run_cmd("osascript -e 'tell application \"EasyEDA-Pro\" to activate'")
time.sleep(1)

# 2. Get current primitive count to find the new one later
JS_BEFORE = "return Object.keys(eda.pcb_Document.currentDocument.primitives).length;"
count_before = execute_js(JS_BEFORE)

# 3. Activate Copper Region tool via API
print("Activating copper tool...")
JS_TOOL = "eda.sys_Command.execute('pcb_copper_region'); return true;"
execute_js(JS_TOOL)
time.sleep(1)

# 4. Use cliclick to draw
print("Drawing with cliclick...")
# coordinates: 400,300 -> 1100,300 -> 1100,800 -> 400,800 -> right click
cliclick_script = "cliclick c:400,300 w:500 c:1100,300 w:500 c:1100,800 w:500 c:400,800 w:500 rc:400,800 w:500 kp:esc"
run_cmd(cliclick_script)
time.sleep(1)

# 5. Find new primitive and set net to GND
JS_AFTER = """
try {
    let prims = eda.pcb_Document.currentDocument.primitives;
    let newPrim = null;
    let copperCount = 0;
    
    // We don't have the exact ID, but we can look for the newest CopperRegion
    for (let k in prims) {
        let p = prims[k];
        if (p.primitiveType === "CopperRegion" || p.primitiveType === "Region" || p.primitiveType === "Pour") {
            copperCount++;
            newPrim = p; // just grab the last one
        }
    }
    
    if (newPrim) {
        // Find GND net internal ID
        let nets = await eda.pcb_PrimitiveNet.getAll();
        let gndId = "GND";
        if (nets) {
            for (let n of nets) {
                if (n.name === "GND") gndId = n.primitiveId;
            }
        }
        
        // Update its net
        newPrim.net = gndId;
        
        // Rebuild copper
        if (eda.sys_Command.hasCommand("pcb_rebuildAllCopper")) {
            eda.sys_Command.execute("pcb_rebuildAllCopper");
        }
        return { status: "Success", newPrimType: newPrim.primitiveType, gndId: gndId };
    }
    
    return { status: "No CopperRegion found", copperCount: copperCount };
} catch(e) { return { error: e.message }; }
"""
res = execute_js(JS_AFTER)
print(json.dumps(res, indent=2))
