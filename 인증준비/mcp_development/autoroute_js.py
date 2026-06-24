import json
import urllib.request
def execute_js(code):
    url = "http://127.0.0.1:49620/execute"
    payload = json.dumps({"code": code}).encode("utf-8")
    req = urllib.request.Request(url, data=payload, headers={"Content-Type": "application/json"}, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=45) as response:
            res = json.loads(response.read().decode("utf-8"))
            if res.get("success"): return res.get("result")
            return {"error": res.get("error")}
    except Exception as e:
        return {"error": str(e)}

JS = """
try {
    // Open Dialog
    eda.sys_Command.execute('pcb_route_autoRoute');
    
    // Wait a bit, then click the primary button
    setTimeout(() => {
        let btns = document.querySelectorAll('.el-button--primary, .dialog-btn-confirm, button');
        for (let b of btns) {
            let text = b.innerText ? b.innerText.toLowerCase() : '';
            if (text.includes('run') || text.includes('start') || text.includes('실행') || text.includes('확인')) {
                b.click();
                break;
            }
        }
    }, 1000);
    return "Dialog opened and click scheduled";
} catch(e) { return e.message; }
"""
print(execute_js(JS))
