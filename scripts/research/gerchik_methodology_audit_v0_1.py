"""Second implementation of witness checks, NOT an independent reviewer.

Does not import/call detection or rating code. Checks research archetypes only;
no numeric hypothesis is promoted to an author rule or approved market policy.
"""
from decimal import Decimal, ROUND_CEILING


def witness_check(rows, level, policy):
    checks = {}
    try:
        s, e = level['source_index'], level['confirmation_index']
        p = Decimal(level['price'])
        kind, side = level['primary_type'], level['side']
        field = 2 if level['source_field'] == 'high' else 3
        w = level['witness_indices']
        checks['indices'] = (type(s) is int and type(e) is int and 0 <= s <= e < len(rows)
                             and all(type(i) is int and 0 <= i <= e for i in w)
                             and len(set(w)) == len(w) and s in w and e in w)
        if not checks['indices']:
            return {'status':'REJECTED','checks':checks}
        b = [tuple(map(Decimal,r[1:5])) for r in rows[:e+1]]
        checks['ohlc'] = all(all(v.is_finite() and v > 0 for v in x)
                            and x[2] <= min(x[0],x[3]) <= max(x[0],x[3]) <= x[1] for x in b)
        checks['source'] = (Decimal(rows[s][field]) == p and rows[s][0] == level['source_open_ms']
                            and level['source_field'] in ('high','low'))
        checks['chronology'] = (rows[e][6]+1 == level['known_at_ms']
                                and all(rows[i][6]+1 <= level['known_at_ms'] for i in w)
                                and all(a[6]+1 == z[0] for a,z in zip(rows[:e],rows[1:e+1])))
        checks['witness_bytes'] = ('witness_bars' not in level or
                                   level['witness_bars'] == [rows[i] for i in w])
        checks['side'] = side in ('SUPPORT','RESISTANCE')
        inside = lambda v, role: v > p if role == 'SUPPORT' else v < p
        opposite = 'RESISTANCE' if side == 'SUPPORT' else 'SUPPORT'

        def contact(i, role):
            x = b[i]
            if not inside(x[3],role): return None
            boundary = x[2] if role == 'SUPPORT' else x[1]
            if boundary == p: return 'TOUCH'
            if inside(x[0],role) and (boundary < p if role == 'SUPPORT' else boundary > p):
                return 'FALSE_BREAKOUT'
            return None

        def structure(origin, role):
            k = policy['directional_transitions']
            sign = 1 if role == 'RESISTANCE' else -1
            if not k <= origin <= e-k: return False
            if not all(sign*(b[j][1]-b[j-1][1]) > 0 and sign*(b[j][2]-b[j-1][2]) > 0
                       for j in range(origin-k+1,origin+1)): return False
            if not all(sign*(b[j][1]-b[j-1][1]) < 0 and sign*(b[j][2]-b[j-1][2]) < 0
                       for j in range(origin+1,origin+k+1)): return False
            reference = min(x[2] for x in b[origin-k:origin+1]) if sign == 1 else max(x[1] for x in b[origin-k:origin+1])
            for j in range(origin+k,e+1):
                if (b[j][1] > p if sign == 1 else b[j][2] < p): return False
                if (b[j][2] < reference if sign == 1 else b[j][1] > reference): return True
            return False

        valid = False
        if kind == 'LIMIT':
            valid = e == s+2 and all(Decimal(rows[j][field]) == p for j in range(s,e+1))
        elif kind == 'CONSOLIDATION':
            valid = (e-s-1 >= 3 and Decimal(rows[e][field]) == p and
                     all(Decimal(rows[j][field]) < p if side == 'RESISTANCE'
                         else Decimal(rows[j][field]) > p for j in range(s+1,e)))
        elif kind == 'TREND_BREAK':
            valid = (structure(s,side) and
                     all(not inside(b[j][3],opposite) and inside(b[j][3],side) for j in range(s+1,e+1))
                     and sum(contact(j,side) is not None for j in range(s+1,e+1)) >= policy['trend_defenses'])
        elif kind == 'HISTORICAL':
            points = {j for j in range(e+1) for role,index in (('SUPPORT',2),('RESISTANCE',1))
                      if b[j][index] == p and structure(j,role)}
            valid = len(points) >= policy['historical_repetitions']
        elif kind == 'MIRROR':
            old = opposite
            breaks = [j for j in range(s+1,e) if inside(b[j][3],side)]
            if breaks:
                first = breaks[0]
                valid = (contact(s,old) is not None and
                         sum(contact(j,old) is not None for j in range(s,first)) >= policy['mirror_defenses']
                         and all(inside(b[j][3],side) for j in range(first,e+1))
                         and inside(b[e][0],side) and contact(e,side) == 'TOUCH')
        elif kind == 'PARANORMAL_BAR':
            n = policy['paranormal_reference_bars']
            if s >= n:
                mean = sum((x[1]-x[2] for x in b[s-n:s]),Decimal(0))/n
                contacts = {contact(j,side) for j in range(s+1,e+1)}
                valid = (mean > 0 and b[s][1]-b[s][2] >= Decimal(policy['paranormal_multiple'])*mean
                         and {'TOUCH','FALSE_BREAKOUT'} <= contacts
                         and all(inside(b[j][3],side) for j in range(s+1,e+1)))
        elif kind == 'GAP' and len(w) >= 3:
            a,z = w[0:2]
            up = z == a+1 and b[a][1] < b[z][2] and p in (b[a][1],b[z][2]) and side=='SUPPORT'
            down = z == a+1 and b[z][1] < b[a][2] and p in (b[a][2],b[z][1]) and side=='RESISTANCE'
            valid = ((up or down) and e > z and contact(e,side) is not None
                     and all(inside(b[j][3],side) for j in range(z+1,e+1)))
        checks['archetype'] = valid
    except (KeyError, IndexError, TypeError, ValueError, ArithmeticError):
        checks['malformed'] = False
    return dict(status='SECOND_IMPLEMENTATION_PASS' if all(checks.values()) else 'REJECTED',
                checks=checks, independent_human_review='NOT_PERFORMED',
                scope='RESEARCH_ARCHETYPE_NOT_BOOK_SEMANTIC_APPROVAL')


