import copy
import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]/"scripts"/"research"))
from gerchik_independent_labels_v0_1 import validate_labels, packet_digest


class LabelTests(unittest.TestCase):
    def setUp(self):
        self.packet = {"panels": [{"case_id": "A", "symbol": "FIXTURE", "as_of_ms": 200,
                                  "d1": [[100,"10","12","9","11","0",199]], "w1": []}]}
        self.meta = {"FIXTURE": {"tick_size": "1", "effective_from_ms": 0,
                                 "effective_until_ms": 200, "provenance": "synthetic"}}
        self.review = {"case_id": "A", "reviewer_id": "synthetic-reviewer",
                       "packet_sha256": packet_digest(self.packet),
                       "proposer_id": "synthetic-proposer", "reviewed_at_ms": 300,
                       "decision": "LEVELS", "rationale": "synthetic pattern",
                       "levels": [{"source_bar_id": "d1:100", "source_field": "low", "price": "9",
                                   "primary_type": "HISTORICAL", "pattern_bar_ids": ["d1:100"],
                                   "pattern_rationale": "synthetic reviewed claim, not automatic detection"}]}

    def run_labels(self, review=None, metadata=None):
        return validate_labels(self.packet, self.meta if metadata is None else metadata,
                               [self.review if review is None else review], evaluated_at=300)

    def test_reference_only_no_backdating(self):
        result = self.run_labels()
        self.assertEqual(result["status"], "REFERENCE_LABELS_COMPLETE")
        self.assertEqual(result["tradable_levels_created"], 0)

    def test_missing_real_reviews_stay_pending(self):
        result = validate_labels(self.packet, {}, [], evaluated_at=300)
        self.assertEqual(result["missing_case_ids"], ["A"])
        self.assertEqual(result["status"], "PENDING")

    def test_self_review_is_not_independent(self):
        r = copy.deepcopy(self.review); r["reviewer_id"] = r["proposer_id"]
        self.assertEqual(self.run_labels(r)["issues"][0]["reason"], "INDEPENDENT_REVIEWER_REQUIRED")

    def test_current_metadata_does_not_cover_history(self):
        m = copy.deepcopy(self.meta); m["FIXTURE"]["effective_from_ms"] = 150
        self.assertEqual(self.run_labels(metadata=m)["issues"][0]["reason"], "TICK_METADATA_PERIOD_NOT_COVERED")
        self.assertEqual(self.run_labels(metadata={})["issues"][0]["reason"], "HISTORICAL_TICK_METADATA_REQUIRED")

    def test_wrong_price_duplicate_type_or_future_witness_rejected(self):
        for change in ("price", "duplicate", "future"):
            r = copy.deepcopy(self.review)
            if change == "price": r["levels"][0]["price"] = "10"
            elif change == "duplicate": r["levels"].append(copy.deepcopy(r["levels"][0]))
            else: r["levels"][0]["pattern_bar_ids"].append("d1:200")
            with self.assertRaises(ValueError): self.run_labels(r)

    def test_scores_and_availability_cannot_leak_into_labels(self):
        r = copy.deepcopy(self.review); r["packet_sha256"] = "0"*64
        with self.assertRaises(ValueError): self.run_labels(r)
        r = copy.deepcopy(self.review); r["score"] = 80
        with self.assertRaises(ValueError): self.run_labels(r)
        r = copy.deepcopy(self.review); r["levels"][0]["tradable_known_at"] = 100
        with self.assertRaises(ValueError): self.run_labels(r)

    def test_review_timestamp_and_tick_mismatch_rejected(self):
        r = copy.deepcopy(self.review); r["reviewed_at_ms"] = 301
        with self.assertRaises(ValueError): self.run_labels(r)
        m = copy.deepcopy(self.meta); m["FIXTURE"]["tick_size"] = "2"
        with self.assertRaises(ValueError): self.run_labels(metadata=m)

    def test_negative_reference_example_can_be_recorded(self):
        r = copy.deepcopy(self.review); r.update(decision="NO_LEVELS", levels=[])
        self.assertEqual(self.run_labels(r)["accepted"][0]["labels"], 0)


if __name__ == "__main__": unittest.main()
