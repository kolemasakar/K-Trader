"""Compatibility adapter to owner-approved ATR5 v2 (existing PR94 module).

Never implement a second ATR algorithm. Input is ascending closed MT4 D1
JSONL candles; the canonical engine consumes newest-to-oldest DailyBar.
"""
from scripts.research.gerchik_filtered_atr5_v1 import (
    DailyBar, InsufficientHistory, filtered_atr5 as owner_filtered_atr5
)

ATRUnavailable = InsufficientHistory

def filtered_atr5(completed_bars, *, lookback_limit=250):
    bars = [DailyBar(timestamp=str(x["open_time"]),
                     high=float(x["high"]), low=float(x["low"]))
            for x in reversed(completed_bars)]
    return owner_filtered_atr5(bars, max_lookback=lookback_limit)["atr5"]

def filtered_atr5_audit(completed_bars, *, lookback_limit=250):
    bars = [DailyBar(timestamp=str(x["open_time"]),
                     high=float(x["high"]), low=float(x["low"]))
            for x in reversed(completed_bars)]
    return owner_filtered_atr5(bars, max_lookback=lookback_limit)