def contextual_zone(price, asset_class, *, anchor_price, anchor_known_at_ms,
                    as_of_ms, forex_point_size, tick_size, radius_rounding, provenance):
    """Explicit symmetric zone mathematics; caller must approve anchor/rounding.

    Raw mathematical zones can be inspected without pretending tick compliance.
    Radius CEILING is supported only as an explicitly supplied research choice.
    """
    p = Decimal(price)
    if not provenance or not p.is_finite() or p <= 0:
        raise ValueError('positive source price and provenance required')
    if (type(anchor_known_at_ms) is not int or type(as_of_ms) is not int
            or anchor_known_at_ms > as_of_ms):
        raise ValueError('causal explicit anchor required')
    if asset_class == 'FOREX':
        point = Decimal(forex_point_size) if forex_point_size is not None else Decimal(0)
        if not point.is_finite() or point <= 0: raise ValueError('broker point convention required')
        radius = 3*point
    elif asset_class == 'GOLD': radius = Decimal('0.15')
    elif asset_class == 'OIL': radius = Decimal('0.03')
    elif asset_class in ('CRYPTO','EQUITY'):
        if anchor_price is None: raise ValueError('percentage anchor required')
        anchor = Decimal(anchor_price)
        if not anchor.is_finite() or anchor <= 0: raise ValueError('positive percentage anchor required')
        radius = anchor*Decimal('0.0004')
    else: raise ValueError('unknown instrument class')
    rounded = False
    if radius_rounding == 'CEILING':
        if tick_size is None: raise ValueError('explicit tick size required for rounding')
        tick = Decimal(tick_size)
        if not tick.is_finite() or tick <= 0 or p/tick != (p/tick).to_integral_value():
            raise ValueError('invalid tick or off-tick source')
        radius = (radius/tick).to_integral_value(rounding=ROUND_CEILING)*tick
        rounded = True
    elif radius_rounding != 'RAW': raise ValueError('explicit supported radius policy required')
    return dict(price=str(p),radius=str(radius),lower=str(p-radius),upper=str(p+radius),
                significance='EQUAL_THROUGHOUT',anchor_price=anchor_price,
                anchor_known_at_ms=anchor_known_at_ms,rounding=radius_rounding,
                tick_rounded=rounded,provenance=provenance,status='MATHEMATICAL_POLICY_PREVIEW')
