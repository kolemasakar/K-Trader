import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("phase11g_causal_runner", ROOT / "scripts" / "phase11g_causal_runner.py")
mod = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
SPEC.loader.exec_module(mod)


def test_m15_alignment_and_tags():
    t = mod.parse_utc("2026-09-17T01:15:00Z")
    assert mod.is_m15(t)
    assert mod.tag(t) == "20260917T011500Z"
    assert mod.iso(t) == "2026-09-17T01:15:00Z"


def test_reject_non_m15():
    t = mod.parse_utc("2026-09-17T01:17:00Z")
    assert not mod.is_m15(t)


def test_latest_closed_respects_lag():
    now = mod.parse_utc("2026-09-17T01:15:10Z")
    assert mod.iso(mod.latest_closed(now, 30)) == "2026-09-17T01:00:00Z"
    now2 = mod.parse_utc("2026-09-17T01:15:40Z")
    assert mod.iso(mod.latest_closed(now2, 30)) == "2026-09-17T01:15:00Z"
