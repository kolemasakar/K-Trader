"""Research-only causal filtered D1 ATR(5). Input: newest-to-oldest CLOSED D1 bars.
Rolling reference is an explicit experimental choice, not a book-prescribed formula.
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
    """Caller must supply completed bars only. Never fetch future or live bars."""
    if not isinstance(max_lookback, int) or max_lookback < 5:
        raise ValueError("max_lookback must be an integer >= 5")
    bars = list(closed_bars[:max_lookback])
    if len(bars) < 5:
        raise InsufficientHistory("At least five completed D1 bars required")
    spans = [bar.span for bar in bars]
    if len({bar.timestamp for bar in bars}) != len(bars):
        raise ValueError("Duplicate timestamps")
    if any(bars[i].timestamp <= bars[i + 1].timestamp for i in range(len(bars) - 1)):
        raise ValueError("Bars must be newest-to-oldest")
    accepted, rejected = [], []
    def reference(i):
        if i + 5 > len(bars):
            raise InsufficientHistory("Insufficient older completed bars for reference")
        return sum(spans[i:i + 5]) / 5
    def verdict(i, ref):
        return ("LARGE" if spans[i] >= 2 * ref else
                "SMALL" if spans[i] <= ref / 3 else "NORMAL")
    start = None
    for i in range(len(bars) - 4):
        ref = reference(i)
        reason = verdict(i, ref)
        item = dict(timestamp=bars[i].timestamp, range=spans[i], reference=ref)
        if reason == "NORMAL":
            start = i
            accepted.append(item)
            break
        rejected.append(dict(**item, reason=reason))
    if start is None:
        raise InsufficientHistory("No normal bootstrap bar within lookback")
    # Experimental reference: candidate + four immediately older closed bars.
    # No already-accepted newer bar enters the candidate's reference.
    for i in range(start + 1, len(bars) - 4):
        if len(accepted) == 5:
            break
        ref = reference(i)
        reason = verdict(i, ref)
        item = dict(timestamp=bars[i].timestamp, range=spans[i], reference=ref)
        if reason == "NORMAL":
            accepted.append(item)
        else:
            rejected.append(dict(**item, reason=reason))
    if len(accepted) != 5:
        raise InsufficientHistory("Fewer than five normal bars within lookback")
    return dict(atr5=sum(item["range"] for item in accepted) / 5,
                accepted=accepted, rejected=rejected,
                inspected=len(accepted) + len(rejected),
                reference_policy="five-consecutive-candidate-inclusive-v1")
