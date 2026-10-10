import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from scripts.research.gerchik_level_event_ledger_v0_1 import LevelLedger, Evidence
from scripts.research.gerchik_structural_review_gate_v0_1 import verify_reviewed_extremum
from scripts.research.gerchik_ledger_cross_tf_evidence_v0_1 import ledger_cross_tf_evidence


class StrengthIntegrationTests(unittest.TestCase):
    def bundle(self, event_id, tf, price, end):
        event = dict(event_id=event_id, symbol="FIXTURE", timeframe=tf, source_field="low",
                     source_bar_id=event_id+"-bar", price=price, tick_size="1", observed_at=end)
        bar = dict(bar_id=event_id+"-bar", symbol="FIXTURE", timeframe=tf,
                   opened_at="2026-09-01T00:00:00Z", closed_at=end, low=price)
        review = dict(event_id=event_id, reviewer_id="synthetic-independent-reviewer",
                      decision="APPROVED", reviewed_at="2026-09-09T00:00:00Z")
        return dict(event=event, source_bar=bar, review=review)

    def test_overlap_confirmed_at_review_without_mutating_prices_or_primary_types(self):
        ledger = LevelLedger()
        bundles = {}
        for event_id, tf, price, end, primary in (
            ("D", "1d", "100", "2026-09-02T00:00:00Z", "HISTORICAL"),
            ("W", "1w", "101", "2026-09-08T00:00:00Z", "MIRROR")):
            ledger.record_formation(symbol="FIXTURE", timeframe=tf, price=price, tick_size="1",
                                    primary_type=primary, formed_at=end,
                                    formation_event_id=event_id, source_field="low")
            bundles[event_id] = self.bundle(event_id, tf, price, end)
        self.assertEqual(ledger_cross_tf_evidence(ledger, bundles, "2026-09-08T23:59:59Z", {"FIXTURE": 1}), [])
        pairs = ledger_cross_tf_evidence(ledger, bundles, "2026-09-09T00:00:00Z", {"FIXTURE": 1})
        self.assertEqual(len(pairs), 1)
        self.assertEqual(pairs[0]["distance"], "1")
        self.assertEqual(pairs[0]["primary_types"], ["HISTORICAL", "MIRROR"])
        self.assertEqual([str(x.price) for x in ledger.as_of("2026-09-09T00:00:00Z")], ["100", "101"])
        self.assertTrue(all(x.state == "CANDIDATE" for x in ledger.as_of("2026-09-09T00:00:00Z")))

    def test_review_checks_source_and_causal_available_time(self):
        b = self.bundle("D", "1d", "100", "2026-09-02T00:00:00Z")
        for mutation in ("price", "time", "review"):
            import copy
            x = copy.deepcopy(b)
            if mutation == "price":
                x["event"]["price"] = "101"
            elif mutation == "time":
                x["review"]["reviewed_at"] = "2026-09-01T00:00:00Z"
            else:
                x["review"]["decision"] = "PENDING"
            with self.assertRaises(ValueError):
                verify_reviewed_extremum(x["event"], x["source_bar"], x["review"], "2026-09-09T00:00:00Z")

    def test_one_primary_identity_and_evidence_deduplication(self):
        ledger = LevelLedger()
        args = dict(symbol="FIXTURE", timeframe="1d", price="100", tick_size="1",
                    formed_at="2026-09-02T00:00:00Z", source_field="low")
        level = ledger.record_formation(**args, primary_type="HISTORICAL", formation_event_id="F")
        with self.assertRaises(ValueError):
            ledger.record_formation(**args, primary_type="MIRROR", formation_event_id="M")
        evidence = Evidence("T", "TOUCH", "2026-09-03T00:00:00Z", "bar-T")
        ledger.add_evidence(level, evidence)
        with self.assertRaises(ValueError):
            ledger.add_evidence(level, evidence)
        self.assertEqual(level.primary_type, "HISTORICAL")


if __name__ == "__main__":
    unittest.main()
