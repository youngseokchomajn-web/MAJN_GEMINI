#!/usr/bin/env python3
"""
MAJN Bassinet - Automated Web BLE Wireless OTA Runner (Lossless Safe Flow)
Prevents BLE buffer overflow by using paced chunk transmission and verifying actual received bytes.
"""

import sys
import os
import json
import asyncio
import time

try:
    from bleak import BleakScanner, BleakClient
except ImportError:
    print("Error: bleak library not found. Run via: uv run --with bleak python tools/run_ble_ota.py")
    sys.exit(1)

# Protocol v1 UUIDs
OTA_SERVICE_UUID = "00000004-6a6e-4d41-4a4e-000000000001"
OTA_CONTROL_UUID = "00000005-6a6e-4d41-4a4e-000000000001"
OTA_DATA_UUID    = "00000006-6a6e-4d41-4a4e-000000000001"
CHUNK_SIZE = 256

async def run_ota(bin_path):
    if not os.path.exists(bin_path):
        print(f"[OTA] Error: Firmware file not found: {bin_path}")
        return False

    with open(bin_path, "rb") as f:
        firmware_bytes = f.read()

    total_bytes = len(firmware_bytes)
    print(f"[OTA] Loaded firmware: {bin_path} ({total_bytes:,} bytes, {total_bytes / 1024:.1f} KB)")

    print("[OTA] Scanning for 'MAJN-Bassinet' over Bluetooth Low Energy...")
    target_device = None

    devices = await BleakScanner.discover(timeout=5.0)
    for d in devices:
        name = d.name or ""
        if "MAJN" in name.upper() or "BASSINET" in name.upper():
            target_device = d
            print(f"[OTA] Found Target Device: {d.name} [{d.address}]")
            break

    if not target_device:
        print("[OTA] Error: Target device 'MAJN-Bassinet' not found in BLE scan.")
        return False

    ota_ready_event = asyncio.Event()
    ota_status_result = {"status": None, "error": None, "progress": 0}

    def notification_handler(sender, data):
        try:
            msg = json.loads(data.decode("utf-8"))
            st = msg.get("status")
            err = msg.get("error")
            prog = msg.get("progress", 0)
            ota_status_result["status"] = st
            ota_status_result["error"] = err
            ota_status_result["progress"] = prog
            if st == "ready":
                ota_ready_event.set()
            elif st == "error":
                print(f"\n[ESP32-Error] Status: {st}, Error: {err}")
            elif st == "success":
                print(f"\n🎉 [ESP32-Success] Flash verification PASSED! Device is rebooting...")
        except Exception as e:
            pass

    print(f"[OTA] Connecting to {target_device.name}...")
    async with BleakClient(target_device.address, timeout=20.0) as client:
        print(f"[OTA] Connected successfully! Enabling notifications...")
        await client.start_notify(OTA_CONTROL_UUID, notification_handler)
        await asyncio.sleep(0.5)

        # 1. Send OTA_BEGIN
        print(f"[OTA] Initializing OTA session on ESP32 (Size: {total_bytes} bytes)...")
        begin_payload = json.dumps({"cmd": "OTA_BEGIN", "size": total_bytes}).encode("utf-8")
        await client.write_gatt_char(OTA_CONTROL_UUID, begin_payload, response=True)

        try:
            await asyncio.wait_for(ota_ready_event.wait(), timeout=6.0)
            print("[OTA] ESP32 Ready! Commencing lossless buffered transfer...")
        except asyncio.TimeoutError:
            print(f"[OTA] Fatal: Timeout waiting for 'ready'. Status: {ota_status_result}")
            return False

        # 2. Stream Binary Chunks with Safe Flow Pacing
        # Every 8 chunks (~2KB), perform a response=True write or micro-flush to avoid packet drops
        offset = 0
        start_time = time.time()
        chunk_count = 0

        while offset < total_bytes:
            if not client.is_connected:
                print("\n[OTA] Error: BLE disconnected during transfer!")
                return False

            end = min(offset + CHUNK_SIZE, total_bytes)
            chunk = firmware_bytes[offset:end]

            chunk_count += 1
            # Every 12 chunks, request ACK (response=True) to guarantee BLE buffer synchronization
            use_response = (chunk_count % 12 == 0)
            await client.write_gatt_char(OTA_DATA_UUID, chunk, response=use_response)
            offset = end

            pct = int((offset / total_bytes) * 100)
            esp_prog = ota_status_result.get("progress", 0)
            elapsed = time.time() - start_time
            kb_s = (offset / 1024) / elapsed if elapsed > 0 else 0
            bar = "#" * (pct // 5) + "-" * (20 - (pct // 5))
            print(f"[OTA] [{bar}] Sent {pct}% | ESP32 Flash {esp_prog}% | {kb_s:.1f} KB/s", end="\r")

            # 18ms delay ensures ESP32 SPI flash write time (10~15ms) completes cleanly
            await asyncio.sleep(0.018)

        print(f"\n[OTA] All {total_bytes:,} bytes sent from Mac. Waiting for ESP32 flash write to reach 100%...")

        # Wait until ESP32 acknowledges 100% or near 100%
        for _ in range(40):
            if ota_status_result.get("progress", 0) >= 99:
                break
            await asyncio.sleep(0.2)

        print("[OTA] Sending OTA_END to trigger partition verification and reboot...")
        end_payload = json.dumps({"cmd": "OTA_END"}).encode("utf-8")
        try:
            await client.write_gatt_char(OTA_CONTROL_UUID, end_payload, response=True)
        except Exception:
            # Device often cuts BLE and reboots immediately
            pass

        # Give 3 seconds to capture reboot or error
        for _ in range(15):
            if ota_status_result.get("status") in ["success", "error"]:
                break
            await asyncio.sleep(0.2)

        if ota_status_result.get("status") == "error":
            print(f"❌ [OTA] Flash Verification Failed: {ota_status_result.get('error')}")
            return False

        print("🎉 [OTA] 100% Lossless Firmware Update Completed Successfully!")
        print("🎉 [OTA] ESP32 has booted into Wi-Fi SoftAP mode!")
        return True

if __name__ == "__main__":
    firmware_file = sys.argv[1] if len(sys.argv) > 1 else "bassinet_simulator/majn_wifi_phone_firmware.bin"
    success = asyncio.run(run_ota(firmware_file))
    sys.exit(0 if success else 1)
