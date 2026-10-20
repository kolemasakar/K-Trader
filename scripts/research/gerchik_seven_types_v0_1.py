"""Causal research archetypes for seven Gerchik types, not reviewer approval.

Numeric archetype parameters are explicit project hypotheses. No raw pivot,
close-derived price, ATR, gradient, implicit tick size or trading dependency.
Structural key points require a complete directional reversal AND a new
extreme beyond the preceding leg. Trend-break additionally needs two defenses.
"""
from dataclasses import dataclass
from decimal import Decimal, ROUND_HALF_UP
from .gerchik_strict_candidates_v0_1 import formations as strict_formations
from .gerchik_level_strength_v0_1 import BASE


@dataclass(frozen=True)
class ResearchPolicy:
    provenance: str
    directional_transitions: int
    trend_defenses: int
    historical_repetitions: int
    mirror_defenses: int
    paranormal_reference_bars: int
    paranormal_multiple: str
    calendar: str

    def validate(self):
        numbers = (self.directional_transitions, self.trend_defenses,
                   self.historical_repetitions, self.mirror_defenses,
                   self.paranormal_reference_bars)
        if (not self.provenance or any(type(x) is not int or x < 2 for x in numbers)
                or self.calendar not in ('UTC_CONTINUOUS_24_7', 'US_EQUITY_SESSION_WALL_CLOCK')):
            raise ValueError('explicit research parameters and supported calendar required')
        m = Decimal(self.paranormal_multiple)
        if not m.is_finite() or m < 2:
            raise ValueError('paranormal multiple must be >=2')


def _prices(rows):
    return [tuple(map(Decimal, r[1:5])) for r in rows]


def _inside(value, price, side):
    return value > price if side == 'SUPPORT' else value < price


def _contact(bar, price, side):
    o, h, l, c = bar
    if not _inside(c, price, side):
        return None
    boundary = l if side == 'SUPPORT' else h
    if boundary == price:
        return 'TOUCH'
    penetrated = boundary < price if side == 'SUPPORT' else boundary > price
    if penetrated and _inside(o, price, side):
        return 'FALSE_BREAKOUT'
    return None


def _claim(rows, tf, price, side, kind, origin, confirmation, witnesses):
    return dict(price=str(price), timeframe=tf, side=side, type=kind,
                source_index=origin, source_open_ms=rows[origin][0],
                source_field='high' if Decimal(rows[origin][2]) == price else 'low',
                known_at_ms=rows[confirmation][6]+1,
                confirmation_index=confirmation, witness_indices=sorted(set(witnesses)))


