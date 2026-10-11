import sys
import unittest
from dataclasses import replace
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts" / "research"))
from gerchik_level_strength_v0_1 import BASE, Formation, Policy, Proof, SourceBar, rate


class StrengthTests(unittest.TestCase):
    def setUp(self):
        self.origin = SourceBar("origin", "FIXTURE", "1d", 0, 100, 110, 120, 100, 115)
        self.level = Formation("L1", "FIXTURE", 100, "1", "HISTORICAL", "origin", "low",
                               100, 100, "synthetic-reviewer", "synthetic-pattern-review", 100,
                               "APPROVED", "synthetic-primary-pattern", "CONFIRMED")
        self.policy = Policy("synthetic-not-market-policy", 2, 2, None, 0, "")
        self.touch = SourceBar("touch", "FIXTURE", "1d", 100, 200, 110, 120, 100, 115)
        self.proof = Proof("P1", "TOUCH", "touch", "SUPPORT", 200, 200,
                           "synthetic-reviewer", "APPROVED")

    def rating(self, level=None, bars=None, proofs=None, policy=None, as_of=1000):
        return rate(level or self.level, bars or [self.origin, self.touch],
                    [self.proof] if proofs is None else proofs, policy or self.policy, as_of=as_of)

    def test_exact_arithmetic_and_book_components(self):
        result = self.rating()
        self.assertEqual(result["score"], 32.5)  # 25 base + 5 touch + 2.5 wick
        self.assertIsNone(result["probability"])
        self.assertFalse(result["round_assessed"])

    def test_all_seven_types_and_equal_mirror_historical(self):
        for kind, base in BASE.items():
            self.assertEqual(self.rating(level=replace(self.level, primary_type=kind), proofs=[])["score"], base)
        self.assertEqual(BASE["MIRROR"], BASE["HISTORICAL"])

    def test_round_number_twenty_percent_is_labeled_model(self):
        policy = replace(self.policy, round_step_ticks=25, round_policy_provenance="synthetic-grid")
        result = self.rating(policy=policy)
        self.assertEqual(result["score"], 39)
        self.assertEqual(result["round_bonus"], 6.5)

    def test_false_break_and_near_miss_ohlc_validation(self):
        for kind, low, expected in (("FALSE_BREAKOUT", 99, 1), ("NEAR_MISS", 102, 1)):
            bar = replace(self.touch, low=low)
            proof = replace(self.proof, kind=kind)
            result = self.rating(bars=[self.origin, bar], proofs=[proof])
            self.assertEqual(result["counts"][kind], expected)
        with self.assertRaises(ValueError):
            self.rating(proofs=[replace(self.proof, kind="FALSE_BREAKOUT")])
        excursion = replace(self.touch, bar_id="excursion", close=98, low=97)
        returned = replace(self.touch, start=200, end=300, low=101)
        proof = replace(self.proof, kind="FALSE_BREAKOUT", known_at=300, reviewed_at=300,
                        related_bar_ids=("excursion", "touch"))
        self.assertEqual(self.rating(bars=[self.origin, excursion, returned], proofs=[proof])
                         ["counts"]["FALSE_BREAKOUT"], 1)
        with self.assertRaises(ValueError):
            self.rating(bars=[self.origin, replace(excursion, close=110), returned], proofs=[proof])

    def test_new_extreme_requires_prior_known_reference(self):
        proof = replace(self.proof, kind="NEW_EXTREME", reference_ticks=119, reference_known_at=100)
        self.assertEqual(self.rating(proofs=[proof])["components"]["new_extreme"], 10)
        for change in (replace(proof, reference_known_at=101), replace(proof, reference_ticks=120)):
            with self.assertRaises(ValueError):
                self.rating(proofs=[change])

    def test_short_contact_is_symmetric(self):
        origin = replace(self.origin, open=90, high=100, low=80, close=85)
        touch = replace(self.touch, open=90, high=100, low=80, close=85)
        result = self.rating(level=replace(self.level, source_field="high"), bars=[origin, touch],
                             proofs=[replace(self.proof, side="RESISTANCE")])
        self.assertEqual(result["score"], self.rating()["score"])

    def test_overlap_d1_w1_is_allowed_and_future_confirmation_excluded(self):
        weekly = SourceBar("weekly", "FIXTURE", "1w", 0, 700, 110, 120, 101, 115)
        proof = Proof("W1", "CROSS_TF", "weekly", "SUPPORT", 700, 700, "synthetic-reviewer", "APPROVED")
        result = self.rating(bars=[self.origin, weekly], proofs=[proof])
        self.assertEqual(result["components"]["cross_tf"], 5)
        prefix = self.rating(bars=[self.origin, weekly], proofs=[proof], as_of=699)
        self.assertEqual(prefix["score"], 25)
        self.assertEqual(prefix["excluded_future_event_ids"], ["W1"])

    def test_cross_tf_requires_distinct_tf_and_inclusive_tolerance(self):
        weekly = replace(self.touch, bar_id="weekly", timeframe="1w", low=102)
        proof = replace(self.proof, event_id="W1", kind="CROSS_TF", source_bar_id="weekly")
        self.assertEqual(self.rating(bars=[self.origin, weekly], proofs=[proof])["components"]["cross_tf"], 5)
        with self.assertRaises(ValueError):
            self.rating(bars=[self.origin, replace(weekly, low=103)], proofs=[proof])

    def test_duplicate_records_and_formation_reuse_rejected(self):
        for proofs in ([self.proof, self.proof], [self.proof, replace(self.proof, event_id="copy")],
                       [replace(self.proof, source_bar_id="origin")]):
            with self.assertRaises(ValueError):
                self.rating(proofs=proofs)

    def test_unreviewed_invalid_or_unavailable_levels_have_no_score(self):
        for level in (replace(self.level, state="INVALID_LIMIT"), replace(self.level, known_at=1001)):
            self.assertIsNone(self.rating(level=level)["score"])
        with self.assertRaises(ValueError):
            self.rating(level=replace(self.level, review_decision="PENDING"))

    def test_source_identity_price_and_causality_rejected(self):
        for level in (replace(self.level, price_ticks=101), replace(self.level, formed_at=99)):
            with self.assertRaises(ValueError):
                self.rating(level=level)
        with self.assertRaises(ValueError):
            self.rating(proofs=[replace(self.proof, known_at=199)])

    def test_pre_availability_reaction_cannot_be_rebranded_strengthening(self):
        old = replace(self.touch, start=50, end=150)
        with self.assertRaises(ValueError):
            self.rating(bars=[self.origin, old])

    def test_future_extension_preserves_as_of_score(self):
        future = replace(self.touch, bar_id="future", start=1000, end=1100)
        proof = replace(self.proof, event_id="future", source_bar_id="future", known_at=1100, reviewed_at=1100)
        result = self.rating(bars=[self.origin, self.touch, future], proofs=[self.proof, proof])
        self.assertEqual(result["score"], self.rating()["score"])

    def test_evidence_caps_and_round_bonus_cannot_exceed_one_hundred(self):
        bars, proofs = [self.origin], []
        for i in range(20):
            name = str(i)
            bar = replace(self.touch, bar_id=name, start=100+i*100, end=200+i*100,
                          low=99 if i >= 6 else 100)
            bars.append(bar)
            proofs.append(replace(self.proof, event_id=name, source_bar_id=name,
                                  kind="FALSE_BREAKOUT" if i >= 6 else "TOUCH",
                                  known_at=bar.end, reviewed_at=bar.end))
        proofs.append(replace(proofs[-1], event_id="new-extreme", kind="NEW_EXTREME",
                              reference_ticks=119, reference_known_at=100))
        policy = replace(self.policy, round_step_ticks=25, round_policy_provenance="synthetic-grid")
        result = self.rating(level=replace(self.level, primary_type="TREND_BREAK"),
                             bars=bars, proofs=proofs, policy=policy, as_of=3000)
        self.assertEqual(result["score"], 100)
        self.assertEqual(result["components"]["false_breakouts"], 15)


if __name__ == "__main__":
    unittest.main()
