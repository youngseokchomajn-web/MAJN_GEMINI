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
    // Find any DOM element that contains 'DRC' or 'Errors' or numbers
    let treeNodes = document.querySelectorAll('.tree-node, .drc-item, .drc-error, [class*="drc"]');
    let texts = [];
    for (let node of treeNodes) {
        if (node.innerText && node.innerText.includes('Error')) {
            texts.push(node.innerText.trim());
        }
    }
    // Try a broad search if nothing found
    if (texts.length === 0) {
        let allDivs = document.querySelectorAll('div');
        for (let div of allDivs) {
            if (div.innerText && div.innerText.includes('Clearance Error')) {
                texts.push(div.innerText.substring(0, 100)); // Just grab a snippet
                break;
            }
        }
    }
    return texts.length > 0 ? texts : "No DRC panel found in DOM";
} catch(e) { return e.message; }
"""
print(execute_js(JS))
