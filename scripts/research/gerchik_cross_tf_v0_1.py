"""Read-only cross-timeframe association of independently formed D1/W1 candidates.
No automatic confirmation, detector, or cross-timeframe primary-type reassignment.
"""
from collections import defaultdict
from decimal import Decimal
from datetime import datetime, timezone


def _utc(value):
    dt = datetime.fromisoformat(value.replace('Z', '+00:00'))
    if dt.tzinfo is None or dt.utcoffset().total_seconds() != 0:
        raise ValueError('UTC timestamp required')
    return dt.astimezone(timezone.utc)


def associate(levels, as_of):
    """Group visible candidates by exact symbol + decimal price, preserving source TF."""
    cutoff = _utc(as_of)
    grouped = defaultdict(list)
    for level in levels:
        if level.state != 'CANDIDATE':
            raise ValueError('Only unconfirmed research candidates supported')
        if level.timeframe not in ('1d', '1w'):
            raise ValueError('Only D1/W1 sources supported')
        if _utc(level.formed_at) > cutoff:
            continue
        price = Decimal(level.price)
        tick = Decimal(level.tick_size)
        if not price.is_finite() or not tick.is_finite() or tick <= 0 or price / tick != (price / tick).to_integral_value():
            raise ValueError('Invalid exact tick identity')
        grouped[(level.symbol, price)].append(level)
    output = []
    for (symbol, price), records in sorted(grouped.items()):
        frames = {x.timeframe for x in records}
        output.append({'symbol': symbol, 'price': str(price),
                       'timeframes': sorted(frames),
                       'cross_tf': frames == {'1d', '1w'},
                       'candidates': [{'timeframe': x.timeframe,
                                       'primary_type': x.primary_type,
                                       'formed_at': x.formed_at,
                                       'formation_event_id': x.formation_event_id}
                                      for x in sorted(records, key=lambda x: (x.formed_at, x.timeframe))],
                       'state': 'CANDIDATE_ONLY'})
    return output
