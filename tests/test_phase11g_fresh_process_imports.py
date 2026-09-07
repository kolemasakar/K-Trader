from __future__ import annotations

from pathlib import Path
import subprocess
import sys

import pytest


ROOT = Path(__file__).resolve().parents[1]


def _run_fresh(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, *args],
        cwd=ROOT,
        capture_output=True,
        text=True,
        timeout=30,
        check=False,
    )


def test_replay_can_import_before_lazy_outcome_sample_exports() -> None:
    result = _run_fresh(
        "-c",
        (
            "from ktrader.replay import ReplayStudyConfig, ReplayStudyContext; "
            "from ktrader.outcomes import build_outcome_sample, OutcomeSample; "
            "assert ReplayStudyConfig is not None; "
            "assert ReplayStudyContext is not None; "
            "assert callable(build_outcome_sample); "
            "assert OutcomeSample is not None"
        ),
    )
    assert result.returncode == 0, result.stderr


@pytest.mark.parametrize(
    "script",
    (
        "scripts/run_replay_study.py",
        "scripts/build_study_cohort.py",
        "scripts/build_dataset_catalogue.py",
        "scripts/export_outcome_sample.py",
    ),
)
def test_phase11g_cli_help_imports_in_fresh_process(script: str) -> None:
    result = _run_fresh(str(ROOT / script), "--help")
    assert result.returncode == 0, result.stderr
    assert "usage:" in result.stdout.lower()
