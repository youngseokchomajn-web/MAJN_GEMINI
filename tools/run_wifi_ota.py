#!/usr/bin/env python3
"""
MAJN Bassinet - Passive Web Wi-Fi Wireless OTA Runner
Uploads firmware via HTTP POST /update to ESP32 without modifying Mac Wi-Fi configuration.
Complies with AGENTS.md rules: Zero network hijacking, absolute path support.
"""

import sys
import os
import time
import urllib.request
import urllib.error

DEFAULT_FIRMWARE_BIN = "/tmp/fw.bin"
FALLBACK_FIRMWARE_BIN = "/Users/youngseok/Desktop/majn/인증준비/firmware/majn_wifi_phone_firmware.bin"
DEFAULT_URL = "http://192.168.4.1/update"
OTA_TOKEN = "majn2026-ota-token"

def check_target_reachable(url=DEFAULT_URL, timeout=2.0):
    host = url.split("//", 1)[-1].split("/", 1)[0]
    ping_url = f"http://{host}/api/ping"
    try:
        req = urllib.request.Request(ping_url, method="GET")
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            if resp.status == 200:
                return True
    except Exception:
        pass
    return False

def upload_firmware(bin_path, url=DEFAULT_URL, token=OTA_TOKEN):
    resolved_path = os.path.abspath(bin_path)
    if not os.path.exists(resolved_path):
        print(f"[Wi-Fi OTA] Error: Firmware file not found: {resolved_path}")
        return False

    with open(resolved_path, "rb") as f:
        file_bytes = f.read()

    total_bytes = len(file_bytes)
    if total_bytes == 0:
        print("[Wi-Fi OTA] Error: Binary file is empty.")
        return False

    if file_bytes[0] != 0xE9:
        print(f"[Wi-Fi OTA] Error: First byte 0x{file_bytes[0]:02X} != 0xE9. Invalid ESP32 flash image!")
        return False

    print(f"[Wi-Fi OTA] Target URL: {url}")
    print(f"[Wi-Fi OTA] Firmware: {resolved_path} ({total_bytes:,} bytes, {total_bytes / 1024:.1f} KB)")

    # 1. Reachability Check
    if not check_target_reachable(url):
        print("[Wi-Fi OTA] Error: Target http://192.168.4.1 is not reachable.")
        print("[Wi-Fi OTA] Please ensure your Mac is connected to 'MAJN-Bassinet' Wi-Fi network before running.")
        return False

    # 2. Construct Multipart Body with Token
    boundary = "----WebKitFormBoundaryMAJNOTA2026"
    
    body = (
        f"--{boundary}\r\n"
        f'Content-Disposition: form-data; name="token"\r\n\r\n'
        f"{token}\r\n"
        f"--{boundary}\r\n"
        f'Content-Disposition: form-data; name="update"; filename="firmware.bin"\r\n'
        f"Content-Type: application/octet-stream\r\n\r\n"
    ).encode("utf-8") + file_bytes + f"\r\n--{boundary}--\r\n".encode("utf-8")

    req = urllib.request.Request(
        url,
        data=body,
        headers={
            "Content-Type": f"multipart/form-data; boundary={boundary}",
            "Content-Length": str(len(body)),
            "Connection": "close"
        },
        method="POST"
    )

    print(f"[Wi-Fi OTA] Commencing HTTP upload ({len(body):,} bytes stream)...")
    start_time = time.time()
    try:
        with urllib.request.urlopen(req, timeout=45) as response:
            resp_text = response.read().decode("utf-8", errors="replace")
            elapsed = time.time() - start_time
            print(f"[Wi-Fi OTA] Completed in {elapsed:.1f}s ({total_bytes / elapsed / 1024:.1f} KB/s)")
            print(f"[Wi-Fi OTA] Server Response [{response.status}]: {resp_text.strip()}")
            if "SUCCESS" in resp_text:
                print("🎉 [Wi-Fi OTA] Transfer & Flash verification PASSED! ESP32 is rebooting.")
                return True
            else:
                print(f"[Wi-Fi OTA] Server indicated failure: {resp_text}")
                return False
    except urllib.error.HTTPError as e:
        err_msg = e.read().decode("utf-8", errors="replace")
        print(f"[Wi-Fi OTA] HTTP Error {e.code}: {err_msg}")
        return False
    except Exception as e:
        print(f"[Wi-Fi OTA] Network/Transfer Error: {e}")
        return False

def main():
    if len(sys.argv) > 1:
        bin_path = sys.argv[1]
    elif os.path.exists(DEFAULT_FIRMWARE_BIN):
        bin_path = DEFAULT_FIRMWARE_BIN
    else:
        bin_path = FALLBACK_FIRMWARE_BIN

    url = sys.argv[2] if len(sys.argv) > 2 else DEFAULT_URL
    success = upload_firmware(bin_path, url)
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
