import asyncio
import json
import sys
import os
from bleak import BleakScanner, BleakClient

OTA_SERVICE_UUID = "00000004-6a6e-4d41-4a4e-000000000001"
OTA_CONTROL_UUID = "00000005-6a6e-4d41-4a4e-000000000001"
OTA_DATA_UUID    = "00000006-6a6e-4d41-4a4e-000000000001"

CHUNK_SIZE = 512

async def main():
    fw_path = os.path.expanduser("~/Desktop/majn_latest_firmware.bin")
    if not os.path.exists(fw_path):
        print(f"Error: Firmware file not found at {fw_path}")
        return

    fw_size = os.path.getsize(fw_path)
    print(f"Loaded firmware: {fw_path} ({fw_size} bytes)")

    print("Scanning for MAJN-Bassinet...")
    device = None
    devices = await BleakScanner.discover(timeout=5.0)
    for d in devices:
        if d.name and "MAJN" in d.name:
            device = d
            break

    if not device:
        print("Error: Could not find MAJN-Bassinet device via BLE. Ensure board is powered on!")
        return

    print(f"Found device: {device.name} ({device.address}). Connecting...")
    async with BleakClient(device) as client:
        print(f"Connected! MTU: {client.mtu_size}")

        ota_status_events = []
        def on_ota_status(sender, data):
            msg = data.decode("utf-8", errors="ignore")
            print(f"[ESP32 OTA NOTIFY] {msg}")
            ota_status_events.append(msg)

        await client.start_notify(OTA_CONTROL_UUID, on_ota_status)
        await asyncio.sleep(0.5)

        # 1. Send OTA_BEGIN
        begin_payload = json.dumps({"cmd": "OTA_BEGIN", "size": fw_size}).encode("utf-8")
        print(f"Sending OTA_BEGIN (size: {fw_size})...")
        await client.write_gatt_char(OTA_CONTROL_UUID, begin_payload, response=True)
        await asyncio.sleep(1.0)

        # 2. Stream binary chunks with ACK (response=True) to prevent dropped packets
        print("Streaming firmware binary with ACK verification...")
        with open(fw_path, "rb") as f:
            data = f.read()

        total = len(data)
        offset = 0
        last_pct = 0
        # Optimal chunk size fitting in MTU 515 (512 bytes payload)
        chunk_size = min(CHUNK_SIZE, client.mtu_size - 3) if client.mtu_size > 23 else 244
        print(f"Transfer chunk size: {chunk_size} bytes")

        while offset < total:
            chunk = data[offset:offset + chunk_size]
            # Write chunk with ACK verification
            await client.write_gatt_char(OTA_DATA_UUID, chunk, response=True)
            offset += len(chunk)
            pct = int((offset / total) * 100)
            if pct != last_pct and pct % 10 == 0:
                print(f"[OTA Host Sent] {pct}% ({offset}/{total} bytes)")
                last_pct = pct

        print("[OTA Host] 100% transfer complete!")
        await asyncio.sleep(1.0)

        # 3. Send OTA_END
        end_payload = json.dumps({"cmd": "OTA_END"}).encode("utf-8")
        print("Sending OTA_END for verification & reboot...")
        try:
            await client.write_gatt_char(OTA_CONTROL_UUID, end_payload, response=True)
        except Exception as e:
            print(f"Notice: GATT write during reboot ({e})")

        print("Waiting 5s for reboot confirmation...")
        await asyncio.sleep(5.0)
        print(f"Total OTA status events received: {ota_status_events}")

if __name__ == "__main__":
    asyncio.run(main())
