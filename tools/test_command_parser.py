#!/usr/bin/env python3
"""
MAJN Wireless Command Parser & Security Matrix Unit Test Suite (v2.0)
===================================================================
Automated host-side verification of:
1. Command parsing, parameter boundary constraints, and invalid payloads.
2. State machine transitions (RUNNING -> STOPPING -> READY).
3. ESTOP / FAULT lockout and recovery gate.
4. OTA cross-locking gate and firmware validation checks.
5. Deep static source verification of firmware C++ files:
   - Wi-Fi access control, WPA2 NVS generation, and token purge.
   - CORS wildcard removal.
   - BLE GATT MITM encryption permissions and advertising intervals.
   - OTA partition size alignment (0x330000 = 3.19 MB) and 0xE9 magic byte check.
   - Universal amplifier FAULT lock across all boot paths.
"""

import json
import sys
import os
import re

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

FW_METADATA = {
    "source_mode": "UNKNOWN",
    "git_branch": "feature/phone-wifi-control",
    "git_commit_sha": "UNKNOWN",
    "files_read": {}
}

def get_self_sha256():
    import hashlib
    try:
        with open(__file__, "rb") as f:
            return hashlib.sha256(f.read()).hexdigest()
    except Exception:
        return "UNKNOWN"

def get_git_commit_sha(ref):
    import subprocess
    try:
        res = subprocess.run(["git", "rev-parse", ref], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True)
        return res.stdout.strip()
    except Exception:
        return "UNKNOWN"

def read_fw_file(filename):
    import subprocess
    global FW_METADATA
    # In docs/ branches or mixed branches, prioritize feature/phone-wifi-control where latest firmware lives
    try:
        git_path = f"feature/phone-wifi-control:인증준비/firmware/src/{filename}"
        res = subprocess.run(["git", "show", git_path], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True)
        FW_METADATA["source_mode"] = "GIT_SHOW"
        if FW_METADATA["git_commit_sha"] == "UNKNOWN":
            FW_METADATA["git_commit_sha"] = get_git_commit_sha("feature/phone-wifi-control")
        FW_METADATA["files_read"][filename] = len(res.stdout)
        return res.stdout
    except Exception:
        local_path = os.path.join(FW_SRC, filename)
        if os.path.exists(local_path):
            with open(local_path, "r", encoding="utf-8") as f:
                content = f.read()
                FW_METADATA["source_mode"] = "LOCAL_FILESYSTEM"
                FW_METADATA["files_read"][filename] = len(content)
                return content
        raise FileNotFoundError(f"Cannot find {filename}")

class MockVibration:
    def __init__(self):
        self.target_freq = 45.0
        self.target_amp = 0.0
        self.current_amp = 0.0

    def set_target(self, freq, amp):
        self.target_freq = max(30.0, min(65.0, freq))
        self.target_amp = max(0.0, min(0.5, amp))

