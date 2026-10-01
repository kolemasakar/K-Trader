"""Research-only iterative five-accepted-bar ATR5; newest-to-oldest CLOSED bars.

Owner rule: start with five closed bars, compare all five against their
current mean, replace one abnormal bar with the next older unused bar,
recompute and recheck all five until none is abnormal.
Tie-breaking when several bars are abnormal: replace the newest first.
"""
from dataclasses import dataclass
from math import isfinite

class InsufficientHistory(ValueError):
    pass

@dataclass(frozen=True)
class DailyBar:
    timestamp: str
    high: float
    low: float

    @property
    def span(self):
        if not (isfinite(self.high) and isfinite(self.low) and self.high > self.low):
            raise ValueError(f"Invalid D1 high/low at {self.timestamp}")
        return self.high - self.low

def filtered_atr5(closed_bars, max_lookback=250):
    """Caller supplies only completed bars, newest first; no live/future bars."""
    if isinstance(max_lookback, bool) or not isinstance(max_lookback, int) or max_lookback < 5:
        raise ValueError("max_lookback must be an integer >= 5")
    bars = list(closed_bars[:max_lookback])
    if len(bars) < 5:
        raise InsufficientHistory("At least five completed D1 bars required")
    spans = [bar.span for bar in bars]
    if len({bar.timestamp for bar in bars}) != len(bars):
        raise ValueError("Duplicate timestamps")
    if any(bars[i].timestamp <= bars[i+1].timestamp for i in range(len(bars)-1)):
        raise ValueError("Bars must be newest-to-oldest")
    selected = list(range(5))
    next_older = 5
    rejected = []
    while True:
        mean = sum(spans[i] for i in selected) / 5
        abnormal = next(((position, i, "LARGE" if spans[i] >= 2 * mean else "SMALL")
                         for position, i in enumerate(selected)
                         if spans[i] >= 2 * mean or spans[i] <= mean / 3), None)
        if abnormal is None:
            return dict(atr5=mean,
                        accepted=[dict(timestamp=bars[i].timestamp, range=spans[i],
                                       reference=mean) for i in selected],
                        rejected=rejected,
                        inspected=next_older,
                        reference_policy="iterative-five-selected-recheck-v2")
        position, index, reason = abnormal
        if next_older >= len(bars):
            raise InsufficientHistory("Insufficient older closed bars to replace abnormal bar")
        rejected.append(dict(timestamp=bars[index].timestamp, range=spans[index],
                             reference=mean, reason=reason))
        selected[position] = next_older
        selected.sort()
        next_older += 1
