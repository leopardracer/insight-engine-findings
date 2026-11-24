#!/usr/bin/env python3
"""Backwards-compatible wrapper. Prefer: python -m decoder timeline samples/

FICTION: part of a story on X. Synthetic data only.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from decoder.__main__ import main  # noqa: E402

if __name__ == "__main__":
    sys.exit(main(["timeline", *sys.argv[1:]]))
