#!/usr/bin/env python3
"""Read-only inspector for Dell Inspiron 5509 NVRAM setup variables under Linux efivarfs."""

import os
import sys

EFIVARS_DIR = "/sys/firmware/efi/efivars"

VARS = {
    "Setup": ("ec87d643-eba4-4bb5-a1e5-3f3e36b20da9", 0xAEC),
    "SaSetup": ("72c5e28c-7783-43a1-8767-fad73fccafa4", 0x44C),
    "CpuSetup": ("b08f97ff-e6e8-4193-a997-5e9e9b0adb32", 0x28E),
    "PchSetup": ("4570b7f1-ade8-4943-8dc3-406472842384", 0x7EC),
}

FIELDS = [
    ("SaSetup", 0x84, "DVMT Pre-Allocated", {0x00: "0M", 0x01: "32M", 0x02: "64M", 0x03: "96M", 0x04: "128M", 0xFE: "60M (Dell default)"}),
    ("SaSetup", 0x85, "DVMT Total Gfx Mem", {0x01: "128M", 0x02: "256M", 0x03: "MAX"}),
    ("SaSetup", 0x87, "VT-d", {0x00: "Disabled", 0x01: "Enabled"}),
    ("SaSetup", 0x88, "Above 4GB MMIO", {0x00: "Disabled", 0x01: "Enabled"}),
    ("CpuSetup", 0x43, "CFG Lock (MSR 0xE2)", {0x00: "Disabled", 0x01: "Enabled"}),
    ("CpuSetup", 0xDF, "Overclocking Lock", {0x00: "Disabled", 0x01: "Enabled"}),
    ("Setup", 0x0D, "Enable ACPI Auto Config", {0x00: "Disabled", 0x01: "Enabled"}),
    ("Setup", 0x0E, "ACPI S3 Support", {0x00: "Disabled", 0x01: "Enabled"}),
    ("Setup", 0x1C, "Low Power S0 Idle (S0ix)", {0x00: "Disabled", 0x01: "Enabled"}),
    ("Setup", 0x6BE, "Integrated Thunderbolt", {0x00: "Disabled", 0x01: "Enabled"}),
    ("Setup", 0x6C2, "Wake From Thunderbolt", {0x00: "Disabled", 0x01: "Enabled"}),
    ("PchSetup", 0x49, "SATA Mode", {0x00: "AHCI", 0x01: "RAID/RST"}),
    ("PchSetup", 0x600, "Enable 8254 Clock Gate", {0x00: "Disabled", 0x01: "Enabled", 0x02: "Runtime + S3 Resume"}),
]


def load_var(name: str, guid: str, expected_size: int) -> bytes | None:
    path = os.path.join(EFIVARS_DIR, f"{name}-{guid}")
    if not os.path.exists(path):
        return None
    with open(path, "rb") as f:
        raw = f.read()
    payload = raw[4:]  # strip 4-byte UEFI attribute header
    if len(payload) != expected_size:
        print(f"[warn] {name}: got {len(payload)} bytes, expected {expected_size} (different BIOS version?)", file=sys.stderr)
    return payload


def main() -> int:
    if not os.path.isdir(EFIVARS_DIR):
        print(f"Error: {EFIVARS_DIR} not found (not booted in UEFI mode?)", file=sys.stderr)
        return 1

    loaded = {name: load_var(name, guid, size) for name, (guid, size) in VARS.items()}

    for store, offset, label, labels in FIELDS:
        buf = loaded.get(store)
        if buf is None or offset >= len(buf):
            print(f"{store}[0x{offset:03X}] {label:28s}: <unavailable>")
            continue
        val = buf[offset]
        desc = labels.get(val, "unknown")
        print(f"{store}[0x{offset:03X}] {label:28s}: 0x{val:02X} ({desc})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
