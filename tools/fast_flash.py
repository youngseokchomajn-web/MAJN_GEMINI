#!/usr/bin/env python3
"""
MAJN Fast Poller & Instant Flasher
"""
import subprocess
import time
import os
import sys

PORT = "/dev/cu.usbserial-0001"
PYTHON = os.path.expanduser("~/.platformio/penv/bin/python")
BUILD_DIR = "/Users/youngseok/Desktop/majn/인증준비/firmware/.pio/build/esp32_wifi_phone"
BOOTLOADER = os.path.join(BUILD_DIR, "bootloader.bin")
PARTITIONS = os.path.join(BUILD_DIR, "partitions.bin")
BOOT_APP0 = "/Users/youngseok/.platformio/packages/framework-arduinoespressif32/tools/partitions/boot_app0.bin"
FIRMWARE = os.path.join(BUILD_DIR, "firmware.bin")

print("=" * 64)
print("🚀 MAJN 자동 플래셔 대기 중")
print("👉 3번(IO0)과 6번(GND)을 2~3초간 '꾹' 대고 계셔주세요!")
print("=" * 64)

flash_cmd = [
    PYTHON, "-m", "esptool",
    "--port", PORT,
    "--baud", "921600",
    "--before", "no-reset",
    "--after", "no-reset",
    "write-flash", "-z",
    "--flash-mode", "dio",
    "--flash-freq", "40m",
    "--flash-size", "8MB",
    "0x1000", BOOTLOADER,
    "0x8000", PARTITIONS,
    "0xe000", BOOT_APP0,
    "0x10000", FIRMWARE
]

reboot_cmd = [
    PYTHON, "-m", "esptool",
    "--port", PORT,
    "--baud", "115200",
    "--before", "no-reset",
    "--after", "no-reset",
    "--no-stub",
    "write-mem", "0x3FF48000", "0x80000000", "0x80000000"
]

count = 0
while True:
    count += 1
    # Check if chip enters bootloader
    res = subprocess.run(
        [PYTHON, "-m", "esptool", "--port", PORT, "--baud", "115200", "--before", "no-reset", "--connect-attempts", "1", "chip-id"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    if res.returncode == 0:
        print("\n\n🎉 [부트로더 진입 감지 성공!] 손을 떼셔도 됩니다! (플래시 진행 중...)")
        flash_res = subprocess.run(flash_cmd)
        if flash_res.returncode == 0:
            print("\n⚡ [자동 소프트웨어 리셋 실행] 0x3FF48000 레지스터 리셋...")
            time.sleep(0.3)
            subprocess.run(reboot_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            print("\n" + "=" * 64)
            print("🎉 [플래시 및 자동 재부팅 100% 완료!]")
            print("=" * 64)
            break
        else:
            print("⚠️ 플래시 에러 발생, 재시도...")
    print(f"\r[감시 중 #{count}] 3번(IO0)+6번(GND) 2~3초간 접촉 대기 중...", end="", flush=True)
    time.sleep(0.15)
