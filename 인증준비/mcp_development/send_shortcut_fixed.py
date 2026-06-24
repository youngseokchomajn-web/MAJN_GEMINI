import os
import sys
import time

def send_shortcut(key, use_shift=False, use_cmd=False):
    modifiers = []
    if use_shift: modifiers.append("shift down")
    if use_cmd: modifiers.append("command down")
    
    mod_str = ""
    if modifiers:
        mod_str = f" using {{{', '.join(modifiers)}}}"

    applescript = f"""
    tell application "EasyEDA-Pro" to activate
    delay 0.5
    tell application "System Events"
        keystroke "{key}"{mod_str}
    end tell
    """
    os.system(f"osascript -e '{applescript}'")

if __name__ == "__main__":
    print("Activating EasyEDA-Pro and sending Shift+B...")
    send_shortcut("B", use_shift=True)
    print("Done!")
