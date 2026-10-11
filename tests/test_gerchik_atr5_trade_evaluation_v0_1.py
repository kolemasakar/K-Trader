"""Deterministic geometry/causality tests, not profitability evidence."""
from datetime import datetime, timedelta, timezone
import unittest

from scripts.research.gerchik_atr5_trade_evaluation_v0_1 import ClosedDailyBar, evaluate_trade


def bars(ranges):
    end = datetime(2026, 10, 1, tzinfo=timezone.utc)
    return [ClosedDailyBar((end-timedelta(days=i+1)).isoformat(),
                           (end-timedelta(days=i)).isoformat(), 100+span, 100)
            for i, span in enumerate(ranges)]


def run(ranges, **changes):
    args = dict(cutoff="2026-10-01T00:00:00Z", direction="LONG", entry=100,
                stop=98, target=106, source_id="synthetic-fixture")
    args.update(changes)
    return evaluate_trade(bars(ranges), **args)


class TradeEvaluationTests(unittest.TestCase):
    def test_long_and_short_symmetric(self):
        long = run([10]*15)
        short = run([10]*15, direction="SHORT", stop=102, target=94)
        self.assertEqual(long["canonical"], short["canonical"])
        self.assertEqual(long["geometry"]["gross_rr"], 3)
        self.assertEqual(long["canonical"]["metrics"]["target_distance_atr5"], .6)

    def test_anomaly_replacement_and_provenance(self):
        report = run([40, 10, 10, 1]+[10]*12)
        self.assertEqual(report["canonical"]["atr5"], 10)
        self.assertEqual([r["reason"] for r in report["canonical"]["calculation"]["rejected"]], ["LARGE", "SMALL"])
        self.assertEqual(report["canonical"]["quality"]["inspected_bars"], 7)

    def test_irrelevant_older_history_preserves_canonical_result(self):
        self.assertEqual(run([10]*5)["canonical"], run([10]*5+[200, 1])["canonical"])

    def test_future_and_naive_cutoffs_rejected(self):
        for cutoff in ["2026-09-30T23:59:59Z", "2026-10-01T00:00:00"]:
            with self.assertRaises(ValueError):
                run([10]*15, cutoff=cutoff)

    def test_mixed_timezone_duplicate_source_rejected(self):
        data = bars([10]*5)
        data[1] = ClosedDailyBar("2026-09-30T03:00:00+03:00", data[1].closed_at, 110, 100)
        with self.assertRaises(ValueError):
            evaluate_trade(data, cutoff="2026-10-01T00:00:00Z", direction="LONG",
                           entry=100, stop=98, target=106, source_id="fixture")

    def test_bad_geometry_and_values_rejected(self):
        for changes in [dict(stop=101), dict(target=99), dict(entry=float("nan")),
                        dict(stop=True), dict(source_id=""), dict(current_session_range=-1),
                        dict(max_lookback=True), dict(include_v3=1)]:
            with self.assertRaises(ValueError):
                run([10]*15, **changes)

    def test_v2_survives_short_v3_history(self):
        report = run([10]*5, include_v3=True)
        self.assertEqual(report["canonical"]["atr5"], 10)
        self.assertIsNone(report["experimental_v3"]["calculation"]["atr5"])

    def test_warmup_cannot_replace_v2_or_disable_analysis(self):
        baseline = run([30]*3+[10]*20)
        comparison = run([30]*3+[10]*20, include_v3=True)
        self.assertEqual(baseline["canonical"], comparison["canonical"])
        self.assertEqual(comparison["experimental_v3"]["calculation"]["status"], "NEW_REGIME_WARMUP")
        self.assertIsNone(comparison["experimental_v3"]["metrics"])
        self.assertNotIn("trade_allowed", comparison)

    def test_insufficient_preserves_geometry_without_inventing_atr(self):
        report = run([10]*4)
        self.assertEqual(report["canonical"]["status"], "INSUFFICIENT_HISTORY")
        self.assertIsNone(report["canonical"]["metrics"])
        self.assertEqual(report["geometry"]["gross_rr"], 3)

    def test_session_range_is_unclipped_descriptive_ratio(self):
        report = run([10]*15, current_session_range=25)
        self.assertEqual(report["canonical"]["metrics"]["session_range_atr5"], 2.5)
        self.assertNotIn("remaining_energy", report["canonical"]["metrics"])

    def test_inputs_immutable_and_v3_opt_in(self):
        data = bars([10]*15)
        original = list(data)
        report = evaluate_trade(data, cutoff="2026-10-01T00:00:00Z", direction="LONG",
                                entry=100, stop=98, target=106, source_id="fixture")
        self.assertEqual(original, data)
        self.assertNotIn("experimental_v3", report)


if __name__ == "__main__":
    unittest.main()
