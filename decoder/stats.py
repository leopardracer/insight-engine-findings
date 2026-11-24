"""Aggregate views over a set of payloads."""
from __future__ import annotations

from collections import Counter
from dataclasses import dataclass

from .payload import Payload


@dataclass
class Summary:
    packets: int
    absent: int
    without_consent: int
    span_min: int
    states: Counter
    tags: Counter
    keywords: Counter
    debug_refs: int


def summarize(payloads: list[Payload]) -> Summary:
    states, tags, keywords = Counter(), Counter(), Counter()
    for p in payloads:
        states[p.game_state] += 1
        tags.update(p.ambient)
        keywords.update(p.keywords)
    span = 0
    if len(payloads) > 1:
        span = int((payloads[-1].ts - payloads[0].ts).total_seconds() // 60)
    return Summary(
        packets=len(payloads),
        absent=sum(p.player_absent for p in payloads),
        without_consent=sum(not p.consent for p in payloads),
        span_min=span,
        states=states,
        tags=tags,
        keywords=keywords,
        debug_refs=sum(p.debug_ref is not None for p in payloads),
    )


def gaps(payloads: list[Payload]) -> list[int]:
    """Minutes between consecutive packets."""
    return [
        int((b.ts - a.ts).total_seconds() // 60)
        for a, b in zip(payloads, payloads[1:])
    ]
