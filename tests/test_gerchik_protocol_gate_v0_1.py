import copy
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts" / "research"))
from gerchik_protocol_gate_v0_1 import FAMILIES, audit_protocol, fingerprint


def fixture():
    return {
        "schema": "ktrader.gerchik.protocol.v0.1", "code_commit": "a" * 40, "target_r": 1,
        "data": {"inventory_sha256": "b" * 64, "symbols": ["BTCUSDT"],
                 "start_ms": 1000, "end_ms": 10000},
        "study": {"start_ms": 2000, "end_ms": 9000, "warmup_policy": "fixture",
                  "claim": "EXPLORATORY"},
        "levels": {"atr_used": False, "atr_diagnostic": "ITERATIVE_D1_ATR5_V2",
                   "ledger_sha256": "c" * 64, "specification_sha256": "d" * 64,
                   "tolerance_anchor": "fixture", "tick_rounding": "fixture",
                   "causal_known_at_policy": "fixture", "entry_precision": "fixture",
                   "week_policy": "COMPLETE_UTC_MON_SUN_FROM_D1"},
        "strategies": [{"id": sid, "family": family, "executable_spec_sha256": "e" * 64,
                        "unresolved": [], "parameter_migration": "fixture",
                        "stop_basis": "BEYOND_LEVEL"} for sid, family in FAMILIES.items()],
        "execution": {"entry": "NEXT_OPEN", "collision_policy": "AMBIGUOUS",
                      "interval_ms": 100, "horizon_bars": 2, "fee_rate": 0,
                      "adverse_fill_cost": 0, "funding_cost_per_unit": 0,
                      "cost_provenance": "synthetic", "funding_estimate_policy": "synthetic",
                      "overlap_policy": "fixture", "calendar_metadata": "fixture",
                      "cost_basis": "DECLARED_PROXY"},
        "resources": {"archive_read_only": True, "free_only": True, "memory_mb": 128,
                      "timeout_seconds": 30, "output_location": "fixture-output"},
    }


class ProtocolTests(unittest.TestCase):
    def test_complete_is_declaration_not_verification(self):
        m = fixture()
        original = copy.deepcopy(m)
        result = audit_protocol(m)
        self.assertEqual(result["status"], "DECLARATIONS_COMPLETE")
        self.assertEqual(result["artifact_verification"], "NOT_PERFORMED")
        self.assertEqual(m, original)

    def test_empty_and_malformed_have_diagnostics(self):
        for m in (None, [], {}, {"strategies": [{"id": []}], "study": {"claim": {}},
                               "execution": {"cost_basis": {}, "collision_policy": []}}):
            self.assertEqual(audit_protocol(m)["status"], "BLOCKED")

    def test_duplicate_strategy_and_wrong_family(self):
        m = fixture()
        m["strategies"][1] = copy.deepcopy(m["strategies"][0])
        self.assertIn("SIX_UNIQUE_STRATEGIES", audit_protocol(m)["blockers"])
        m = fixture()
        m["strategies"][1]["family"] = "BREAKOUT_RETEST"
        self.assertIn("S2_IDENTITY", audit_protocol(m)["blockers"])

    def test_s3_stop_and_unresolved_confirmation(self):
        m = fixture()
        m["strategies"][2]["stop_basis"] = "RETEST_EXTREME"
        m["strategies"][0]["unresolved"] = ["confirmation"]
        blockers = audit_protocol(m)["blockers"]
        self.assertIn("S3_STOP_BEYOND_LEVEL", blockers)
        self.assertIn("S1_UNRESOLVED_PARAMETERS", blockers)

    def test_atr_geometry_rejected(self):
        m = fixture()
        m["levels"]["atr_used"] = True
        self.assertIn("ATR_FREE_LEVELS", audit_protocol(m)["blockers"])

    def test_partial_week_policy_rejected(self):
        m = fixture()
        m["levels"]["week_policy"] = "RAW_PARTIAL_W1"
        self.assertIn("CLOSED_W1_POLICY", audit_protocol(m)["blockers"])

    def test_costs_cannot_be_silently_omitted(self):
        m = fixture()
        del m["execution"]["funding_cost_per_unit"]
        self.assertIn("COST_FUNDING_COST_PER_UNIT", audit_protocol(m)["blockers"])
        m["execution"]["fee_rate"] = float("nan")
        self.assertIn("FINITE_JSON_REQUIRED", audit_protocol(m)["blockers"])

    def test_bool_is_not_numeric_horizon(self):
        m = fixture()
        m["execution"]["horizon_bars"] = True
        self.assertIn("EXECUTION_HORIZON_BARS", audit_protocol(m)["blockers"])

    def test_study_must_stay_in_cohort(self):
        m = fixture()
        m["study"]["end_ms"] = 10001
        self.assertIn("STUDY_BOUNDARIES_AND_WARMUP", audit_protocol(m)["blockers"])

    def test_inspected_control_cannot_be_independent(self):
        m = fixture()
        m["study"].update(claim="INDEPENDENT_VALIDATION", holdout={
            "previously_inspected": True, "reservation_sha256": "f" * 64,
            "reservation_provenance": "already-inspected-fixture"})
        self.assertIn("UNTOUCHED_CONTROL_EVIDENCE", audit_protocol(m)["blockers"])

    def test_three_r_requires_completed_comparable_one_r(self):
        m = fixture()
        digest = fingerprint(m)
        m["target_r"] = 3
        self.assertEqual(fingerprint(m), digest)
        self.assertIn("MATCHING_COMPLETED_1R_REQUIRED", audit_protocol(m)["blockers"])
        m["prior_1r"] = {"target_r": 1, "status": "COMPLETED", "report_sha256": "f" * 64,
                         "comparison_sha256": digest}
        self.assertEqual(audit_protocol(m)["status"], "DECLARATIONS_COMPLETE")
        m["execution"]["fee_rate"] = .001
        self.assertIn("MATCHING_COMPLETED_1R_REQUIRED", audit_protocol(m)["blockers"])

    def test_deterministic_hash_includes_unknown_extension(self):
        m = fixture()
        self.assertEqual(fingerprint(m), fingerprint(dict(reversed(list(m.items())))))
        changed = copy.deepcopy(m)
        changed["additional_assumption"] = "changed"
        self.assertNotEqual(fingerprint(m), fingerprint(changed))


if __name__ == "__main__":
    unittest.main()