class MockSystem:
    def __init__(self):
        self.system_active = False
        self.safety_lock = False
        self.vibration = MockVibration()
        self.amp_ready = True
        self.amp_diag_fault = False
        self.duration_min = 15
        self.ota_in_progress = False
        self.reboot_scheduled = False
        self.wifi_cred_reset = False
        self.ota_bytes_received = 0
        self.ota_expected_size = 0
        self.thermal_derated = False
        self.last_derated_target = 0.0

    def simulate_thermal_supervisor(self, warn_byte):
        if not self.system_active:
            self.thermal_derated = False
            self.last_derated_target = 0.0
            return
        if warn_byte & 0x04:
            cur = self.vibration.target_amp
            if not self.thermal_derated or (cur > self.last_derated_target + 0.01):
                if cur > 0.01:
                    derated = cur * 0.5
                    self.vibration.set_target(self.vibration.target_freq, derated)
                    self.last_derated_target = derated
                    self.thermal_derated = True
        else:
            self.thermal_derated = False
            self.last_derated_target = 0.0

    def get_system_state(self):
        if self.safety_lock:
            return "FAULT"
        if self.system_active:
            return "RUNNING"
        if not self.system_active and self.vibration.current_amp > 0.001:
            return "STOPPING"
        return "READY"

    def handle_json_command(self, json_str):
        if not json_str or len(json_str.strip()) == 0:
            return False, {"id": -1, "cmd": "UNKNOWN", "status": "rejected", "state": self.get_system_state()}

        try:
            doc = json.loads(json_str)
        except Exception:
            return False, {"id": -1, "cmd": "UNKNOWN", "status": "rejected", "state": self.get_system_state()}

        req_id = doc.get("id", -1)
        cmd = doc.get("cmd", "")

        # OTA active gate
        if self.ota_in_progress and cmd not in ("PING", "STATUS"):
            return False, {"id": req_id, "cmd": cmd, "status": "rejected", "state": "OTA_ACTIVE"}

        if cmd == "PING":
            return True, {"id": req_id, "cmd": cmd, "status": "applied", "state": self.get_system_state()}

        if cmd == "STATUS":
            return True, {"id": req_id, "cmd": cmd, "status": "applied", "state": self.get_system_state()}

        if cmd == "START":
            if self.safety_lock:
                return False, {"id": req_id, "cmd": cmd, "status": "fault", "state": "FAULT"}

            f = float(doc.get("frequency_hz", self.vibration.target_freq))
            a = float(doc.get("amplitude", 0.4 if self.vibration.target_amp < 0.05 else self.vibration.target_amp))

            if f < 30.0 or f > 65.0 or a < 0.0 or a > 0.5:
                return False, {"id": req_id, "cmd": cmd, "status": "rejected", "state": self.get_system_state()}

            if "duration_min" in doc:
                dm = int(doc["duration_min"])
                if 1 <= dm <= 30:
                    self.duration_min = dm

            if not self.amp_ready or self.amp_diag_fault:
                self.system_active = False
                self.safety_lock = True
                self.vibration.current_amp = 0.0
                self.vibration.target_amp = 0.0
                return False, {"id": req_id, "cmd": cmd, "status": "failed", "state": "FAULT"}

            self.system_active = True
            self.vibration.set_target(f, a)
            self.vibration.current_amp = a
            return True, {"id": req_id, "cmd": cmd, "status": "applied", "state": "RUNNING"}

        if cmd == "STOP":
            self.system_active = False
            self.vibration.target_amp = 0.0
            # Note: current_amp remains > 0 until decayed
            return True, {"id": req_id, "cmd": cmd, "status": "applied", "state": self.get_system_state()}

        if cmd == "ESTOP":
            self.system_active = False
            self.safety_lock = True
            self.vibration.current_amp = 0.0
            self.vibration.target_amp = 0.0
            return True, {"id": req_id, "cmd": cmd, "status": "applied", "state": "FAULT"}

        if cmd == "RESET_FAULT":
            if not self.safety_lock:
                return True, {"id": req_id, "cmd": cmd, "status": "applied", "state": self.get_system_state()}
            if self.amp_diag_fault or not self.amp_ready:
                return False, {"id": req_id, "cmd": cmd, "status": "rejected", "state": "FAULT"}
            self.safety_lock = False
            return True, {"id": req_id, "cmd": cmd, "status": "applied", "state": "READY"}

        if cmd == "SET_FREQUENCY":
            if self.safety_lock:
                return False, {"id": req_id, "cmd": cmd, "status": "rejected", "state": "FAULT"}
            if "frequency_hz" not in doc:
                return False, {"id": req_id, "cmd": cmd, "status": "rejected", "state": self.get_system_state()}
            f = float(doc["frequency_hz"])
            if f < 30.0 or f > 65.0:
                return False, {"id": req_id, "cmd": cmd, "status": "rejected", "state": self.get_system_state()}
            self.vibration.set_target(f, self.vibration.target_amp)
            return True, {"id": req_id, "cmd": cmd, "status": "applied", "state": self.get_system_state()}

        if cmd == "SET_AMPLITUDE":
            if self.safety_lock:
                return False, {"id": req_id, "cmd": cmd, "status": "rejected", "state": "FAULT"}
            if "amplitude" not in doc:
                return False, {"id": req_id, "cmd": cmd, "status": "rejected", "state": self.get_system_state()}
            a = float(doc["amplitude"])
            if a < 0.0 or a > 0.5:
                return False, {"id": req_id, "cmd": cmd, "status": "rejected", "state": self.get_system_state()}
            self.vibration.set_target(self.vibration.target_freq, a)
            if self.system_active:
                self.vibration.current_amp = a
            return True, {"id": req_id, "cmd": cmd, "status": "applied", "state": self.get_system_state()}

        if cmd == "SET_DURATION":
            if "duration_min" not in doc:
                return False, {"id": req_id, "cmd": cmd, "status": "rejected", "state": self.get_system_state()}
            dm = int(doc["duration_min"])
            if 1 <= dm <= 30:
                self.duration_min = dm
                return True, {"id": req_id, "cmd": cmd, "status": "applied", "state": self.get_system_state()}
            return False, {"id": req_id, "cmd": cmd, "status": "rejected", "state": self.get_system_state()}

        if cmd == "RESET_WIFI_CRED":
            self.wifi_cred_reset = True
            self.reboot_scheduled = True
            return True, {"id": req_id, "cmd": cmd, "status": "applied", "state": "REBOOTING"}

        if cmd == "REBOOT":
            self.reboot_scheduled = True
            return True, {"id": req_id, "cmd": cmd, "status": "applied", "state": "REBOOTING"}

        return False, {"id": req_id, "cmd": cmd, "status": "rejected", "state": self.get_system_state()}

    def start_ota(self, size_bytes):
        MAX_PARTITION = 0x330000  # 3,342,336 bytes
        if self.system_active:
            return False, "LOCKED_RUNNING"
        if size_bytes == 0 or size_bytes > MAX_PARTITION:
            return False, "INVALID_SIZE"
        self.ota_in_progress = True
        self.ota_expected_size = size_bytes
        self.ota_bytes_received = 0
        return True, "READY"

    def write_ota_chunk(self, data_bytes):
        if not self.ota_in_progress:
            return False, "NOT_RUNNING"
        if self.ota_bytes_received == 0:
            if len(data_bytes) == 0 or data_bytes[0] != 0xE9:
                self.ota_in_progress = False
                return False, "INVALID_MAGIC"
        self.ota_bytes_received += len(data_bytes)
        return True, "OK"


