from __future__ import annotations

import ctypes
import importlib.util
from pathlib import Path

import pytest


_SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "run_readonly_research.py"
_SPEC = importlib.util.spec_from_file_location("run_readonly_research", _SCRIPT)
assert _SPEC is not None and _SPEC.loader is not None
launcher = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(launcher)


def test_reject_same_archive_and_result_directory(tmp_path, monkeypatch):
    (tmp_path / "dataset_summary.json").write_text('{"panel_size": 19}')
    monkeypatch.setattr(launcher.os, "geteuid", lambda: 1002)
    with pytest.raises(ValueError, match="must not overlap"):
        launcher.validate_paths(tmp_path, tmp_path)


def test_reject_nested_results_even_if_user_can_write(tmp_path, monkeypatch):
    archive = tmp_path / "archive"
    archive.mkdir()
    (archive / "dataset_summary.json").write_text('{"panel_size": 19}')
    results = archive / "results"
    results.mkdir()
    monkeypatch.setattr(launcher.os, "geteuid", lambda: 1002)
    with pytest.raises(ValueError, match="must not overlap"):
        launcher.validate_paths(archive, results)


def test_reject_source_from_world_writable_tmp(tmp_path, monkeypatch):
    archive = tmp_path / "archive"
    archive.mkdir()
    (archive / "dataset_summary.json").write_text('{"panel_size": 19}')
    results = tmp_path / "results"
    results.mkdir()
    monkeypatch.setattr(launcher.os, "geteuid", lambda: 1002)
    with pytest.raises(ValueError, match="reserve /tmp"):
        launcher.validate_paths(archive, results)


def test_landlock_rights_cover_source_write_truncate_and_remove():
    assert launcher._WRITE_RIGHTS & (1 << 1)  # WRITE_FILE
    assert launcher._WRITE_RIGHTS & (1 << 4)  # REMOVE_DIR
    assert launcher._WRITE_RIGHTS & (1 << 5)  # REMOVE_FILE
    assert launcher._WRITE_RIGHTS & (1 << 14)  # TRUNCATE


def test_syscall_error_fails_closed(monkeypatch):
    monkeypatch.setattr(ctypes, "get_errno", lambda: 1)
    with pytest.raises(PermissionError, match="landlock"):
        launcher._checked(-1, "landlock_create_ruleset")
