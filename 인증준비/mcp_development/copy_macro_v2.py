import subprocess
import time
import json, urllib.request

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

def run(cmd):
    subprocess.run(cmd, shell=True)

print("Activating EasyEDA-Pro...")
run("osascript -e 'tell application \"EasyEDA-Pro\" to activate'")
time.sleep(1)

print("Selecting all via API...")
execute_js("eda.sys_Command.execute('pcb_select_all');")
time.sleep(0.5)

print("Executing copy via API...")
execute_js("eda.sys_Command.execute('sys_copy');")
time.sleep(1)

print("Clicking reference point at center...")
# Move to 800, 500, wait, and click
run("cliclick m:800,500 w:500 c:800,500")
time.sleep(1)

print("Checking clipboard...")
res = subprocess.run("pbpaste | head -c 100", shell=True, capture_output=True, text=True)
print("Clipboard starts with:", res.stdout)
