"""Experimental ATR5 v3: confirmed three-bar volatility-regime adaptation.

Research-only; never replaces owner-approved v2 or emits trading signals.
Newest-first CLOSED DailyBar inputs. No future observations.
"""
from statistics import median
from .gerchik_filtered_atr5_v1 import DailyBar, filtered_atr5, InsufficientHistory

def adaptive_atr5_v3(closed_bars, *, confirmation=3, baseline_window=10,
                     regime_ratio=2.0, max_lookback=250):
    if confirmation != 3 or baseline_window < 5 or regime_ratio <= 1:
        raise ValueError("Research v3 requires three-bar confirmation and valid baseline")
    bars = list(closed_bars[:max_lookback])
    if len(bars) < confirmation + baseline_window:
        return dict(status="BASELINE_INSUFFICIENT", atr5=None, regime_confirmed=False)
    # Reuse v2's fail-closed input checks, including chronology and positive spans.
    # Validation here covers the entire selected historical window.
    spans = [bar.span for bar in bars]
    if len({bar.timestamp for bar in bars}) != len(bars) or any(
            bars[i].timestamp <= bars[i+1].timestamp for i in range(len(bars)-1)):
        raise ValueError("Unique newest-to-oldest timestamps required")
    recent = median(spans[:confirmation])
    baseline = median(spans[confirmation:confirmation+baseline_window])
    ratio = recent / baseline
    direction = "EXPANSION" if ratio >= regime_ratio else (
        "CONTRACTION" if ratio <= 1/regime_ratio else None)
    # Three bars must all individually support the direction; one spike
    # among normal bars does not constitute a new regime.
    confirmed = direction is not None and all(
        (v >= baseline * regime_ratio if direction == "EXPANSION"
         else v <= baseline / regime_ratio) for v in spans[:confirmation])
    if not confirmed:
        try:
            result = filtered_atr5(bars, max_lookback=max_lookback)
        except InsufficientHistory:
            return dict(status="V2_INSUFFICIENT", atr5=None, regime_confirmed=False)
        return dict(status="V2_BASELINE", atr5=result["atr5"],
                    regime_confirmed=False, v2=result)
    # Extend contiguous new-regime bars backwards. Compare to the frozen
    # baseline, not to the inflated mean of the mixed five-bar window.
    segment = 0
    for span in spans:
        if (span >= baseline * regime_ratio if direction == "EXPANSION"
                else span <= baseline / regime_ratio):
            segment += 1
        else:
            break
    if segment < 5:
        return dict(status="NEW_REGIME_WARMUP", atr5=None, regime_confirmed=True,
                    direction=direction, regime_bars=segment, baseline=baseline)
    # No borrowing from the old regime. For this exploratory version, five
    # most recent coherent bars define the new-regime estimate directly.
    chosen = bars[:5]
    return dict(status="NEW_REGIME_READY", atr5=sum(x.span for x in chosen)/5,
                regime_confirmed=True, direction=direction, regime_bars=segment,
                baseline=baseline, accepted=[x.timestamp for x in chosen],
                estimator="mean-of-five-new-regime-bars-experimental")
