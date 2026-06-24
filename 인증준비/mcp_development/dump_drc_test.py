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
    let drcArray = await eda.pcb_Drc.getDrcErrorArray();
    if (!drcArray) return { count: 0, details: [] };
    
    let errs = [];
    let count = 0;
    for (let group of drcArray) {
        if (group.list) {
            for (let err of group.list) {
                count++;
                let obj1Str = err.obj1 ? (err.obj1.typeName + " " + err.obj1.suffix) : "Unknown";
                let obj2Str = err.obj2 ? (err.obj2.typeName + " " + err.obj2.suffix) : "None";
                errs.push(`[${err.errorType}] ${err.ruleName} - ${obj1Str} <-> ${obj2Str}`);
            }
        }
    }
    return { count: count, details: errs };
} catch(e) { return { error: e.message }; }
"""
res = execute_js(JS)
if "error" in res:
    print("Error:", res["error"])
else:
    with open("drc_test_board.txt", "w") as f:
        f.write(f"Count: {res['count']}\\n")
        f.write("\\n".join(res['details']))
    print(f"Dumped {res['count']} errors to drc_test_board.txt")
