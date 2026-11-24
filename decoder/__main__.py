"""Command line entry point: python -m decoder <command> [path]"""
from __future__ import annotations

import argparse
import csv
import sys

from . import __version__
from .payload import PayloadError, load_dir
from .stats import gaps, summarize

BANNER = "FICTION: synthetic data written for a story on X. See README.\n"
DIM, RED, YEL, RST = "\033[2m", "\033[31m", "\033[33m", "\033[0m"


def _c(text: str, color: str, on: bool) -> str:
    return f"{color}{text}{RST}" if on else text


def cmd_timeline(payloads, args) -> int:
    for p in payloads:
        consent = _c("NO ", RED, args.color) if not p.consent else "yes"
        heard = ", ".join(p.tags) or "-"
        line = (f"{_c(p.source, DIM, args.color)}  {p.ts:%H:%M:%S}  {p.game_state:<6}"
                f" {p.inactive_min:>4} min  consent:{consent}  heard: {heard}")
        print(line)
        if args.debug and p.debug_ref:
            print(_c(f"    debug_ref present ({len(p.debug_ref)} chars, base64)", YEL, args.color))
    return 0


def cmd_stats(payloads, args) -> int:
    s = summarize(payloads)
    print(f"packets            {s.packets}")
    print(f"player away        {s.absent}/{s.packets}")
    print(f"no mic consent     {s.without_consent}/{s.packets}")
    print(f"time covered       {s.span_min} min")
    print(f"gaps between       {', '.join(map(str, gaps(payloads))) or '-'} min")
    print("states             " + ", ".join(f"{k}:{v}" for k, v in s.states.most_common()))
    print("most heard         " + ", ".join(f"{k}({v})" for k, v in s.tags.most_common(5)))
    print("keywords           " + (", ".join(s.keywords) or "-"))
    if s.debug_refs:
        print(_c(f"debug refs         {s.debug_refs} (run timeline --debug)", YEL, args.color))
    return 0


def cmd_csv(payloads, args) -> int:
    w = csv.writer(sys.stdout)
    w.writerow(["file", "ts", "game_state", "inactive_min", "consent", "tags"])
    for p in payloads:
        w.writerow([p.source, p.ts.isoformat(), p.game_state, p.inactive_min, p.consent, "|".join(p.tags)])
    return 0


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="decoder", description="Read Insight Engine ambient payloads (fiction).")
    ap.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    ap.add_argument("--no-color", dest="color", action="store_false")
    sub = ap.add_subparsers(dest="cmd")
    for name, fn in (("timeline", cmd_timeline), ("stats", cmd_stats), ("csv", cmd_csv)):
        sp = sub.add_parser(name)
        sp.add_argument("path", nargs="?", default="samples")
        sp.set_defaults(fn=fn)
        if name == "timeline":
            sp.add_argument("--debug", action="store_true", help="show debug fields")
    args = ap.parse_args(argv)
    if not args.cmd:
        args = ap.parse_args(["timeline", *(argv or sys.argv[1:])])
    if not sys.stdout.isatty():
        args.color = False
    try:
        payloads = load_dir(args.path)
    except (PayloadError, FileNotFoundError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    if not payloads:
        print(f"no packets in {args.path}", file=sys.stderr)
        return 1
    if args.cmd != "csv":
        print(BANNER)
    return args.fn(payloads, args)


if __name__ == "__main__":
    sys.exit(main())
