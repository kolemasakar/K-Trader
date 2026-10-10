"""MT4 broker-wall-clock stock D1 to legacy Gerchik detector row adapter.

The epoch is only a monotonic coordinate, NOT UTC exchange-time evidence.
Weekly candles are emitted only once a later ISO week is observed.
"""
from datetime import datetime, timezone
from decimal import Decimal

def row_from_mt4(candle):
    opened=datetime.fromisoformat(candle["open_time"])
    closed=datetime.fromisoformat(candle["close_time"])
    if opened.tzinfo or closed.tzinfo:
        raise ValueError("expect opaque naive broker-wall-clock input")
    if closed<=opened or candle.get("closed") is not True:
        raise ValueError("unclosed or invalid candle")
    def ms(t):
        return int(t.replace(tzinfo=timezone.utc).timestamp()*1000)
    return [ms(opened),str(candle["open"]),str(candle["high"]),
            str(candle["low"]),str(candle["close"]),str(candle.get("volume",0)),ms(closed)-1]

def completed_daily(candles):
    rows=[row_from_mt4(x) for x in candles]
    if any(a[6]>=b[0] for a,b in zip(rows,rows[1:])):
        raise ValueError("overlapping/unordered D1")
    return rows

def completed_weekly(candles):
    """Finalize an ISO week ONLY after first closed D1 of a subsequent week."""
    groups=[]
    for x in candles:
        t=datetime.fromisoformat(x["open_time"])
        week=t.isocalendar()[:2]
        if not groups or groups[-1][0]!=week: groups.append((week,[x]))
        else: groups[-1][1].append(x)
    result=[]
    for _, bars in groups[:-1]:
        if not bars: continue
        first,last=bars[0],bars[-1]
        o=row_from_mt4(first); z=row_from_mt4(last)
        result.append([o[0],str(first["open"]),
                       str(max(Decimal(str(b["high"])) for b in bars)),
                       str(min(Decimal(str(b["low"])) for b in bars)),
                       str(last["close"]),str(sum(Decimal(str(b.get("volume") or 0)) for b in bars)),
                       z[6]])
    return result
