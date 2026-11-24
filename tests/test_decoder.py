import json
import tempfile
import unittest
from pathlib import Path

from decoder.payload import PayloadError, load_dir, parse
from decoder.stats import gaps, summarize
from tools.redact import is_redacted, redact_id

SAMPLES = Path(__file__).resolve().parent.parent / "samples"


class PayloadTests(unittest.TestCase):
    def test_samples_load_in_time_order(self):
        payloads = load_dir(SAMPLES)
        self.assertEqual(len(payloads), 6)
        self.assertEqual([p.ts for p in payloads], sorted(p.ts for p in payloads))

    def test_v2_payload_uses_flat_tags(self):
        p = parse({"v": 2, "game_state": "menu", "ts": "2026-06-02T10:00:00Z", "tags": ["tv_audio:music"]})
        self.assertEqual(p.tags, ("tv_audio:music",))
        self.assertEqual(p.game_state, "MENU")

    def test_unknown_version_is_rejected(self):
        with self.assertRaises(PayloadError):
            parse({"v": 9, "game_state": "IDLE", "ts": "2026-06-02T10:00:00Z"})

    def test_keywords_are_split_from_ambient_tags(self):
        p = parse({"v": 3, "game_state": "PAUSED", "ts": "2026-11-23T22:41:07Z",
                   "ambient_tags": ["child_voice", "keyword:mortgage"]})
        self.assertEqual(p.keywords, ("mortgage",))
        self.assertEqual(p.ambient, ("child_voice",))


class StatsTests(unittest.TestCase):
    def test_summary_counts(self):
        s = summarize(load_dir(SAMPLES))
        self.assertEqual(s.packets, 6)
        self.assertEqual(s.without_consent, 6)
        self.assertEqual(s.debug_refs, 1)

    def test_gaps_are_positive(self):
        self.assertTrue(all(g > 0 for g in gaps(load_dir(SAMPLES))))


class RedactTests(unittest.TestCase):
    def test_redact_masks_last_groups(self):
        self.assertEqual(redact_id("PS5-7F3A-91C2-04BE"), "PS5-7F3A-████-████")

    def test_all_samples_are_redacted(self):
        for f in SAMPLES.glob("packet_*.json"):
            dev = json.loads(f.read_text(encoding="utf-8"))["device_id"]
            self.assertTrue(is_redacted(dev), f.name)


if __name__ == "__main__":
    unittest.main()
