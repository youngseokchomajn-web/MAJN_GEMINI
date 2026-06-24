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

print("0. 캔버스의 모든 라우팅 초기화 (Unroute All) ...")
execute_js("return eda.sys_Command.execute('pcb_route_unrouteAll');")
time.sleep(2)

print("1. EasyEDA Pro 창 포커스 및 오토라우터 메뉴 호출...")
# AppleScript로 오토라우터 단축키 또는 메뉴를 직접 누를 수 없으므로, API로 창을 엽니다.
JS_OPEN = "return eda.sys_Command.execute('pcb_route_autoRoute');"
execute_js(JS_OPEN)

time.sleep(2)

print("2. AppleScript로 EasyEDA-Pro 창을 강제 활성화하고 Enter(실행) 키 입력...")
applescript_enter = """
tell application "EasyEDA-Pro"
    activate
    delay 1
    tell application "System Events"
        keystroke return
    end tell
end tell
"""
os.system(f"osascript -e '{applescript_enter}'")

print("3. 오토라우터 완료 대기 (20초)...")
time.sleep(20)

print("4. AppleScript로 Shift+B (구리 통판 갱신) 전송...")
applescript_shift_b = """
tell application "EasyEDA-Pro"
    activate
    delay 1
    tell application "System Events"
        keystroke "B" using shift down
    end tell
end tell
"""
os.system(f"osascript -e '{applescript_shift_b}'")

print("5. DRC 재검사 대기 (5초)...")
time.sleep(5)

print("6. API로 DRC 에러 개수 확인...")
JS_DRC = "return await eda.pcb_Drc.check(true, false, true);"
res = execute_js(JS_DRC)
total = 0
if isinstance(res, list):
    for cat in res:
        for item in cat.get('list', []):
            total += item.get('count', 0)

print(f"Total DRC Errors after full automation: {total}")
