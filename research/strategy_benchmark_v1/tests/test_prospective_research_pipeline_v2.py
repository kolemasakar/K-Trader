from __future__ import annotations

import json
import pathlib
import subprocess
import sys
import tempfile
import unittest


HERE = pathlib.Path(__file__).resolve().parents[1]
RUNNER = HERE / "run_prospective_research_pipeline_v2.py"


class ProspectivePipelineV2Tests(unittest.TestCase):
    def test_plan_contains_all_guard_stages(self):
        with tempfile.TemporaryDirectory() as td:
            root = pathlib.Path(td)
            prior = root / "prior"
            prior.mkdir()
            (prior / "observations.jsonl").write_text("{}\n")
            base = root / "base"
            base.mkdir()
            manifests = root / "manifests"
            completed = subprocess.run(
                [
                    sys.executable,
                    str(RUNNER),
                    "--as-of",
                    "2026-09-16T16:30:00Z",
                    "--prior-outcomes",
                    str(prior),
                    "--base",
                    str(base),
                    "--manifest-dir",
                    str(manifests),
                ],
                text=True,
                capture_output=True,
            )
            self.assertEqual(completed.returncode, 0, completed.stderr)
            report = json.loads((manifests / "pipeline_v2_20260916T163000Z_plan.json").read_text())
            self.assertEqual(report["status"], "PLAN_ONLY")
            self.assertFalse(report["holdout_opened"])
            self.assertFalse(report["production_action"])
            self.assertEqual(
                [stage["stage"] for stage in report["stages"]],
                [
                    "capture",
                    "funding",
                    "resolver",
                    "post30",
                    "statistics",
                    "evidence",
                    "portfolio_risk",
                    "state_manifest",
                ],
            )

    def test_missing_prior_fails_closed(self):
        with tempfile.TemporaryDirectory() as td:
            root = pathlib.Path(td)
            completed = subprocess.run(
                [
                    sys.executable,
                    str(RUNNER),
                    "--as-of",
                    "2026-09-16T16:30:00Z",
                    "--prior-outcomes",
                    str(root / "missing-prior"),
                    "--base",
                    str(root / "base"),
                    "--manifest-dir",
                    str(root / "manifests"),
                ],
                text=True,
                capture_output=True,
            )
            self.assertNotEqual(completed.returncode, 0)
            self.assertIn("PRIOR_OUTCOMES_MISSING", completed.stderr + completed.stdout)


if __name__ == "__main__":
    unittest.main()
