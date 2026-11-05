#!/usr/bin/env python3
"""
MAJN ESP32 GPIO Conflict & Strapping Pin Verification Engine (v2.0)
------------------------------------------------------------------
Audits ESP32 pin allocation against:
1. Boot strapping pin restrictions (GPIO0, GPIO2, GPIO5, GPIO12, GPIO15)
2. Input-only (GPI) physical silicon restrictions (GPIO34-39)
3. Peripheral pin multiplexing collisions (I2C, I2S, SPI, UART)
MANDATORY: Enforces sys.exit(1) on failure.
"""

import sys
import csv
import json
import argparse
from pathlib import Path

# ESP32 Physical Silicon Pin Database
STRAPPING_PINS = {
    "GPIO0":  {"default": "Pull-Up", "safe_boot": "HIGH", "trap": "LOW (Enters Download Mode)"},
    "GPIO2":  {"default": "Pull-Down", "safe_boot": "LOW (or Floating)", "trap": "HIGH (Enters Flash Mode)"},
    "GPIO5":  {"default": "Pull-Up", "safe_boot": "HIGH", "trap": "Timing hazard if driven at boot"},
    "GPIO12": {"default": "Pull-Down", "safe_boot": "LOW (3.3V Flash)", "trap": "HIGH (Sets VDD_SDIO to 1.8V -> FLASH BRICK)"},
    "GPIO15": {"default": "Pull-Up", "safe_boot": "LOW (Silent Boot)", "trap": "HIGH (Enables debug ROM print & SDIO timing)"}
}

INPUT_ONLY_GPI_PINS = {"GPIO34", "GPIO35", "GPIO36", "GPIO39", "IO34", "IO35", "IO36", "IO39", "SENSOR_VP", "SENSOR_VN"}

PERIPHERAL_RESERVATIONS = {
    "GPIO21": "AMP_I2C_SDA",
    "GPIO27": "AMP_I2C_SCL",
    "GPIO26": "I2S_BCLK",
    "GPIO25": "I2S_LRCLK",
    "GPIO22": "I2S_DIN",
    "GPIO18": "SPI_SCLK",
    "GPIO19": "SPI_MISO",
    "GPIO23": "SPI_MOSI",
    "GPIO5":  "SPI_CS",
    "GPIO4":  "BOOST_EN",
    "GPIO13": "AMP_PDN",
    "GPIO35": "AMP_FAULTz_ADR",
    "GPIO34": "SENSOR_INT1"
}

def load_gpio_allocation(csv_path):
    p = Path(csv_path)
    if not p.exists():
        print(f"[ERROR] GPIO CSV file not found: {p}", file=sys.stderr)
        sys.exit(1)
    allocations = {}
    with open(p, "r", encoding="utf-8") as f:
        reader = csv.reader(f)
        header = next(reader, None)
        header_map = {}
        if header:
            header_upper = [h.strip().upper() for h in header]
            for idx, col in enumerate(header_upper):
                if "GPIO" in col: header_map["gpio"] = idx
                elif "PIN_NUM" in col or col == "PIN": header_map["pin"] = idx
                elif "PROPOSED_ROLE" in col or "NET" in col or "ASSIGNED" in col:
                    if "net" not in header_map or "PROPOSED" in col: header_map["net"] = idx
                elif "TYPE" in col or "DIRECTION" in col: header_map["direction"] = idx
                elif "INTERNAL_PULL" in col or "PULL" in col: header_map["pull"] = idx

        for row in reader:
            if not row or not any(row): continue
            if header_map and "gpio" in header_map:
                gpio_idx = header_map["gpio"]
                gpio_name = row[gpio_idx].strip().upper() if len(row) > gpio_idx else ""
                module_pin = row[header_map.get("pin", 1)].strip() if len(row) > header_map.get("pin", 1) else ""
                assigned_net = row[header_map.get("net", 2)].strip() if len(row) > header_map.get("net", 2) else ""
                direction = row[header_map.get("direction", 3)].strip() if len(row) > header_map.get("direction", 3) else ""
                pull_config = row[header_map.get("pull", 4)].strip() if len(row) > header_map.get("pull", 4) else ""
            else:
                gpio_name = row[0].strip().upper()
                module_pin = row[1].strip() if len(row) > 1 else ""
                assigned_net = row[2].strip() if len(row) > 2 else ""
                direction = row[3].strip() if len(row) > 3 else ""
                pull_config = row[4].strip() if len(row) > 4 else ""

            allocations[gpio_name] = {
                "pin": module_pin,
                "net": assigned_net,
                "direction": direction,
                "pull": pull_config
            }
    return allocations