def detect_all(rows, timeframe, policy):
    """Return earliest primary identities plus later pattern evidence.

    Simultaneously qualifying different types remain AMBIGUOUS. No base-weight
    ranking selects a primary. Every claim stores a complete causal witness.
    """
    policy.validate()
    if timeframe not in ('D1', 'W1'):
        raise ValueError('D1/W1 only')
    strict = strict_formations(rows, timeframe, session_calendar=(policy.calendar == 'US_EQUITY_SESSION_WALL_CLOCK'))  # validates OHLC and order
    step = 86400000 if timeframe == 'D1' else 604800000
    if policy.calendar == 'UTC_CONTINUOUS_24_7':
        if any(r[0] % 86400000 or r[6]+1-r[0] != step for r in rows):
            raise ValueError('complete UTC bars required')
        if timeframe == 'W1' and any((r[0]-4*86400000) % step for r in rows):
            raise ValueError('Monday-start UTC weeks required')
    else:
        if any(r[6] < r[0] for r in rows):
            raise ValueError('invalid session candle')
        if any(a[6] >= b[0] for a,b in zip(rows, rows[1:])):
            raise ValueError('non-increasing/overlapping session candles')
    prices = _prices(rows)
    claims = []
    for x in strict:
        origin = next(i for i, r in enumerate(rows) if r[0] == x['source_open_ms'])
        claims.append(_claim(rows, timeframe, Decimal(x['price']), x['side'],
                             x['primary_type'], origin, x['confirmation_index'],
                             range(origin, x['confirmation_index']+1)))
    k = policy.directional_transitions
    keypoints = []
    for i in range(k, len(rows)-k):
        for direction, field, side in ((1, 1, 'RESISTANCE'), (-1, 2, 'SUPPORT')):
            forward = all(direction*(prices[j][1]-prices[j-1][1]) > 0
                          and direction*(prices[j][2]-prices[j-1][2]) > 0
                          for j in range(i-k+1, i+1))
            reverse = all(direction*(prices[j][1]-prices[j-1][1]) < 0
                          and direction*(prices[j][2]-prices[j-1][2]) < 0
                          for j in range(i+1, i+k+1))
            if not (forward and reverse):
                continue
            reference = (min(b[2] for b in prices[i-k:i+1]) if direction == 1
                         else max(b[1] for b in prices[i-k:i+1]))
            p = prices[i][field]
            new_at = None
            for j in range(i+k, len(rows)):
                # The source must remain an extreme until structural qualification.
                if (direction == 1 and prices[j][1] > p) or (direction == -1 and prices[j][2] < p):
                    break
                if (direction == 1 and prices[j][2] < reference) or (direction == -1 and prices[j][1] > reference):
                    new_at = j
                    break
            if new_at is None:
                continue
            keypoints.append(dict(price=p, side=side, origin=i, known=new_at,
                                  start=i-k, reference=str(reference)))
            defenses = []
            for j in range(i+1, len(rows)):
                if not _inside(prices[j][3], p, side):
                    break
                if _contact(prices[j], p, side):
                    defenses.append(j)
                if len(defenses) >= policy.trend_defenses and j >= new_at:
                    claims.append(_claim(rows, timeframe, p, side, 'TREND_BREAK', i, j,
                                         list(range(i-k, new_at+1))+defenses))
                    break
    # Historical recurrence requires structurally qualified key points, never bare pivots.
    groups = {}
    for point in sorted(keypoints, key=lambda x: (x['known'], x['origin'])):
        group = groups.setdefault(point['price'], [])
        if any(x['origin'] == point['origin'] for x in group):
            continue
        group.append(point)
        if len(group) >= policy.historical_repetitions:
            witnesses = [j for x in group for j in range(x['start'], x['known']+1)]
            claims.append(_claim(rows, timeframe, point['price'], point['side'],
                                 'HISTORICAL', group[0]['origin'], point['known'], witnesses))
    # Mirror: multiple old-side defenses, then a closed break and opposite-side retest.
    for i, b in enumerate(prices):
        for field, side in ((1, 'RESISTANCE'), (2, 'SUPPORT')):
            p = b[field]
            if not _inside(b[3], p, side):
                continue
            defenses = [i]
            broken = None
            opposite = 'SUPPORT' if side == 'RESISTANCE' else 'RESISTANCE'
            for j in range(i+1, len(rows)):
                bar = prices[j]
                if broken is None:
                    if _inside(bar[3], p, opposite):
                        if len(defenses) < policy.mirror_defenses:
                            break
                        broken = j
                    elif _contact(bar, p, side):
                        defenses.append(j)
                elif not _inside(bar[3], p, opposite):
                    # Failed change of role: do not bridge over the failure.
                    break
                elif (_inside(bar[0], p, opposite)
                      and _contact(bar, p, opposite) == 'TOUCH'):
                    claims.append(_claim(rows, timeframe, p, opposite, 'MIRROR', i, j,
                                         defenses+[broken, j]))
                    break
    # Non-ATR arithmetic reference excludes the formation bar and uses only past bars.
    n = policy.paranormal_reference_bars
    multiple = Decimal(policy.paranormal_multiple)
    for i in range(n, len(rows)):
        mean = sum((b[1]-b[2] for b in prices[i-n:i]), Decimal(0))/n
        if mean <= 0 or prices[i][1]-prices[i][2] < multiple*mean:
            continue
        for field, side in ((1, 'RESISTANCE'), (2, 'SUPPORT')):
            p = prices[i][field]
            contacts = {}
            for j in range(i+1, len(rows)):
                if not _inside(prices[j][3], p, side):
                    break
                kind = _contact(prices[j], p, side)
                if kind and kind not in contacts:
                    contacts[kind] = j
                if {'TOUCH', 'FALSE_BREAKOUT'} <= contacts.keys():
                    claims.append(_claim(rows, timeframe, p, side, 'PARANORMAL_BAR', i, j,
                                         list(range(i-n, i+1))+list(contacts.values())))
                    break
    # True traded-price gap: disjoint adjacent ranges in a contiguous 24/7 series.
    # Missing bars were rejected above. Both boundaries need their own later defense.
    for i in range(1, len(rows)):
        if policy.calendar != "UTC_CONTINUOUS_24_7":
            continue  # session gaps need separately reviewed exchange calendar
        a, b = prices[i-1], prices[i]
        boundaries = []
        if a[1] < b[2]:
            boundaries = [(a[1], 'SUPPORT', i-1), (b[2], 'SUPPORT', i)]
        elif b[1] < a[2]:
            boundaries = [(a[2], 'RESISTANCE', i-1), (b[1], 'RESISTANCE', i)]
        for p, side, origin in boundaries:
            for j in range(i+1, len(rows)):
                if not _inside(prices[j][3], p, side):
                    break
                if _contact(prices[j], p, side):
                    claims.append(_claim(rows, timeframe, p, side, 'GAP', origin, j,
                                         [i-1, i, j]))
                    break
    levels = {}
    # Group by availability before assigning type; a deterministic sort is not a tie-break.
    grouped = {}
    for claim in claims:
        key = (Decimal(claim['price']), claim['known_at_ms'])
        grouped.setdefault(key, []).append(claim)
    for (p, known), batch in sorted(grouped.items()):
        if p not in levels:
            types = sorted({x['type'] for x in batch})
            primary = dict(batch[0])
            primary.update(primary_type=types[0] if len(types) == 1 else 'AMBIGUOUS',
                           competing_primary_types=types if len(types) > 1 else [],
                           status='RESEARCH_CANDIDATE', verification='AUTOMATED_ARCHETYPE_ONLY',
                           historical_tick='PENDING', independent_review='PENDING',
                           additional_patterns=[])
            levels[p] = primary
        else:
            for claim in batch:
                event = dict(type=claim['type'], known_at_ms=known,
                             source_open_ms=claim['source_open_ms'],
                             witness_indices=claim['witness_indices'])
                if event not in levels[p]['additional_patterns']:
                    levels[p]['additional_patterns'].append(event)
    return sorted(levels.values(), key=lambda x: (x['known_at_ms'], Decimal(x['price'])))


