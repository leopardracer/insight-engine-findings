#!/usr/bin/env python3
"""Mask the last two groups of a device_id before publishing a packet.

  python tools/redact.py samples/packet_0412.json   # edits in place
  python tools/redact.py --check samples/           # exit 1 if anything is unmasked

FICTION: part of a story on X. Synthetic data only.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

MASK = "████"
DEVICE = re.compile(r"^(?P<head>[A-Z0-9]+-[0-9A-F]{4})-(?P<a>[^-]+)-(?P<b>[^-]+)$")


def redact_id(device_id: str) -> str:
    m = DEVICE.match(device_id)
    if not m:
        return device_id
    return f"{m['head']}-{MASK}-{MASK}"


def is_redacted(device_id: str) -> bool:
    return device_id.endswith(f"-{MASK}-{MASK}") or not DEVICE.match(device_id)


def files(target: Path) -> list[Path]:
    return sorted(target.glob("packet_*.json")) if target.is_dir() else [target]


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("path", type=Path)
    ap.add_argument("--check", action="store_true")
    args = ap.parse_args(argv)
    bad = 0
    for f in files(args.path):
        data = json.loads(f.read_text(encoding="utf-8"))
        dev = data.get("device_id", "")
        if args.check:
            if not is_redacted(dev):
                print(f"UNREDACTED {f.name}: {dev}")
                bad += 1
            continue
        new = redact_id(dev)
        if new != dev:
            data["device_id"] = new
            f.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
            print(f"redacted {f.name}")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