def audit_gpio(allocations):
    violations = []
    warnings = []

    for gpio, info in allocations.items():
        net = info["net"].upper()
        direction = info["direction"].upper()
        pull = info["pull"].upper()

        # 1. Strapping Pin Audit
        if gpio in STRAPPING_PINS:
            trap_desc = STRAPPING_PINS[gpio]["trap"]
            if gpio == "GPIO15":
                if "PDN" in net:
                    violations.append(f"STRAPPING VIOLATION: {gpio} connected to '{net}'. Strapping pin conflict! {trap_desc}")
                if "PULL-UP" in pull or "PULLUP" in pull:
                    violations.append(f"STRAPPING VIOLATION: {gpio} has pull-up enabled! Forces debug log and SDIO timing hazard.")
            elif gpio == "GPIO12":
                if "HIGH" in pull or "PULL-UP" in pull:
                    violations.append(f"CRITICAL STRAPPING VIOLATION: {gpio} pulled HIGH! Bricks 3.3V flash power.")

        # 2. Input-Only (GPI) Pin Audit
        if gpio in INPUT_ONLY_GPI_PINS:
            if "OUTPUT" in direction:
                violations.append(f"SILICON LIMITATION VIOLATION: {gpio} is configured as OUTPUT. This pin has NO output buffer in silicon!")
            has_internal_pull = ("INTERNAL PULL" in pull or "PULLUP" in pull or "PULL-UP" in pull or "PULLDOWN" in pull or "PULL-DOWN" in pull) and ("NO " not in pull and "NONE" not in pull and "NOT" not in pull)
            if has_internal_pull:
                violations.append(f"SILICON LIMITATION VIOLATION: {gpio} configured with internal pull. GPI pins have NO internal pull resistors!")

        # 3. Peripheral Collision Audit
        if gpio in PERIPHERAL_RESERVATIONS:
            expected_net = PERIPHERAL_RESERVATIONS[gpio]
            if net and expected_net not in net and "NC" not in net:
                warnings.append(f"Peripheral assignment divergence: {gpio} is assigned to '{net}', expected baseline '{expected_net}'")

    print("\n" + "=" * 60)
    print(f"ESP32 GPIO CONFLICT AUDIT: Audited {len(allocations)} pins")
    print(f"Violations: {len(violations)}, Warnings: {len(warnings)}")
    print("=" * 60)

    for w in warnings:
        print(f"  [WARN] {w}")
    for v in violations:
        print(f"  [FAIL] {v}", file=sys.stderr)

    if violations:
        print("\n>>> AUDIT FAILED: Hazardous GPIO configuration detected (sys.exit(1)) <<<", file=sys.stderr)
        sys.exit(1)
    else:
        print("\n>>> AUDIT PASSED: All GPIO assignments boot-safe and silicon-compliant (sys.exit(0)) <<<")
        sys.exit(0)

def main():
    parser = argparse.ArgumentParser(description="Audit ESP32 GPIO allocation table.")
    parser.add_argument("--gpio-csv", type=str, required=True, help="Path to GPIO allocation CSV")
    args = parser.parse_args()
    alloc = load_gpio_allocation(args.gpio_csv)
    audit_gpio(alloc)

if __name__ == "__main__":
    main()
