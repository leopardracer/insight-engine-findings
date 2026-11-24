> [!WARNING]
> **This is fiction.** This repository is part of a serialized story posted on X by [@leopardracer](https://x.com/leopardracer). "Insight Engine" does not exist. Every packet, endpoint and number here is synthetic and was written for the story. Nothing in this repo is evidence of anything about any real game, console or company.

# What GTA 6 sends home while it's paused

> Everything I pulled out of the Insight Engine module before I got fired. Packet samples, endpoints, the decoder, and how to check your own console. Fork it. I don't know how long this stays up.
>
> *(in-story text, see the warning above)*

## What it collects

| field | example from my own console | how often |
|---|---|---|
| `ambient_tags` | child_voice, tv_audio:news, raised_voices | every 90s |
| `keywords` | mortgage, late payment, divorce | every 90s |
| `household` | 2 adults, 1 child, income band C | daily |
| `game_state` | PAUSED, MENU, IDLE (sent anyway) | every 90s |
| `mic.consent_flag` | **false** | every packet |

## Read the samples yourself

```bash
python3 decoder/decode.py samples/
```

The decoder prints a timeline of every packet in `samples/`: what the "console" was doing and what it "heard".

## Check your own network

In the story, the module uploads ~2 KB every 90 seconds to `203.0.113.42:443`.

That address is from `203.0.113.0/24`, a range reserved for documentation (RFC 5737). It is not routable and you will never see it on a real network, because none of this is real.

## About the story

- Day 1: the firing
- Day 2: the dashboard
- Day 3: the call
- Day 4: this repo

Follow along on X: [@leopardracer](https://x.com/leopardracer)
