import time
import os
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

print("1. Opening Auto Router Dialog via API...")
JS_OPEN = "return eda.sys_Command.execute('pcb_route_autoRoute');"
res = execute_js(JS_OPEN)
print("Dialog result:", res)

time.sleep(2)

print("2. Simulating 'Enter' to press Run...")
os.system("osascript -e 'tell application \"System Events\" to keystroke return'")

print("3. Waiting 15 seconds for Auto Router to finish...")
time.sleep(15)

print("4. Simulating 'Shift+B' to Rebuild Copper Pour...")
os.system("osascript -e 'tell application \"System Events\" to keystroke \"B\" using shift down'")

print("5. Opening Check DRC Dialog via API...")
JS_DRC = "return eda.sys_Command.execute('pcb_drc_checkAll');"
res_drc = execute_js(JS_DRC)
if res_drc and "error" in res_drc and "not a function" in res_drc["error"]:
    # Fallback to menu command if known
    JS_DRC = "return eda.sys_Command.execute('menu_pcb_drcCheck');"
    execute_js(JS_DRC)
    
time.sleep(2)
print("6. Simulating 'Enter' to run DRC Check (if dialog appears)...")
os.system("osascript -e 'tell application \"System Events\" to keystroke return'")

print("Done. Flow triggered.")
