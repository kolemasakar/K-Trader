"""Research-only HISTORICAL candidate discovery from *upstream-qualified* D1/W1 extrema.

This is NOT a pivot qualifier: it refuses unqualified extrema, never confirms levels,
and does not infer intrabar touch order.
"""
from collections import defaultdict
from decimal import Decimal
from .gerchik_cross_tf_v0_1 import _utc
from .gerchik_structural_review_gate_v0_1 import verify_reviewed_extremum


def historical_candidates(items, as_of, min_independent=2):
    """Public entrypoint: accepts complete source-bar/review bundles, never bare events."""
    events = []
    source_intervals = {}
    for item in items:
        if not isinstance(item, dict) or set(item) != {'event', 'source_bar', 'review'}:
            raise ValueError('Complete event/source_bar/review bundle required')
        event = verify_reviewed_extremum(item['event'], item['source_bar'], item['review'], as_of)
        bar = item['source_bar']
        if not bar.get('opened_at'):
            raise ValueError('Source bar opened_at required for cross-timeframe independence')
        start, end = _utc(bar['opened_at']), _utc(bar['closed_at'])
        if start >= end:
            raise ValueError('Invalid source bar interval')
        if not start <= _utc(event['observed_at']):
            raise ValueError('Noncausal source bar')
        source_intervals[(event['symbol'], event['event_id'])] = (start, end)
        events.append(event)
    if not isinstance(min_independent, int) or min_independent < 2:
        raise ValueError('Require at least two independent qualified events')
    cutoff = _utc(as_of)
    groups = defaultdict(list)
    seen = set()
    for e in events:
        required = ('symbol', 'timeframe', 'source_field', 'price', 'tick_size',
                    'observed_at', 'event_id', 'source_bar_id', 'structural_qualification')
        if any(k not in e for k in required):
            raise ValueError('Missing upstream event provenance')
        if e['timeframe'] not in ('1d', '1w') or e['source_field'] not in ('high', 'low'):
            raise ValueError('D1/W1 HIGH/LOW only')
        if e['structural_qualification'] != 'INDEPENDENT_REVIEW_VERIFIED':
            raise ValueError('Raw/unqualified pivot not permitted')
        observed = _utc(e['observed_at'])
        if observed > cutoff:
            continue
        price, tick = Decimal(str(e['price'])), Decimal(str(e['tick_size']))
        if not price.is_finite() or not tick.is_finite() or tick <= 0 or price <= 0 or price / tick != (price / tick).to_integral_value():
            raise ValueError('Invalid exact tick price')
        identity = (e['symbol'], e['event_id'])
        if not e['symbol'] or not e['event_id'] or not e['source_bar_id']:
            raise ValueError('Empty provenance')
        if identity in seen:
            raise ValueError('Duplicate event ID')
        seen.add(identity)
        groups[(e['symbol'], price)].append(e)
    result = []
    for (symbol, price), group in sorted(groups.items()):
        # Different TF bar IDs do not prove independent physical market events.
        # Conservatively reject groups containing any overlapping source intervals.
        intervals = [(e, source_intervals[(e['symbol'], e['event_id'])]) for e in group]
        if any(a['source_bar_id'] == b['source_bar_id'] or
               (start_a < end_b and start_b < end_a)
               for i, (a, (start_a, end_a)) in enumerate(intervals)
               for b, (start_b, end_b) in intervals[i + 1:]):
            continue
        independent = {e['source_bar_id'] for e in group}
        if len(independent) < min_independent:
            continue
        result.append({'symbol': symbol, 'price': str(price), 'type': 'HISTORICAL',
                       'state': 'CANDIDATE', 'qualification': 'UPSTREAM_REQUIRED',
                       'event_ids': sorted(e['event_id'] for e in group),
                       'independent_bar_count': len(independent),
                       'available_at': max(_utc(e['observed_at']) for e in group).isoformat()})
    return result
