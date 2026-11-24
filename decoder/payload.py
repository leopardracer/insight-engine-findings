"""Parsing and validation of ambient payloads (v2 and v3)."""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path

SUPPORTED_VERSIONS = (2, 3)
GAME_STATES = {"PLAYING", "PAUSED", "MENU", "IDLE"}


class PayloadError(ValueError):
    """Raised when a packet does not look like an ambient payload."""


@dataclass(frozen=True)
class Payload:
    version: int
    module: str
    device_id: str
    ts: datetime
    game_state: str
    inactive_min: int
    mic_source: str
    consent: bool
    tags: tuple[str, ...]
    household: dict = field(default_factory=dict)
    dest: str = ""
    next_upload_s: int = 0
    debug_ref: str | None = None
    source: str = ""

    @property
    def keywords(self) -> tuple[str, ...]:
        return tuple(t.split(":", 1)[1] for t in self.tags if t.startswith("keyword:"))

    @property
    def ambient(self) -> tuple[str, ...]:
        return tuple(t for t in self.tags if not t.startswith("keyword:"))

    @property
    def player_absent(self) -> bool:
        return self.game_state in {"PAUSED", "MENU", "IDLE"}


def _parse_ts(raw: str) -> datetime:
    try:
        return datetime.fromisoformat(raw.replace("Z", "+00:00"))
    except (TypeError, ValueError) as exc:
        raise PayloadError(f"bad timestamp: {raw!r}") from exc


def parse(data: dict, source: str = "") -> Payload:
    version = data.get("v")
    if version not in SUPPORTED_VERSIONS:
        raise PayloadError(f"{source or 'packet'}: unsupported payload version {version!r}")
    state = str(data.get("game_state", "")).upper()
    if state not in GAME_STATES:
        raise PayloadError(f"{source or 'packet'}: unknown game_state {state!r}")

    # v2 kept tags flat under "tags"; v3 moved them to "ambient_tags"
    tags = data.get("ambient_tags") if version == 3 else data.get("tags", [])
    mic = data.get("mic") or {}

    return Payload(
        version=version,
        module=data.get("module", "insight.ambient"),
        device_id=data.get("device_id", "unknown"),
        ts=_parse_ts(data.get("ts")),
        game_state=state,
        inactive_min=int(data.get("paused_for_min", data.get("idle_for_min", 0))),
        mic_source=mic.get("source", "unknown"),
        consent=bool(mic.get("consent_flag", False)),
        tags=tuple(tags or ()),
        household=dict(data.get("household") or {}),
        dest=data.get("dest", ""),
        next_upload_s=int(data.get("next_upload_s", 0)),
        debug_ref=data.get("debug_ref"),
        source=source,
    )


def load(path: str | Path) -> Payload:
    path = Path(path)
    with path.open(encoding="utf-8") as fh:
        try:
            data = json.load(fh)
        except json.JSONDecodeError as exc:
            raise PayloadError(f"{path.name}: not valid JSON ({exc.msg})") from exc
    return parse(data, source=path.name)


def load_dir(folder: str | Path) -> list[Payload]:
    folder = Path(folder)
    files = sorted(folder.glob("packet_*.json")) if folder.is_dir() else [folder]
    return sorted((load(f) for f in files), key=lambda p: p.ts)
