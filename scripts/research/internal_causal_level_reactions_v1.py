"""Causal, internal-only D1/W1 level reaction diagnostics.

No ATR, lower-timeframe level creation, trade signals, or external holdout.
Rebuild as-of zones from only already-confirmed pivots at each D1 close.
"""
from collections import defaultdict

def same_event_key(pivot, daily_bars):
    """Group weekly and daily pivots only if same kind and weekly extreme
    occurs at daily pivot price within the weekly pivot's seven UTC days."""
    if pivot["tf"] == "1d":
        return (pivot["kind"], pivot["pivot_open_ms"], pivot["price"])
    week_start = pivot["pivot_open_ms"]
    matches = [b for b in daily_bars if week_start <= b["t"] < week_start + 7*86400000
               and b["h" if pivot["kind"] == "resistance" else "l"] == pivot["price"]]
    return (pivot["kind"], matches[0]["t"], pivot["price"]) if matches else (
        pivot["kind"], week_start, pivot["price"], "W1_UNMATCHED")

def independent_events(pivots, daily_bars):
    events=defaultdict(list)
    for p in pivots:
        events[same_event_key(p,daily_bars)].append(p)
    return events

def causal_reactions(daily, pivots, cluster_fn, horizon=5, band=.003):
    """One observation per zone per as-of date, at first post-formation touch.

    Touch is on next closed D1 bar only; outcomes are measured on subsequent
    closed D1 bars, never the touching bar (unknown intrabar ordering).
    A reaction is descriptive displacement >=1% from zone center within
    horizon days, not a tradable P&L or entry rule.
    """
    if horizon < 1: raise ValueError("horizon must be positive")
    seen=set()
    out=[]
    for i in range(len(daily)-horizon-1):
        as_of=daily[i]["close_t"]
        known=[p for p in pivots if p["confirmed_close_ms"]<=as_of]
        zones=cluster_fn(known,as_of,relative_band=band)
        next_bar=daily[i+1]
        for zone in zones:
            center=zone["center"]
            if center<=0:continue
            # Do not retrospectively credit a future pivot to an older zone.
            key=(zone["kind"],tuple(sorted(
                (p["tf"],p["pivot_open_ms"],p["confirmed_close_ms"],p["price"])
                for p in known if p["kind"]==zone["kind"]
                and zone["low"]<=p["price"]<=zone["high"])))
            if key in seen:continue
            touch=(next_bar["l"]<=center*(1+band)
                   and next_bar["h"]>=center*(1-band))
            if not touch:continue
            seen.add(key)
            future=daily[i+2:i+2+horizon]
            if len(future)<horizon:continue
            if zone["kind"]=="support":
                reaction=max(b["h"] for b in future)/center-1
            else:
                reaction=1-min(b["l"] for b in future)/center
            out.append({"known_ms":as_of,"touch_close_ms":next_bar["close_t"],
                        "kind":zone["kind"],"center":center,
                        "reaction_1pct":reaction>=.01,
                        "max_favorable_move":reaction})
    return out
