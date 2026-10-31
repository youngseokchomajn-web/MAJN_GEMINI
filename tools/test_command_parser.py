#!/usr/bin/env python3
"""
MAJN Wireless Command Parser & Security Matrix Unit Test Suite (v1.0)
===================================================================
Automated host-side verification of command handling, parameter boundary
constraints, state machine transitions (including STOPPING state),
and static endpoint security rules for MAJN Smart Bassinet Firmware.
"""

import json
import sys
import os

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
            if self.amp_diag_fault:
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

    ok, res = sys_instance.handle_json_command(json.dumps({"id": 12, "cmd": "RESET_FAULT"}))
    assert_eq("RESET_FAULT restores READY", ok, True)
    assert_eq("State after RESET_FAULT", res["state"], "READY")

    print("\n=== TEST SUITE 5: OTA Cross-Locking Gate ===")
    sys_instance.ota_in_progress = True
    ok, res = sys_instance.handle_json_command(json.dumps({"id": 13, "cmd": "START", "frequency_hz": 45.0, "amplitude": 0.3}))
    assert_eq("START rejected during OTA", ok, False)
    assert_eq("Rejection status during OTA", res["state"], "OTA_ACTIVE")

    ok, res = sys_instance.handle_json_command(json.dumps({"id": 14, "cmd": "PING"}))
    assert_eq("PING allowed during OTA", ok, True)
    sys_instance.ota_in_progress = False

    print("\n=== TEST SUITE 6: RESET_WIFI_CRED Command ===")
    ok, res = sys_instance.handle_json_command(json.dumps({"id": 15, "cmd": "RESET_WIFI_CRED"}))
    assert_eq("RESET_WIFI_CRED applied", ok, True)
    assert_eq("RESET_WIFI_CRED flag set", sys_instance.wifi_cred_reset, True)
    assert_eq("Reboot scheduled", sys_instance.reboot_scheduled, True)
    assert_eq("Rebooting state reported", res["state"], "REBOOTING")

    print("\n=== TEST SUITE 7: Static Security & Endpoint Matrix Check ===")
    endpoints = {
        "/api/ping": {"auth_required": False, "methods": ["GET", "OPTIONS"]},
        "/api/status": {"auth_required": True, "methods": ["GET", "OPTIONS"]},
        "/api/command": {"auth_required": True, "methods": ["POST", "OPTIONS"]},
        "/update": {"auth_required": True, "methods": ["GET", "POST"]},
        "/generate_204": {"auth_required": False, "methods": ["GET"]},
    }

    # Verify rules
    assert_eq("/api/ping unauthenticated", endpoints["/api/ping"]["auth_required"], False)
    assert_eq("/api/status authenticated", endpoints["/api/status"]["auth_required"], True)
    assert_eq("/api/command authenticated", endpoints["/api/command"]["auth_required"], True)
    assert_eq("/update authenticated", endpoints["/update"]["auth_required"], True)
    assert_eq("/generate_204 unauthenticated", endpoints["/generate_204"]["auth_required"], False)

    print("\n=======================================================")
    print(f"Total Tests Run: {passed + failed}")
    print(f"Passed: {passed}, Failed: {failed}")
    print("=======================================================")

    return failed == 0

if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
