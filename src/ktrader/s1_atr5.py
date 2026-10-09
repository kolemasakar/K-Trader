"""Deterministic filtered daily ATR5 for S1 research; completed D1 only.

The reference is computed from the latest five eligible completed D1 ranges.
Each iteration rejects a range outside (mean/3, 2*mean), substitutes
the nearest preceding candidate and repeats. Fail closed if no stable set.
"""
from decimal import Decimal

class ATRUnavailable(ValueError):
    pass

def filtered_atr5(completed_bars, *, lookback_limit=250):
    ranges=[Decimal(str(x["high"]))-Decimal(str(x["low"])) for x in completed_bars]
    if len(ranges)<5: raise ATRUnavailable("insufficient completed D1")
    if any(x<0 for x in ranges): raise ATRUnavailable("invalid D1 range")
    candidates=list(reversed(ranges[-lookback_limit:]))
    chosen=[]
    for value in candidates:
        chosen.append(value)
        if len(chosen)<5: continue
        while len(chosen)>5: chosen.pop()
        reference=sum(chosen)/5
        if reference<=0: raise ATRUnavailable("nonpositive reference")
        bad=[i for i,x in enumerate(chosen) if x>=2*reference or x<=reference/3]
        if not bad: return reference
        # Remove only one abnormal candidate, preserving newest-to-oldest order.
        chosen.pop(bad[0])
    raise ATRUnavailable("no stable five normal daily bars within bounded lookback")
