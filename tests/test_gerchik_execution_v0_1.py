import sys
import unittest
from dataclasses import replace
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts" / "research"))
from gerchik_execution_v0_1 import Bar, Config, Setup, simulate


class ExecutionTests(unittest.TestCase):
    def setUp(self):
        self.setup = Setup("S3", "fixture-only", 1000, 900, "closed-D1-fixture", "LONG", 90)
        self.config = Config(1, 2, 100, 0, 0, 0, "explicit-zero-cost-fixture")
        self.first = Bar(1000, 1100, 100, 105, 95, 102)

    def run_case(self, bars, setup=None, config=None):
        return simulate(setup or self.setup, bars, config or self.config)

    def test_long_target(self):
        result = self.run_case([replace(self.first, high=110)])
        self.assertEqual((result["status"], result["net_r"]), ("TARGET", 1))

    def test_short_three_r(self):
        result = self.run_case([Bar(1000, 1100, 100, 105, 70, 80)],
                               replace(self.setup, side="SHORT", stop=110),
                               replace(self.config, target_r=3))
        self.assertEqual(result["net_r"], 3)

    def test_cost_normalization(self):
        result = self.run_case([replace(self.first, high=110)], config=replace(
            self.config, fee_rate=.001, adverse_fill_cost=.1, funding_cost_per_unit=.09))
        self.assertAlmostEqual(result["net_r"], .95)

    def test_gap_loss_worse_than_one_r(self):
        result = self.run_case([self.first, Bar(1100, 1200, 85, 89, 80, 86)])
        self.assertEqual((result["status"], result["gross_r"]), ("STOP_GAP", -1.5))

    def test_target_gap_conservative(self):
        result = self.run_case([self.first, Bar(1100, 1200, 115, 120, 114, 118)])
        self.assertEqual((result["status"], result["gross_r"]), ("TARGET_GAP", 1))

    def test_collision_is_not_win(self):
        bar = replace(self.first, high=115, low=85)
        result = self.run_case([bar])
        self.assertEqual(result["status"], "AMBIGUOUS")
        self.assertIsNone(result["net_r"])
        sensitivity = self.run_case([bar], config=replace(self.config, collision_policy="STOP_FIRST"))
        self.assertEqual(sensitivity["net_r"], -1)

    def test_censored_and_pending(self):
        self.assertEqual(self.run_case([self.first])["status"], "CENSORED")
        self.assertEqual(self.run_case([])["status"], "PENDING_ENTRY")

    def test_time_exit(self):
        result = self.run_case([self.first, Bar(1100, 1200, 102, 106, 99, 105)])
        self.assertEqual((result["status"], result["gross_r"]), ("TIME_EXIT", .5))

    def test_noncausal_level_rejected(self):
        with self.assertRaises(ValueError):
            self.run_case([], setup=replace(self.setup, level_known_at=1001))

    def test_gaps_and_prior_bars_rejected(self):
        for start in (900, 1001):
            with self.assertRaises(ValueError):
                self.run_case([replace(self.first, start=start)])

    def test_bad_prices_and_config_rejected(self):
        for bar in (replace(self.first, high=float("nan")), replace(self.first, low=103)):
            with self.assertRaises(ValueError):
                self.run_case([bar])
        for config in (replace(self.config, target_r=2), replace(self.config, cost_provenance="")):
            with self.assertRaises(ValueError):
                self.run_case([], config=config)

    def test_entry_gap_invalidates_stop(self):
        self.assertEqual(self.run_case([replace(self.first, open=89, low=85)])["status"],
                         "INVALID_ENTRY_GEOMETRY")

    def test_future_extension_does_not_change_closed_trade(self):
        first = replace(self.first, high=110)
        self.assertEqual(self.run_case([first]), self.run_case(
            [first, Bar(1100, 1200, 85, 89, 80, 86)]))


if __name__ == "__main__":
    unittest.main()
