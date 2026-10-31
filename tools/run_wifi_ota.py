#!/usr/bin/env python3
"""
MAJN Bassinet - Automated Web Wi-Fi Wireless OTA Runner
Connects en1 temporarily to 'MAJN-Bassinet', uploads firmware via HTTP POST /update,
and automatically restores Mac connection to original Wi-Fi (U+Net0FAC_5G).
"""

import sys
import os
import time
import subprocess
import urllib.request
import urllib.error

FIRMWARE_BIN = "인증준비/firmware/majn_wifi_phone_firmware.bin"
TARGET_SSID = "MAJN-Bassinet"
ORIGINAL_SSID = "U+Net0FAC_5G"
URL = "http://192.168.4.1/update"

def get_current_wifi():
    try:
        out = subprocess.check_output(["networksetup", "-getairportnetwork", "en1"]).decode()
        for line in out.splitlines():
            if "Current Wi-Fi Network:" in line:
                return line.split(":", 1)[1].strip()
    except Exception:
        pass
    return None

def restore_wifi(ssid=ORIGINAL_SSID):
    print(f"[Wi-Fi OTA] Reconnecting Mac to original Wi-Fi '{ssid}'...")
    subprocess.run(["networksetup", "-setairportnetwork", "en1", ssid], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    time.sleep(2)
    print(f"[Wi-Fi OTA] Restored Wi-Fi to {ssid}!")

def connect_target_wifi():
    print(f"[Wi-Fi OTA] Temporarily associating en1 to '{TARGET_SSID}'...")
    res = subprocess.run(["networksetup", "-setairportnetwork", "en1", TARGET_SSID], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if res.returncode == 0 and "Could not find" not in res.stdout:
        print(f"[Wi-Fi OTA] Connected to {TARGET_SSID}!")
        time.sleep(2)
        return True
    return False

def upload_firmware(bin_path):
    if not os.path.exists(bin_path):
        print(f"[Wi-Fi OTA] Error: Firmware not found: {bin_path}")
        return False

    with open(bin_path, "rb") as f:
        file_bytes = f.read()

    print(f"[Wi-Fi OTA] Uploading {bin_path} ({len(file_bytes):,} bytes) to {URL}...")
    boundary = "----WebKitFormBoundaryMAJNOTA2026"
    
    body = (
        f"--{boundary}\r\n"
        f'Content-Disposition: form-data; name="update"; filename="firmware.bin"\r\n'
        f"Content-Type: application/octet-stream\r\n\r\n"
    ).encode("utf-8") + file_bytes + f"\r\n--{boundary}--\r\n".encode("utf-8")

    req = urllib.request.Request(
        URL,
        data=body,
        headers={
            "Content-Type": f"multipart/form-data; boundary={boundary}",
            "Content-Length": str(len(body)),
            "Connection": "close"
        },
        method="POST"
    )

    try:
        with urllib.request.urlopen(req, timeout=30) as response:
            resp_text = response.read().decode("utf-8", errors="replace")
            print(f"[Wi-Fi OTA] Response: {resp_text}")
            if "SUCCESS" in resp_text:
                print("🎉 [Wi-Fi OTA] 100% Transfer Success! ESP32 is rebooting with Dual BLE+WiFi firmware.")
                return True
    except Exception as e:
        print(f"[Wi-Fi OTA] Upload error: {e}")
        return False

def main():
    bin_path = sys.argv[1] if len(sys.argv) > 1 else FIRMWARE_BIN
    prev_wifi = get_current_wifi() or ORIGINAL_SSID

    try:
        # 1. Connect to MAJN-Bassinet
        connected = False
        for attempt in range(3):
            if connect_target_wifi():
                connected = True
                break
            time.sleep(1)

        if not connected:
            print("[Wi-Fi OTA] Failed to connect to MAJN-Bassinet.")
            return

        # 2. Upload
        print("[Wi-Fi OTA] Waiting for IP lease...")
        time.sleep(2)
        upload_firmware(bin_path)

    finally:
        # 3. Always restore original Wi-Fi
        restore_wifi(prev_wifi)

if __name__ == "__main__":
    main()
