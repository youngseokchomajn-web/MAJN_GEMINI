#!/usr/bin/env python3
"""
Continuous Serial Logger for ESP32 Boot
"""
import serial
import time
import sys

PORT = "/dev/cu.usbserial-0001"
LOG_FILE = "/tmp/esp32_live_boot.log"

print(f"Monitoring {PORT} at 115200 baud... Waiting for EN toggle.")
with open(LOG_FILE, "w", encoding="utf-8") as f:
    f.write("=== Serial Monitor Started ===\n")

try:
    with serial.Serial(PORT, 115200, timeout=0.1) as ser:
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
    print(f"Error: {e}")
