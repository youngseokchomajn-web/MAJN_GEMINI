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
    let result = [];
    let allDivs = document.querySelectorAll('div, span, button, a, li');
    for (let el of allDivs) {
        if (el.innerText && (el.innerText.includes('Auto Router') || el.innerText.includes('Auto Route'))) {
            result.push({
                tag: el.tagName,
                class: el.className,
                text: el.innerText
            });
        }
    }
    return result.slice(0, 5);
} catch(e) { return e.message; }
"""
print(json.dumps(execute_js(JS), indent=2))
