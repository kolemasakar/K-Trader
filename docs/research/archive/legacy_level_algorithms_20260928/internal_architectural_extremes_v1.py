"""Conservative, causal D1/W1 structural-extreme selection.

BOS candidates: a confirmed swing high/low is structurally qualified only
after a later CLOSED bar breaks its high/low respectively. This records
breakout anchors, NOT an entry or a claim that every break is a trend change.
CHoCH and trading-channel boundary identification need separate stateful
definitions and are NOT silently inferred here. Close confirms the break;
the level price always comes from the original candle HIGH/LOW.
"""
def select_break_anchors(bars, pivots):
    eligible=[]
    by_open={b["t"]:i for i,b in enumerate(bars)}
    for p in pivots:
        if p["tf"] not in ("1d","1w"):raise ValueError("D1/W1 only")
        j=by_open.get(p["pivot_open_ms"])
        if j is None:raise ValueError("pivot not in timeframe bars")
        if p["kind"]=="resistance":
            assert bars[j]["h"]==p["price"],"resistance must equal pivot HIGH"
        elif p["kind"]=="support":
            assert bars[j]["l"]==p["price"],"support must equal pivot LOW"
        else:raise ValueError("invalid kind")
        for b in bars[j+1:]:
            if b["close_t"]<=p["confirmed_close_ms"]:continue
            broke=b["c"]>p["price"] if p["kind"]=="resistance" else b["c"]<p["price"]
            if broke:
                x=dict(p);x["confirmed_close_ms"]=b["close_t"]
                x["pivot_confirmed_close_ms"]=p["confirmed_close_ms"]
                x["structural_reason"]="CONFIRMED_SWING_BREAK_ANCHOR"
                x["break_close_ms"]=b["close_t"]
                eligible.append(x)
                break
    return eligible

def select_dual_tf(daily,weekly,d1_pivots,w1_pivots):
    return select_break_anchors(daily,d1_pivots)+select_break_anchors(weekly,w1_pivots)
