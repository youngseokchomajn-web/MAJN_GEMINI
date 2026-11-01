#!/usr/bin/env python3
"""
Continuous Serial Logger for ESP32 Boot
"""
import serial
import time
import sys

import glob
import os

LOG_FILE = "/tmp/esp32_live_boot.log"

# Allow CLI argument or auto-detect usbserial port
port = sys.argv[1] if len(sys.argv) > 1 else None
if not port:
    detected = glob.glob("/dev/cu.usbserial*")
    port = detected[0] if detected else "/dev/cu.usbserial-0001"

print(f"Monitoring {port} at 115200 baud... Waiting for ESP32 boot (power cycle 5V USB-C; note: PCB #0005 has NO physical EN/BOOT buttons).")
with open(LOG_FILE, "w", encoding="utf-8") as f:
    f.write(f"=== Serial Monitor Started on {port} ===\n")

try:
    with serial.Serial(port, 115200, timeout=0.1) as ser:
        ser.reset_input_buffer()
        while True:
            data = ser.read(ser.in_waiting or 1)
            if data:
                text = data.decode("utf-8", errors="replace")
                print(text, end="", flush=True)
                with open(LOG_FILE, "a", encoding="utf-8") as f:
                    f.write(text)
            else:
                time.sleep(0.01)
except Exception as e:
    print(f"Error connecting to {port}: {e}")

