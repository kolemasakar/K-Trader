"""Research-only provenance verification of externally reviewed structural extrema.

This does not claim automatic BOS/CHoCH detection. Review approval is an
explicit independent input; source OHLC and review timestamps are verified.
"""
from decimal import Decimal
from .gerchik_cross_tf_v0_1 import _utc


def verify_reviewed_extremum(event, source_bar, review, as_of):
    cutoff = _utc(as_of)
    required = ('event_id', 'symbol', 'timeframe', 'source_field', 'source_bar_id',
                'price', 'tick_size', 'observed_at')
    if any(not event.get(k) for k in required):
        raise ValueError('Incomplete event provenance')
    if event['timeframe'] not in ('1d', '1w') or event['source_field'] not in ('high', 'low'):
        raise ValueError('D1/W1 HIGH/LOW only')
    if any(not source_bar.get(k) for k in ('bar_id', 'symbol', 'timeframe', 'closed_at')):
        raise ValueError('Incomplete bar provenance')
    if (source_bar['bar_id'], source_bar['symbol'], source_bar['timeframe']) != (
            event['source_bar_id'], event['symbol'], event['timeframe']):
        raise ValueError('Source bar identity mismatch')
    if (review.get('event_id'), review.get('reviewer_id')) == (None, None) or not review.get('reviewer_id'):
        raise ValueError('Independent reviewer required')
    if review.get('event_id') != event['event_id'] or review.get('decision') != 'APPROVED':
        raise ValueError('Matching affirmative review required')
    bar_closed = _utc(source_bar['closed_at'])
    observed = _utc(event['observed_at'])
    reviewed = _utc(review['reviewed_at'])
    if observed < bar_closed or reviewed < observed or reviewed > cutoff:
        raise ValueError('Noncausal event or review')
    price, tick = Decimal(str(event['price'])), Decimal(str(event['tick_size']))
    source_price = Decimal(str(source_bar[event['source_field']]))
    if not all(x.is_finite() for x in (price, tick, source_price)) or price <= 0 or tick <= 0:
        raise ValueError('Invalid price or tick')
    if price != source_price or price / tick != (price / tick).to_integral_value():
        raise ValueError('Extremum mismatch or off-tick price')
    return {**event, 'structural_qualification': 'INDEPENDENT_REVIEW_VERIFIED',
            'observed_at': reviewed.isoformat(),
            'reviewer_id': review['reviewer_id'],
            'reviewed_at': reviewed.isoformat()}
