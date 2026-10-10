"""Causal research-only trade geometry diagnostics. Never emits trade decisions.

Canonical v2 is computed independently. Optional v3 is a labelled comparison;
it cannot replace v2, alter levels/stops/targets or create a volatility gate.
"""
from dataclasses import dataclass
from datetime import datetime, timezone
from math import isfinite

from .gerchik_filtered_atr5_v1 import (
    DailyBar, InsufficientHistory, atr5_quality_diagnostic, filtered_atr5,
)
from .gerchik_adaptive_atr5_v3_experiment import adaptive_atr5_v3


@dataclass(frozen=True)
class ClosedDailyBar:
    """Explicit availability time; timestamp identifies the source D1 candle."""
    timestamp: str
    closed_at: str
    high: float
    low: float


def _utc(value):
    stamp = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if stamp.tzinfo is None or stamp.utcoffset() is None:
        raise ValueError("Timezone-aware timestamp required")
    return stamp.astimezone(timezone.utc)


def _positive(value, name):
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not isfinite(value) or value <= 0:
        raise ValueError(f"{name} must be positive and finite")


def evaluate_trade(closed_bars, *, cutoff, direction, entry, stop, target,
                   source_id, current_session_range=None, include_v3=False,
                   max_lookback=250):
    """Describe caller-supplied technical geometry using only available D1 bars.

    Inputs must be newest first. Future bars are rejected, never silently sliced.
    closed_at is the instant the bar becomes available (not its open time).
    Caller verifies source D1 completeness and supplies technical SL/TP; this
    function neither builds levels nor evaluates entry-pattern confirmation.
    current_session_range is optional as-of high-low, not a directional budget.
    """
    asof = _utc(cutoff)
    if direction not in {"LONG", "SHORT"}:
        raise ValueError("direction must be LONG or SHORT")
    if not isinstance(source_id, str) or not source_id.strip():
        raise ValueError("source_id required for data provenance")
    if not isinstance(include_v3, bool):
        raise ValueError("include_v3 must be boolean")
    if isinstance(max_lookback, bool) or not isinstance(max_lookback, int) or max_lookback < 5:
        raise ValueError("max_lookback must be an integer >= 5")
    for name, value in (("entry", entry), ("stop", stop), ("target", target)):
        _positive(value, name)
    if not (stop < entry < target if direction == "LONG" else target < entry < stop):
        raise ValueError("Invalid directional stop/entry/target geometry")
    if current_session_range is not None:
        if isinstance(current_session_range, bool) or not isinstance(current_session_range, (int, float)) or not isfinite(current_session_range) or current_session_range < 0:
            raise ValueError("current_session_range must be nonnegative and finite")
    rows = list(closed_bars)
    prepared = []
    previous_source = previous_close = None
    for bar in rows:
        source, available = _utc(bar.timestamp), _utc(bar.closed_at)
        if source >= available or available > asof:
            raise ValueError("D1 bar must open before its close and be available at cutoff")
        if previous_source is not None and (source >= previous_source or available >= previous_close):
            raise ValueError("Unique newest-to-oldest source and close timestamps required")
        if previous_source is not None and available > previous_source:
            raise ValueError("Overlapping D1 bars")
        prepared_bar = DailyBar(source.isoformat(), bar.high, bar.low)
        _positive(prepared_bar.span, "D1 range")
        prepared.append(prepared_bar)
        previous_source, previous_close = source, available
    risk, reward = abs(entry - stop), abs(target - entry)
    report = dict(
        schema_version="ktrader.atr5_trade_evaluation.v0.1",
        scope="RESEARCH_ONLY_NO_TRADE_DECISION", cutoff=asof.isoformat(),
        source_id=source_id, input_bars=len(rows), max_lookback=max_lookback,
        latest_closed_at=rows[0].closed_at if rows else None,
        geometry=dict(direction=direction, entry=entry, stop=stop, target=target,
                      risk_distance=risk, target_distance=reward, gross_rr=reward/risk),
    )
    try:
        result = filtered_atr5(prepared, max_lookback=max_lookback)
    except InsufficientHistory as exc:
        report["canonical"] = dict(status="INSUFFICIENT_HISTORY", atr5=None, reason=str(exc),
                                   metrics=None, policy="iterative-five-selected-recheck-v2")
    else:
        atr = result["atr5"]
        metrics = dict(stop_distance_atr5=risk/atr, target_distance_atr5=reward/atr,
                       session_range_atr5=None if current_session_range is None else current_session_range/atr)
        report["canonical"] = dict(status="READY", atr5=atr, metrics=metrics,
                                   calculation=result, quality=atr5_quality_diagnostic(result))
    if include_v3:
        experimental = adaptive_atr5_v3(prepared, max_lookback=max_lookback)
        estimate = experimental["atr5"]
        report["experimental_v3"] = dict(
            approval="NOT_APPROVED_FOR_TRADING", calculation=experimental,
            metrics=None if estimate is None else dict(stop_distance_atr5=risk/estimate,
                                                       target_distance_atr5=reward/estimate),
        )
    return report
