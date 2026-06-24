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
    let projs = await eda.dmt_Project.getAllProjectsInfo();
    for (let p of projs) {
        let boards = await eda.dmt_Board.getAllBoardsInfoByProjectUuid(p.uuid);
        if (boards) {
            for (let b of boards) {
                let pcbs = await eda.dmt_Pcb.getAllPcbsInfoByBoardUuid(b.uuid);
                if (pcbs) {
                    for (let pcb of pcbs) {
                        try {
                            // We can't query getAll components without activating the PCB first!
                            // So we just return all PCB uuids
                            result.push({ proj: p.name, board: b.name, pcb: pcb.name, uuid: pcb.uuid });
                        } catch(e) {}
                    }
                }
            }
        }
    }
    return { all_pcbs: result };
} catch(e) { return { error: e.message }; }
"""
print(json.dumps(execute_js(JS), indent=2))
