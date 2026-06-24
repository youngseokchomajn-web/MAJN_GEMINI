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
    const lcsc = "C165948";
    const devices = await eda.lib_Device.getByLcscIds([lcsc]);
    if (!devices || devices.length === 0) return { error: "No device found" };
    
    let dev = devices[0];
    
    // Instead of full dev, let's try passing the object:
    let compInput = {
        libraryUuid: dev.uuid, // actually maybe dev.libraryUuid or something?
        uuid: dev.uuid
    };
    
    let comp = await eda.pcb_PrimitiveComponent.create(dev, 1, 4000, 4000, 0);
    return { status: "Success", comp: !!comp };
} catch(e) {
    return { error: e.message, stack: e.stack };
}
"""
print(json.dumps(execute_js(JS), indent=2))