def provisional_rating(rows, level, other_levels, *, as_of_ms):
    """Book model preview, NEVER the reviewed rate() path or a confirmed score.

    Contacts stop at first exact-price close beyond the defended side; this is a
    conservative diagnostic freeze, not the unapproved contextual-zone lifecycle.
    No near-miss, new-extreme or round bonus without their approved semantics.
    """
    if type(as_of_ms) is not int:
        raise ValueError('integer cutoff required')
    base = dict(status='PROVISIONAL_RESEARCH_ONLY', confirmed_score=None,
                probability=None, historical_tick='PENDING', independent_review='PENDING',
                calibration='UNVALIDATED_ENGINEERING_WEIGHTS', as_of_ms=as_of_ms)
    if level['known_at_ms'] > as_of_ms or level['primary_type'] not in BASE:
        return dict(base, provisional_score=None, reason='UNAVAILABLE_OR_AMBIGUOUS')
    p = Decimal(level['price'])
    side = level['side']
    counts = {'TOUCH': 0, 'FALSE_BREAKOUT': 0}
    wick = Decimal(0)
    events = []
    closed_beyond = None
    invalid_limit = None
    for r in rows:
        if r[0] < level['known_at_ms'] or r[6]+1 > as_of_ms:
            continue
        b = tuple(map(Decimal, r[1:5]))
        boundary = b[2] if side == 'SUPPORT' else b[1]
        if (level['primary_type'] == 'LIMIT'
                and (boundary < p if side == 'SUPPORT' else boundary > p)):
            invalid_limit = r[6]+1
            break
        if _inside(b[3], p, 'RESISTANCE' if side == 'SUPPORT' else 'SUPPORT'):
            closed_beyond = r[6]+1
            break
        kind = _contact(b, p, side)
        if kind:
            counts[kind] += 1
            length = b[1]-b[2]
            relevant = min(b[0], b[3])-b[2] if side == 'SUPPORT' else b[1]-max(b[0], b[3])
            if length:
                wick = max(wick, relevant/length)
            events.append(dict(kind=kind, source_open_ms=r[0], known_at_ms=r[6]+1))
    reinforcement = []
    for x in other_levels:
        if (x['timeframe'] == level['timeframe'] or Decimal(x['price']) != p
                or x['known_at_ms'] > as_of_ms or x['primary_type'] not in BASE):
            continue
        # Prevent already-breached opposite-TF records from reinforcing current strength.
        if x.get('first_close_beyond_ms') is not None and x['first_close_beyond_ms'] <= as_of_ms:
            continue
        if x.get('first_limit_penetration_ms') is not None and x['first_limit_penetration_ms'] <= as_of_ms:
            continue
        reinforcement.append(dict(timeframe=x['timeframe'], known_at_ms=x['known_at_ms']))
    components = dict(primary_type=Decimal(BASE[level['primary_type']]),
                      touches=Decimal(min(counts['TOUCH'], 6)*5),
                      false_breakouts=Decimal(min(counts['FALSE_BREAKOUT'], 3)*5),
                      rejection_wick=5*wick, cross_tf=Decimal(5 if reinforcement else 0),
                      near_misses=Decimal(0), new_extreme=Decimal(0))
    raw = min(Decimal(100), sum(components.values(), Decimal(0)))
    score = raw.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
    usable = closed_beyond is None and invalid_limit is None
    return dict(base, provisional_score=float(score) if usable else None,
                diagnostic_score_before_close_beyond=float(score),
                first_close_beyond_ms=closed_beyond,
                first_limit_penetration_ms=invalid_limit,
                grade=('VERY_STRONG' if score >= 80 else 'STRONG' if score >= 60
                       else 'MODERATE' if score >= 40 else 'WEAK') if usable else None,
                components={k: float(v) for k, v in components.items()}, counts=counts,
                events=events, reinforcement=reinforcement, round_assessed=False,
                near_miss_assessed=False, new_extreme_assessed=False)