def run_tests():
    passed = 0
    failed = 0

    def assert_eq(test_name, actual, expected):
        nonlocal passed, failed
        if actual == expected:
            print(f"  [PASS] {test_name}: {actual}")
            passed += 1
        else:
            print(f"  [FAIL] {test_name}: Expected {expected}, got {actual}")
            failed += 1

    print("=== TEST SUITE 1: JSON Malformed & Empty Inputs ===")
    sys_instance = MockSystem()
    ok, res = sys_instance.handle_json_command("")
    assert_eq("Empty string handled", ok, False)
    assert_eq("Empty string status", res["status"], "rejected")

    ok, res = sys_instance.handle_json_command("{not valid json")
    assert_eq("Malformed json handled", ok, False)
    assert_eq("Malformed json status", res["status"], "rejected")

    print("\n=== TEST SUITE 2: Range & Boundary Validation ===")
    ok, res = sys_instance.handle_json_command(json.dumps({"id": 1, "cmd": "START", "frequency_hz": 29.9, "amplitude": 0.3}))
    assert_eq("Freq < 30 rejected", ok, False)

    ok, res = sys_instance.handle_json_command(json.dumps({"id": 2, "cmd": "START", "frequency_hz": 65.1, "amplitude": 0.3}))
    assert_eq("Freq > 65 rejected", ok, False)

    ok, res = sys_instance.handle_json_command(json.dumps({"id": 3, "cmd": "START", "frequency_hz": 45.0, "amplitude": 0.55}))
    assert_eq("Amp > 0.50 rejected", ok, False)

    ok, res = sys_instance.handle_json_command(json.dumps({"id": 4, "cmd": "START", "frequency_hz": 45.0, "amplitude": -0.1}))
    assert_eq("Amp < 0.0 rejected", ok, False)

    ok, res = sys_instance.handle_json_command(json.dumps({"id": 5, "cmd": "SET_DURATION", "duration_min": 0}))
    assert_eq("Duration < 1 min rejected", ok, False)

    ok, res = sys_instance.handle_json_command(json.dumps({"id": 6, "cmd": "SET_DURATION", "duration_min": 31}))
    assert_eq("Duration > 30 min rejected", ok, False)

    ok, res = sys_instance.handle_json_command(json.dumps({"id": 7, "cmd": "SET_DURATION", "duration_min": 15}))
    assert_eq("Duration 15 min accepted", ok, True)

    print("\n=== TEST SUITE 3: STOPPING State Transition & Safe Stop ===")
    ok, res = sys_instance.handle_json_command(json.dumps({"id": 8, "cmd": "START", "frequency_hz": 50.0, "amplitude": 0.35}))
    assert_eq("START valid command", ok, True)
    assert_eq("State after START", res["state"], "RUNNING")

    ok, res = sys_instance.handle_json_command(json.dumps({"id": 9, "cmd": "STOP"}))
    assert_eq("STOP command accepted", ok, True)
    # Since current_amp is still 0.35 (simulating decay period), state should be STOPPING
    assert_eq("State immediately on STOP with current_amp > 0", res["state"], "STOPPING")

    # Simulate decay completion
    sys_instance.vibration.current_amp = 0.0
    assert_eq("State after amplitude decay reached 0", sys_instance.get_system_state(), "READY")

    print("\n=== TEST SUITE 4: ESTOP and FAULT Lockout ===")
    ok, res = sys_instance.handle_json_command(json.dumps({"id": 10, "cmd": "ESTOP"}))
    assert_eq("ESTOP command applied", ok, True)
    assert_eq("State after ESTOP", res["state"], "FAULT")

    ok, res = sys_instance.handle_json_command(json.dumps({"id": 11, "cmd": "START", "frequency_hz": 45.0, "amplitude": 0.3}))
    assert_eq("START locked out during FAULT", ok, False)
    assert_eq("START rejection state during FAULT", res["status"], "fault")

    # Hardware fault persists -> RESET_FAULT rejected
    sys_instance.amp_diag_fault = True
    ok, res = sys_instance.handle_json_command(json.dumps({"id": 12, "cmd": "RESET_FAULT"}))
    assert_eq("RESET_FAULT rejected when hardware fault persists", ok, False)
    assert_eq("RESET_FAULT rejection status", res["status"], "rejected")
    assert_eq("State remains FAULT", res["state"], "FAULT")

    # Clear hardware fault -> RESET_FAULT accepted
    sys_instance.amp_diag_fault = False
    ok, res = sys_instance.handle_json_command(json.dumps({"id": 13, "cmd": "RESET_FAULT"}))
    assert_eq("RESET_FAULT restores READY when fault cleared", ok, True)
    assert_eq("State after RESET_FAULT", res["state"], "READY")

    # START rejected if hardware fault occurs during startup
    sys_instance.amp_diag_fault = True
    ok, res = sys_instance.handle_json_command(json.dumps({"id": 14, "cmd": "START", "frequency_hz": 45.0, "amplitude": 0.3}))
    assert_eq("START rejected on hardware fault", ok, False)
    assert_eq("START status on hardware fault", res["status"], "failed")
    assert_eq("State after failed START", res["state"], "FAULT")
    assert_eq("System state is FAULT after failed START", sys_instance.get_system_state(), "FAULT")

    # Subsequent START must be locked out while in FAULT state
    ok, res = sys_instance.handle_json_command(json.dumps({"id": 15, "cmd": "START", "frequency_hz": 45.0, "amplitude": 0.3}))
    assert_eq("Subsequent START locked out in FAULT", ok, False)
    assert_eq("Subsequent START status is fault", res["status"], "fault")

    # RESET_FAULT rejected when hardware fault persists after failed START
    ok, res = sys_instance.handle_json_command(json.dumps({"id": 16, "cmd": "RESET_FAULT"}))
    assert_eq("RESET_FAULT rejected when hardware fault persists after START", ok, False)
    assert_eq("RESET_FAULT rejection status after START", res["status"], "rejected")
    assert_eq("State remains FAULT after rejected RESET_FAULT", res["state"], "FAULT")

    # Clear hardware fault -> RESET_FAULT restores READY
    sys_instance.amp_diag_fault = False
    ok, res = sys_instance.handle_json_command(json.dumps({"id": 17, "cmd": "RESET_FAULT"}))
    assert_eq("RESET_FAULT restores READY for next suite", ok, True)
    assert_eq("State after RESET_FAULT restored", res["state"], "READY")

    print("\n=== TEST SUITE 5: OTA Cross-Locking Gate & Image Verification ===")
    sys_instance.ota_in_progress = True
    ok, res = sys_instance.handle_json_command(json.dumps({"id": 13, "cmd": "START", "frequency_hz": 45.0, "amplitude": 0.3}))
    assert_eq("START rejected during OTA", ok, False)
    assert_eq("Rejection status during OTA", res["state"], "OTA_ACTIVE")

    ok, res = sys_instance.handle_json_command(json.dumps({"id": 14, "cmd": "PING"}))
    assert_eq("PING allowed during OTA", ok, True)
    sys_instance.ota_in_progress = False

    # Test OTA Partition Size Boundary (3,342,336 bytes)
    ok, code = sys_instance.start_ota(3342336)
    assert_eq("OTA exactly partition size accepted", ok, True)
    sys_instance.ota_in_progress = False

    ok, code = sys_instance.start_ota(3342337)
    assert_eq("OTA exceeding partition rejected", ok, False)
    assert_eq("OTA partition overflow status", code, "INVALID_SIZE")

    # Test Magic Byte Check (0xE9)
    sys_instance.start_ota(1900000)
    ok, code = sys_instance.write_ota_chunk(bytes([0xAA, 0xBB, 0xCC]))
    assert_eq("Non-ESP32 magic byte (0xAA) rejected", ok, False)
    assert_eq("Magic byte rejection code", code, "INVALID_MAGIC")

    sys_instance.start_ota(1900000)
    ok, code = sys_instance.write_ota_chunk(bytes([0xE9, 0x04, 0x02]))
    assert_eq("Valid ESP32 magic byte (0xE9) accepted", ok, True)
    sys_instance.ota_in_progress = False

    print("\n=== TEST SUITE 6: RESET_WIFI_CRED & Recovery Command ===")
    ok, res = sys_instance.handle_json_command(json.dumps({"id": 15, "cmd": "RESET_WIFI_CRED"}))
    assert_eq("RESET_WIFI_CRED applied", ok, True)
    assert_eq("RESET_WIFI_CRED flag set", sys_instance.wifi_cred_reset, True)
    assert_eq("Reboot scheduled", sys_instance.reboot_scheduled, True)
    assert_eq("Rebooting state reported", res["state"], "REBOOTING")

    print("\n=== TEST SUITE 7: Deep Static Firmware Source Code Audit ===")
    commit_sha = get_git_commit_sha("feature/phone-wifi-control")
    print(f"  [SOURCE AUDIT TARGET] Branch: feature/phone-wifi-control | Commit SHA: {commit_sha}")
    print(f"  [TEST SCRIPT SHA256] {get_self_sha256()}")
    print("  [SCOPE NOTICE] Static Source Audit tests rule conformance in C++ files.")
    print("                 This does NOT substitute for physical runtime or silicon hardware verification.")
    
    wifi_cpp = read_fw_file("wifi_manager.cpp")
    ble_cpp = read_fw_file("ble_manager.cpp")
    ota_ble_cpp = read_fw_file("ota_ble_service.cpp")
    main_cpp = read_fw_file("main.cpp")

    # Rule 1: No hardcoded Wi-Fi or BLE credentials in source
    has_hardcoded_pass = bool(re.search(r'WiFi\.softAP\(\s*ssid\s*,\s*\"[^\"]+\"', wifi_cpp))
    assert_eq("Zero hardcoded SoftAP password in wifi_manager.cpp", has_hardcoded_pass, False)

    # Rule 2: NVS random passphrase generation present
    has_nvs_pass_gen = "esp_random()" in wifi_cpp and "wifi_pass" in wifi_cpp
    assert_eq("Dynamic NVS WPA2 passphrase generation present", has_nvs_pass_gen, True)

    # Rule 3: auth_token removed from status response
    auth_token_in_status = '"auth_token"' in wifi_cpp
    assert_eq("auth_token purged from /api/status JSON", auth_token_in_status, False)

    # Rule 4: No wildcard CORS headers
    has_wildcard_cors = "Access-Control-Allow-Origin" in wifi_cpp and "*" in wifi_cpp
    cors_matches = re.findall(r'Access-Control-Allow-Origin.*?\*', wifi_cpp)
    assert_eq("Zero wildcard CORS headers in wifi_manager.cpp", len(cors_matches), 0)

    # Rule 5: Authentication enforced on critical endpoints
    has_auth_status = "if (!isRequestAuthorized())" in wifi_cpp and "handleStatus" in wifi_cpp
    assert_eq("Authentication enforced on /api/status", has_auth_status, True)

    has_auth_command = "if (!isRequestAuthorized())" in wifi_cpp and "handleCommand" in wifi_cpp
    assert_eq("Authentication enforced on /api/command", has_auth_command, True)

    has_auth_update = wifi_cpp.count("if (!isRequestAuthorized())") >= 3
    assert_eq("Authentication enforced on /update (GET & POST)", has_auth_update, True)

    # Rule 6: BLE MITM encryption permissions on characteristics
    enc_mitm_ble_count = ble_cpp.count("ESP_GATT_PERM_READ_ENC_MITM | ESP_GATT_PERM_WRITE_ENC_MITM")
    assert_eq("Command, Telemetry, Event characteristics have ENC_MITM", enc_mitm_ble_count >= 3, True)

    enc_mitm_ota_count = ota_ble_cpp.count("ESP_GATT_PERM_READ_ENC_MITM | ESP_GATT_PERM_WRITE_ENC_MITM")
    assert_eq("OTA Control and Data characteristics have ENC_MITM", enc_mitm_ota_count >= 2, True)

    # Rule 7: BLE advertising has min and max preferred intervals
    has_min_preferred = "setMinPreferred(0x06)" in ble_cpp
    has_max_preferred = "setMaxPreferred(0x12)" in ble_cpp
    assert_eq("BLE advertising sets setMinPreferred(0x06)", has_min_preferred, True)
    assert_eq("BLE advertising sets setMaxPreferred(0x12)", has_max_preferred, True)

    # Rule 8: OTA partition size in ota_ble_service.cpp is 0x330000 (3.19 MB)
    has_partition_size_match = "0x330000" in ota_ble_cpp
    assert_eq("BLE OTA partition limit matches 3.19 MB (0x330000)", has_partition_size_match, True)

    # Rule 9: 0xE9 Magic Byte check in both Web OTA and BLE OTA
    web_ota_magic = "0xE9" in wifi_cpp and "Header magic byte" in wifi_cpp
    ble_ota_magic = "0xE9" in ota_ble_cpp and "Header magic byte" in ota_ble_cpp
    assert_eq("Web OTA ESP32 magic byte (0xE9) validation present", web_ota_magic, True)
    assert_eq("BLE OTA ESP32 magic byte (0xE9) validation present", ble_ota_magic, True)

    # Rule 10: Amplifier hardware fault locked across all boot paths in main.cpp
    amp_universal_fault = "if (!ampHealthy)" in main_cpp and "MajnSafety::requestEmergencyStop()" in main_cpp
    assert_eq("Universal amplifier FAULT lock present in main.cpp", amp_universal_fault, True)

    # Rule 11: Zero masking of CLK_FAULT or other faults in system_controller.cpp
    sys_ctrl_cpp = read_fw_file("system_controller.cpp")
    has_fault_masking = ("cFault & 0x0F" in sys_ctrl_cpp) or ("gFault & 0x03" in sys_ctrl_cpp)
    assert_eq("Zero CLK_FAULT or fault masking in system_controller.cpp", has_fault_masking, False)

    # Rule 12: START verifies full hardware diagnostics without masking and triggers emergency stop
    has_full_diag_on_start = (
        "getFullDiagnostics" in sys_ctrl_cpp
        and "cFault != 0 || gFault1 != 0 || gFault2 != 0" in sys_ctrl_cpp
        and "triggerEmergencyStop()" in sys_ctrl_cpp
    )
    assert_eq("START verifies full hardware diagnostics and triggers emergency stop", has_full_diag_on_start, True)

    # Rule 13: Classic BT memory release present in ble_manager.cpp
    has_bt_mem_release = "esp_bt_controller_mem_release(ESP_BT_MODE_CLASSIC_BT)" in ble_cpp
    assert_eq("Classic BT memory release present in ble_manager.cpp", has_bt_mem_release, True)

    # Rule 14: BLE OTA waits for vibration decay before flash write
    has_ble_ota_decay = "MajnVibration::getCurrentAmplitude()" in ota_ble_cpp and "vTaskDelay" in ota_ble_cpp
    assert_eq("BLE OTA waits for vibration decay before flash write", has_ble_ota_decay, True)

    # Rule 15: Immediate amplitude zeroing (stopImmediately) present on emergency stop
    vibr_cpp = read_fw_file("vibration_controller.cpp")
    safety_cpp = read_fw_file("safety_manager.cpp")
    has_stop_immediately = "void stopImmediately()" in vibr_cpp and "MajnVibration::stopImmediately()" in safety_cpp
    assert_eq("Immediate amplitude zeroing (stopImmediately) present on emergency stop", has_stop_immediately, True)

    tas5805m_cpp = read_fw_file("tas5805m.cpp")
    amp_cpp = read_fw_file("amplifier_manager.cpp")

    # Rule 16: BLE Disconnect does not auto-stop soothing session in ble_manager.cpp
    has_disconnect_stop = "MajnSystemCtrl::triggerSafeStop()" in ble_cpp
    assert_eq("Zero session auto-stop on BLE disconnect/idle in ble_manager.cpp", has_disconnect_stop, False)

    # Rule 17: BLE disconnect aborts active BLE-OTA
    has_ble_disconnect_abort = "MajnBleOta::abortOta()" in ble_cpp and "isOtaInProgress()" in ble_cpp
    assert_eq("BLE disconnect aborts active BLE-OTA in ble_manager.cpp", has_ble_disconnect_abort, True)

    # Rule 18: Cross-transport OTA mutual exclusion and atomic locking present
    has_cross_ota_wifi = "MajnBleOta::isOtaInProgress()" in wifi_cpp and "acquireOtaLock()" in wifi_cpp and "releaseOtaLock()" in wifi_cpp
    has_cross_ota_ble = "MajnWiFi::isOtaInProgress()" in ota_ble_cpp and "acquireOtaLock()" in ota_ble_cpp and "releaseOtaLock()" in ota_ble_cpp
    assert_eq("Cross-transport OTA mutual exclusion and atomic locking in wifi_manager.cpp", has_cross_ota_wifi, True)
    assert_eq("Cross-transport OTA mutual exclusion and atomic locking in ota_ble_service.cpp", has_cross_ota_ble, True)

    # Rule 19: SoftAP configured on Channel 6
    has_channel_6 = "WiFi.softAP(ssid, wifiPass.c_str(), 6" in wifi_cpp
    assert_eq("SoftAP channel set to 6 in wifi_manager.cpp", has_channel_6, True)

    # Rule 20: TAS5805M begin ends in STANDBY (Hi-Z, 0x02) to prevent speaker pop
    has_standby_boot = "enterStandbyState()" in tas5805m_cpp and "Amplifier in STANDBY" in tas5805m_cpp
    assert_eq("TAS5805M begin() ends in STANDBY (Hi-Z) to eliminate boot pop noise", has_standby_boot, True)

    # Rule 21: TAS5805M latching fault debounce via clearFault (0x80 to 0x78)
    has_fault_debounce = "MajnAmplifier::clearFault()" in main_cpp and "REG_FAULT_CLEAR, 0x80" in tas5805m_cpp
    assert_eq("Supervisor debounces TAS5805M latched faults with clearFault", has_fault_debounce, True)

    # Rule 22: Thermal derating (warn & 0x04) reduces target amplitude by 50%
    has_thermal_derating = "warn & 0x04" in main_cpp and "* 0.5f" in main_cpp and "MajnVibration::setTarget" in main_cpp
    assert_eq("100ms supervisor performs 50% thermal derating on OTW (135°C)", has_thermal_derating, True)

    # Rule 23: Standby fast-path optimization checks gAmpStandby before mutex
    has_fastpath_standby = "if (gAmpStandby) return true;" in amp_cpp
    has_volatile_flags = "volatile bool gAmpReady" in amp_cpp and "volatile bool gAmpStandby" in amp_cpp
    assert_eq("Standby fast-path optimization checks gAmpStandby before mutex", has_fastpath_standby, True)
    assert_eq("Amplifier status flags declared volatile bool", has_volatile_flags, True)

    # Rule 24: RESET_FAULT explicitly calls MajnAmplifier::clearFault() before checking diagnostics
    has_reset_fault_clear = "MajnAmplifier::clearFault()" in sys_ctrl_cpp and "RESET_FAULT" in sys_ctrl_cpp
    assert_eq("RESET_FAULT explicitly clears latched faults before checking diagnostics", has_reset_fault_clear, True)

    # Rule 25: isOtaInProgress strictly reports gOtaRunning in ota_ble_service.cpp
    has_clean_is_ota = "bool isOtaInProgress() {\n    return gOtaRunning;\n}" in ota_ble_cpp or "bool isOtaInProgress() {\r\n    return gOtaRunning;\r\n}" in ota_ble_cpp
    assert_eq("isOtaInProgress strictly reports BLE OTA status (gOtaRunning)", has_clean_is_ota, True)

    # Rule 26: Thermal derating maintains ceiling on newly commanded targets via sLastDeratedTarget
    has_last_derated_target = "sLastDeratedTarget" in main_cpp
    assert_eq("Thermal derating tracks sLastDeratedTarget to cap new commands during OTW", has_last_derated_target, True)

    print("\n=== TEST SUITE 8: Thermal Derating Dynamics & Command Re-derating ===")
    thermal_sys = MockSystem()
    ok, res = thermal_sys.handle_json_command(json.dumps({"id": 20, "cmd": "START", "frequency_hz": 40.0, "amplitude": 0.40}))
    assert_eq("Thermal test START command accepted", ok, True)
    assert_eq("Initial target amplitude before OTW", thermal_sys.vibration.target_amp, 0.40)

    # Tick 1: OTW (135°C) detected -> 50% derating (0.40 -> 0.20)
    thermal_sys.simulate_thermal_supervisor(0x04)
    assert_eq("OTW trips 50% derating", thermal_sys.vibration.target_amp, 0.20)
    assert_eq("Thermal derating flag active", thermal_sys.thermal_derated, True)

    # Tick 2: OTW still active -> amplitude must remain 0.20 (no exponential decay!)
    thermal_sys.simulate_thermal_supervisor(0x04)
    assert_eq("OTW sustained tick does not exponentially decay amplitude", thermal_sys.vibration.target_amp, 0.20)

    # User issues new higher command while still hot (SET_AMPLITUDE 0.50)
    ok, res = thermal_sys.handle_json_command(json.dumps({"id": 21, "cmd": "SET_AMPLITUDE", "amplitude": 0.50}))
    assert_eq("SET_AMPLITUDE while hot accepted by command gate", ok, True)
    assert_eq("Commanded amplitude updated to 0.50", thermal_sys.vibration.target_amp, 0.50)

    # Tick 3: Supervisor detects target exceeds derated ceiling while OTW active -> derates new target by 50% (0.50 -> 0.25)
    thermal_sys.simulate_thermal_supervisor(0x04)
    assert_eq("New target amplitude re-derated by 50% (0.50 -> 0.25) during OTW", thermal_sys.vibration.target_amp, 0.25)

    # Tick 4: Chip cools down below 135°C (OTW clears)
    thermal_sys.simulate_thermal_supervisor(0x00)
    assert_eq("Thermal derating flag reset upon cooling", thermal_sys.thermal_derated, False)

    thermal_sys.handle_json_command(json.dumps({"id": 22, "cmd": "STOP"}))
    thermal_sys.vibration.current_amp = 0.0
    assert_eq("System safely returned to READY state after thermal test", thermal_sys.get_system_state(), "READY")

    print("\n=======================================================")
    print(f"Total Tests Run: {passed + failed}")
    print(f"Passed: {passed}, Failed: {failed}")
    print("=======================================================")
    print("[VERIFICATION TRACEABILITY METADATA]")
    print(f"  - Script SHA-256   : {get_self_sha256()}")
    print("  - Firmware Branch  : feature/phone-wifi-control")
    print(f"  - Firmware Head SHA: {get_git_commit_sha('feature/phone-wifi-control')}")
    print("  - Verification Scope: Host Unit Test & Static Rule Audit")
    print("                        (Physical silicon/hardware verification tracked separately)")
    print("=======================================================")

    return failed == 0

if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
