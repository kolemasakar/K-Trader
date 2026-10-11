import sys
import unittest
from dataclasses import replace
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts" / "research"))
from gerchik_strategy_patterns_v0_1 import LevelContext, Parameters, TickBar, detect
from gerchik_execution_v0_1 import Bar, Config, simulate


def bars(rows):
    return [TickBar(i*100, (i+1)*100, *row) for i, row in enumerate(rows)]


class PatternTests(unittest.TestCase):
    def setUp(self):
        self.level = LevelContext("FIXTURE", 100, "1", "1d", "HISTORICAL", -100,
                                  "CONFIRMED", "synthetic-formation", "synthetic-admission")
        self.p = Parameters("synthetic-candidate-v1", "synthetic-not-market-parameters", 100,
                            2, 2, 1, 1, "DIRECTIONAL_CLOSE", 6, "RETEST_BAR", 2, 4, 5,
                            20, 50, "FIRST_CLOSE", "CLOSE_SIDE", "LOCAL_EXTREME", 6, None)
        self.fixtures = {
            "S1": [(104, 107, 102, 105), (105, 107, 100, 103), (103, 108, 101, 107)],
            "S2": [(98, 100, 96, 99), (99, 105, 98, 104), (104, 109, 103, 108)],
            "S3": [(98, 100, 96, 99), (99, 105, 98, 104), (101, 106, 100, 105)],
            "S4": [(104, 107, 102, 105), (105, 107, 97, 104)],
            "S5": [(104, 107, 102, 105), (105, 106, 96, 98),
                   (98, 99, 94, 97), (97, 105, 96, 103)],
            "S6": [(100, 110, 95, 100)]*50+[(110, 125, 109, 120)],
        }

    def run_pattern(self, sid, rows=None, **kwargs):
        sequence = bars(self.fixtures[sid] if rows is None else rows)
        return detect(sid, kwargs.pop("side", "LONG"), kwargs.pop("level", self.level),
                      sequence, kwargs.pop("parameters", self.p),
                      as_of=kwargs.pop("as_of", sequence[-1].end if sequence else 0))

    def test_six_long_and_short_families(self):
        expected = {"S1": 99, "S2": 99, "S3": 99, "S4": 96, "S5": 93, "S6": 94}
        for sid, rows in self.fixtures.items():
            with self.subTest(sid=sid):
                result = self.run_pattern(sid)
                self.assertEqual(result["status"], "CANDIDATE")
                self.assertEqual(result["setup"].stop, expected[sid])
                mirrored = [(200-o, 200-l, 200-h, 200-c) for o, h, l, c in rows]
                short = self.run_pattern(sid, mirrored, side="SHORT")
                self.assertEqual(short["status"], "CANDIDATE")
                self.assertEqual(short["setup"].stop, 200-expected[sid])

    def test_s1_exact_first_touch_and_separate_second_tolerance(self):
        rows = list(self.fixtures["S1"])
        rows[1] = (105, 107, 101, 103)
        self.assertEqual(self.run_pattern("S1", rows)["status"], "NO_PATTERN")
        rows = list(self.fixtures["S1"])
        rows[2] = (103, 108, 102, 107)
        self.assertEqual(self.run_pattern("S1", rows)["status"], "NO_PATTERN")

    def test_s2_break_threshold_inclusive_and_continuation_required(self):
        rows = [(98, 100, 96, 99), (99, 103, 98, 102), (102, 106, 101, 105)]
        self.assertEqual(self.run_pattern("S2", rows)["status"], "CANDIDATE")
        strict = replace(self.p, confirmation_policy="CLOSE_BEYOND_PREVIOUS_EXTREME")
        self.assertEqual(self.run_pattern("S2", rows, parameters=strict)["status"], "CANDIDATE")
        boundary = rows[:-1]+[(102, 106, 101, 103)]
        self.assertEqual(self.run_pattern("S2", boundary, parameters=strict)["status"], "NO_PATTERN")
        rows[-1] = (100, 106, 100, 101)
        self.assertEqual(self.run_pattern("S2", rows)["status"], "NO_PATTERN")

    def test_s3_six_bar_window_and_stop_level_not_retest_extreme(self):
        prefix = self.fixtures["S3"][:2]
        waiting = [(104, 108, 103, 105)]
        retest = [(101, 107, 101, 106)]
        result = self.run_pattern("S3", prefix+waiting*5+retest)
        self.assertEqual(result["status"], "CANDIDATE")
        self.assertEqual(result["setup"].stop, 99)
        self.assertEqual(self.run_pattern("S3", prefix+waiting*6+retest)["status"], "NO_PATTERN")

    def test_s3_next_bar_resume_does_not_backdate_availability(self):
        rows = self.fixtures["S3"]+[(105, 110, 104, 109)]
        result = self.run_pattern("S3", rows, parameters=replace(self.p, s3_resume_policy="NEXT_BAR"))
        self.assertEqual(result["setup"].known_at, 400)
        self.assertEqual(result["evidence"]["bar_starts"], [100, 200, 300])

    def test_s4_penetration_boundary_and_return_required(self):
        rows = [(104, 107, 102, 105), (105, 107, 98, 104)]
        self.assertEqual(self.run_pattern("S4", rows)["status"], "CANDIDATE")
        rows[-1] = (105, 107, 99, 104)
        self.assertEqual(self.run_pattern("S4", rows)["status"], "NO_PATTERN")
        rows[-1] = (105, 107, 97, 99)
        self.assertEqual(self.run_pattern("S4", rows)["status"], "NO_PATTERN")

    def test_s5_overlong_structure_is_not_truncated_to_pass(self):
        rows = [self.fixtures["S5"][0]]+[(99, 101, 94, 98)]*5+[(98, 105, 96, 103)]
        self.assertEqual(self.run_pattern("S5", rows)["status"], "NO_PATTERN")
        variant = replace(self.p, s5_max_outside=5, s5_max_structure_bars=6)
        self.assertEqual(self.run_pattern("S5", rows, parameters=variant)["status"], "CANDIDATE")

    def test_s6_prior_range_excludes_signal_and_atr_branch_explicit(self):
        self.assertEqual(self.run_pattern("S6")["status"], "CANDIDATE")
        self.assertEqual(self.run_pattern("S6", parameters=replace(self.p, s6_trend_policy="EMA_SLOPE"))["status"], "CANDIDATE")
        p = replace(self.p, s6_stop_mode="ATR_DISTANCE", s6_atr_stop_ticks=15)
        self.assertEqual(self.run_pattern("S6", parameters=p)["setup"].stop, 105)
        with self.assertRaises(ValueError):
            self.run_pattern("S6", parameters=replace(p, s6_atr_stop_ticks=None))

    def test_level_known_before_formation_is_mandatory(self):
        result = self.run_pattern("S4", level=replace(self.level, known_at=150))
        self.assertEqual(result["status"], "LEVEL_UNAVAILABLE_AT_PATTERN_START")
        for change in (replace(self.level, state="CANDIDATE"), replace(self.level, known_at=201)):
            self.assertEqual(self.run_pattern("S4", level=change)["status"], "LEVEL_UNAVAILABLE")

    def test_future_and_gap_are_rejected(self):
        with self.assertRaises(ValueError):
            self.run_pattern("S4", as_of=199)
        sequence = bars(self.fixtures["S4"])
        sequence[1] = replace(sequence[1], start=101, end=201)
        with self.assertRaises(ValueError):
            detect("S4", "LONG", self.level, sequence, self.p, as_of=201)

    def test_more_history_can_only_use_completed_inputs(self):
        for sid in self.fixtures:
            self.assertEqual(self.run_pattern(sid)["setup"].known_at, len(self.fixtures[sid])*100)

    def test_tick_scaling_and_simulator_handoff(self):
        result = self.run_pattern("S4", level=replace(self.level, tick_size="0.1"))
        self.assertEqual(result["setup"].stop, 9.6)
        setup = self.run_pattern("S4")["setup"]
        result = simulate(setup, [Bar(200, 300, 104, 112, 103, 111)],
                          Config(1, 1, 100, 0, 0, 0, "synthetic-costs"))
        self.assertEqual((result["status"], result["gross_r"]), ("TARGET", 1))

    def test_bad_params_and_cold_start_explicit(self):
        for p in (replace(self.p, stop_buffer_ticks=0), replace(self.p, breakout_ticks=True),
                  replace(self.p, parameter_provenance="")):
            with self.assertRaises(ValueError):
                self.run_pattern("S1", parameters=p)
        self.assertEqual(self.run_pattern("S6", self.fixtures["S6"][:50])["status"], "INSUFFICIENT_HISTORY")


if __name__ == "__main__":
    unittest.main()
