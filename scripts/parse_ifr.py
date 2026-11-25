#!/usr/bin/env python3
"""Search VarStores and options inside an extracted ifrextract text dump."""

import argparse
import re
import sys


VARSTORE_RE = re.compile(
    r"VarStore(?:EFI)?:\s+VarStoreId:\s+(0x[0-9A-Fa-f]+)\s+\[([0-9A-Fa-f-]+)\].*?Size:\s*(?:0x)?([0-9A-Fa-f]+),\s+Name:\s+(\S+)"
)
OPTION_RE = re.compile(
    r"(One Of|Checkbox|Numeric):\s*(.*?),\s*VarStoreInfo\s*\(VarOffset/VarName\):\s*(0x[0-9A-Fa-f]+),\s*VarStore:\s*(0x[0-9A-Fa-f]+)"
)


def parse_varstores(lines: list[str]) -> dict[str, tuple[str, str, str]]:
    stores: dict[str, tuple[str, str, str]] = {}
    for line in lines:
        m = VARSTORE_RE.search(line)
        if m:
            vid, guid, size, name = m.groups()
            stores[vid.lower()] = (name, guid, f"0x{size.upper()}")
    return stores


def main() -> int:
    ap = argparse.ArgumentParser(description="Inspect and search an ifrextract dump.")
    ap.add_argument("ifr_file", help="Path to Setup.ifr.txt")
    ap.add_argument("--varstores", action="store_true", help="List all VarStores in the IFR dump")
    ap.add_argument("--search", "-s", help="Case-insensitive substring to search option prompts")
    args = ap.parse_args()

    with open(args.ifr_file, "r", encoding="utf-8", errors="replace") as f:
        lines = f.read().splitlines()

    stores = parse_varstores(lines)

    if args.varstores:
        for vid, (name, guid, size) in stores.items():
            print(f"{vid:>6}  {name:24s}  size={size:<6}  guid={guid}")
        if not args.search:
            return 0

    if not args.search:
        ap.print_help()
        return 1

    q = args.search.lower()
    matches = 0
    for idx, line in enumerate(lines):
        m = OPTION_RE.search(line)
        if not m:
            continue
        kind, prompt, offset, vid = m.groups()
        if q not in prompt.lower():
            continue
        matches += 1
        store_name = stores.get(vid.lower(), (vid, "", ""))[0]
        print(f"L{idx + 1}: [{store_name} @ {offset}] {kind}: {prompt}")
        for follow in lines[idx + 1 : idx + 14]:
            stripped = re.sub(r"^0x[0-9A-Fa-f]+\s+", "", follow.strip())
            if stripped.startswith(("End One Of", "End {")):
                break
            if stripped.startswith(("One Of Option:", "Default:")):
                print(f"    {stripped.split('{')[0].strip()}")
    if matches == 0:
        print(f"No options matching '{args.search}'", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
