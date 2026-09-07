from __future__ import annotations

from argparse import Namespace
from datetime import datetime, timezone
import importlib.util
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


def _load_script_module(name: str, relative_path: str):
    path = ROOT / relative_path
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


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


def test_replay_cli_exposes_and_preserves_window_bounds() -> None:
    result = _run_fresh(str(ROOT / "scripts/run_replay_study.py"), "--help")
    assert result.returncode == 0, result.stderr
    assert "--start" in result.stdout
    assert "--end" in result.stdout

    module = _load_script_module("run_replay_study_cli", "scripts/run_replay_study.py")
    start = module._utc("2026-09-05T14:45:00Z")
    end = module._utc("2026-09-05T16:00:00+00:00")
    config = module._build_study_config(
        Namespace(step_bars=1, horizon_bars=24, start=start, end=end)
    )

    assert config.start == datetime(2026, 9, 5, 14, 45, tzinfo=timezone.utc)
    assert config.end == datetime(2026, 9, 5, 16, 0, tzinfo=timezone.utc)
    assert config.step_bars == 1
    assert config.horizon_bars == 24


def test_replay_cli_rejects_non_utc_window_bounds() -> None:
    module = _load_script_module("run_replay_study_cli_invalid", "scripts/run_replay_study.py")
    with pytest.raises(Exception):
        module._utc("2026-09-05T14:45:00+03:00")
