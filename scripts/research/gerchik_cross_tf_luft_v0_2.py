"""Research D1/W1 cross-timeframe confirmation within approved symmetric luft.

Only independently qualified upstream formation events can confirm. Luft is
provided by upstream stop policy (20% BaseStop, tick-rounded); ATR is not used here.
"""
from decimal import Decimal
from .gerchik_cross_tf_v0_1 import _utc


def confirm_pairs(levels, as_of, luft_by_symbol):
    cutoff = _utc(as_of)
    eligible = []
    for level in levels:
        if level.timeframe not in ('1d', '1w'):
            raise ValueError('D1/W1 only')
        if level.state != 'CANDIDATE':
            raise ValueError('Expected unconfirmed formation candidate')
        if _utc(level.formed_at) > cutoff:
            continue
        price, tick = Decimal(level.price), Decimal(level.tick_size)
        if not price.is_finite() or not tick.is_finite() or tick <= 0 or price <= 0:
            raise ValueError('Invalid price/tick')
        if price / tick != (price / tick).to_integral_value():
            raise ValueError('Off-tick candidate')
        if not getattr(level, 'structurally_qualified', False):
            continue
        eligible.append(level)
    result = []
    for symbol in sorted({x.symbol for x in eligible}):
        if symbol not in luft_by_symbol:
            raise ValueError('Missing approved upstream luft for symbol')
        luft = Decimal(str(luft_by_symbol[symbol]))
        if not luft.is_finite() or luft < 0:
            raise ValueError('Invalid luft')
        daily = [x for x in eligible if x.symbol == symbol and x.timeframe == '1d']
        weekly = [x for x in eligible if x.symbol == symbol and x.timeframe == '1w']
        for d in daily:
            matches = [w for w in weekly if abs(Decimal(d.price) - Decimal(w.price)) <= luft
                       and w.formation_event_id != d.formation_event_id]
            # Avoid claiming unique confirmation if several weekly candidates overlap.
            if len(matches) != 1:
                continue
            w = matches[0]
            reciprocal = [other for other in daily
                          if abs(Decimal(other.price) - Decimal(w.price)) <= luft
                          and other.formation_event_id != w.formation_event_id]
            if len(reciprocal) != 1:
                continue
            result.append({
                'symbol': symbol, 'd1_price': str(d.price), 'w1_price': str(w.price),
                'distance': str(abs(Decimal(d.price) - Decimal(w.price))),
                'luft': str(luft), 'cross_tf_confirmed': True,
                'confirmed_at': max(_utc(d.formed_at), _utc(w.formed_at)).isoformat(),
                'events': [d.formation_event_id, w.formation_event_id],
                'primary_types': [d.primary_type, w.primary_type],
                'price_policy': 'retain_both_source_prices_no_midpoint',
            })
    return result
