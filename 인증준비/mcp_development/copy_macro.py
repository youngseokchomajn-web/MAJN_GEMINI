import subprocess
import time

def run(cmd):
    subprocess.run(cmd, shell=True)

print("Activating EasyEDA-Pro...")
run("osascript -e 'tell application \"EasyEDA-Pro\" to activate'")
time.sleep(1)

print("Selecting all...")
run("osascript -e 'tell application \"System Events\" to keystroke \"a\" using command down'")
time.sleep(1)

print("Copying...")
run("osascript -e 'tell application \"System Events\" to keystroke \"c\" using command down'")
time.sleep(1)

print("Clicking reference point at center...")
# EasyEDA Pro waits for a mouse click to set the copy reference point
run("cliclick c:800,500")
time.sleep(1)

print("Checking clipboard...")
res = subprocess.run("pbpaste | head -c 100", shell=True, capture_output=True, text=True)
print("Clipboard starts with:", res.stdout)
