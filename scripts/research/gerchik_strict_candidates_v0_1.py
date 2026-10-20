"""Strict causal research subset; raw Decimal prices, no tick or review approval.

LIMIT: three consecutive equal extrema. CONSOLIDATION: an extremum,
at least three strictly one-sided bars, then an exact confirming extremum.
The latter is a conservative engineering subset of the book description.
Same-price/TF identity retains its earliest type; simultaneous types ambiguous.
"""
from decimal import Decimal


def formations(rows, timeframe, *, session_calendar=False):
    """All causal formation episodes; an ongoing LIMIT run emits once."""
    previous = None
    for r in rows:
        o, h, l, c = map(Decimal, r[1:5])
        if not all(x.is_finite() and x > 0 for x in (o, h, l, c)):
            raise ValueError('nonpositive or nonfinite price')
        if not l <= min(o, c) <= max(o, c) <= h or r[6] < r[0]:
            raise ValueError('invalid candle')
        if previous is not None and (r[0] <= previous if session_calendar else r[0] != previous + 1):
            raise ValueError('noncontiguous candles')
        previous = r[6]
    events = []
    for i, bar in enumerate(rows):
        for field, side in ((2, 'RESISTANCE'), (3, 'SUPPORT')):
            p = Decimal(bar[field])
            patterns = []
            if (i >= 2 and all(Decimal(r[field]) == p for r in rows[i-2:i+1])
                    and (i == 2 or Decimal(rows[i-3][field]) != p)):
                patterns.append(('LIMIT', i-2))
            # Nearest prior touch; any penetration terminates the interval.
            for j in range(i-1, -1, -1):
                q = Decimal(rows[j][field])
                if (field == 2 and q > p) or (field == 3 and q < p):
                    break
                if q == p:
                    if i-j-1 >= 3:
                        patterns.append(('CONSOLIDATION', j))
                    break
            if patterns:
                events.append(dict(
                    price=str(p), timeframe=timeframe, side=side,
                    primary_type=patterns[0][0] if len(patterns)==1 else 'AMBIGUOUS',
                    source_open_ms=rows[patterns[0][1]][0],
                    known_at_ms=bar[6]+1, confirmation_index=i,
                    status='RESEARCH_CANDIDATE', tick_compliance='PENDING',
                    independent_review='PENDING'))
    return events


def detect(rows, timeframe):
    found = {}
    for event in formations(rows, timeframe):
        found.setdefault(Decimal(event['price']), event)
    return list(found.values())


def inspect_later(rows, candidate):
    """Evidence only: wick penetration and close beyond are separate observations."""
    p = Decimal(candidate['price'])
    resistance = candidate['side'] == 'RESISTANCE'
    tail = rows[candidate['confirmation_index']+1:]
    field = 2 if resistance else 3
    beyond = lambda x: x > p if resistance else x < p
    touches = [r[6]+1 for r in tail if Decimal(r[field]) == p]
    penetrations = [r[6]+1 for r in tail if beyond(Decimal(r[field]))]
    closes = [r[6]+1 for r in tail if beyond(Decimal(r[4]))]
    return dict(exact_later_touches=len(touches),
                first_penetration_ms=next(iter(penetrations), None),
                first_close_beyond_ms=next(iter(closes), None))
