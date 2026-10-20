"""Adapter to existing Gerchik research detector, not a reimplementation.

Source: scripts/research/gerchik_seven_types_v0_1.py from
research/dual-market-historical-levels-v0-1.
The referenced detector accepts ONLY continuous UTC 24/7 data.
Do not silently reuse it for NYSE/Nasdaq sessions.
"""
from importlib import import_module

class ExistingLevelEngineUnavailable(RuntimeError):
    pass

def detect_existing_levels(rows, timeframe, policy, *, asset_class, calendar):
    if timeframe not in ("D1", "W1"):
        raise ExistingLevelEngineUnavailable("D1/W1 required")
    if (asset_class, calendar) not in (("crypto", "UTC_CONTINUOUS_24_7"), ("us_equity", "US_EQUITY_SESSION_WALL_CLOCK")):
        raise ExistingLevelEngineUnavailable(
            "unsupported asset/calendar pair")
    try:
        engine = import_module("scripts.research.gerchik_seven_types_v0_1")
    except ImportError as exc:
        raise ExistingLevelEngineUnavailable(
            "merge/cherry-pick approved existing detector dependencies before use") from exc
    if not isinstance(policy, engine.ResearchPolicy) or policy.calendar != calendar:
        raise ExistingLevelEngineUnavailable("existing ResearchPolicy required")
    return engine.detect_all(rows, timeframe, policy)
