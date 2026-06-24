import json, urllib.request
try:
    req = urllib.request.Request("http://127.0.0.1:49620/execute", data=json.dumps({"code": "return 'pong';"}).encode("utf-8"), headers={"Content-Type": "application/json"}, method="POST")
    res = urllib.request.urlopen(req).read().decode("utf-8")
    print(res)
except Exception as e:
    print(e)
