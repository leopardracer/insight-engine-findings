#!/usr/bin/env python3
"""Decoder for the (fictional) Insight Engine ambient payloads.

Part of a fiction story. Reads the synthetic JSON samples in samples/
and prints a readable timeline. No network access, no dependencies.
"""
import json
import sys
from pathlib import Path

SUPPORTED = {2}


def load(path: Path) -> dict:
    with path.open(encoding="utf-8") as f:
        pkt = json.load(f)
    if pkt.get("v") not in SUPPORTED:
        raise ValueError(f"{path.name}: unsupported payload version {pkt.get('v')}")
    return pkt


def describe(pkt: dict) -> str:
    state = pkt["game_state"]
    mins = pkt.get("paused_for_min", pkt.get("idle_for_min", 0))
    tags = ", ".join(pkt.get("ambient_tags", [])) or "-"
    consent = "yes" if pkt["mic"]["consent_flag"] else "NO"
    return f"{pkt['ts']}  {state:<6} {mins:>4} min  consent:{consent:<3}  heard: {tags}"


def main(argv: list[str]) -> int:
    target = Path(argv[1]) if len(argv) > 1 else Path("samples")
    files = sorted(target.glob("packet_*.json")) if target.is_dir() else [target]
    if not files:
        print(f"no packets found in {target}", file=sys.stderr)
        return 1
    print("FICTION: synthetic data written for a story. See README.\n")
    for p in files:
        print(f"{p.name}  {describe(load(p))}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
