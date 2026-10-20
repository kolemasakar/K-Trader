"""Independent rule checks on candidate witnesses; NEVER reviewer admission.

No detector imports, tick assumptions, ATR, score, calendar or scheduler.
Passing a shape check is not a confirmed Gerchik type or independent label.
"""
from collections import Counter
from decimal import Decimal


def audit_panel(panel, rows, *, as_of_ms):
    c = panel['candidate']
    price = Decimal(c['price'])
    support = c['side'] == 'SUPPORT'
    if c['side'] not in ('SUPPORT', 'RESISTANCE'):
        raise ValueError('unknown side')
    origin, end = c['source_index'], c['confirmation_index']
    if not 0 <= origin <= end < len(rows):
        raise ValueError('invalid formation indices')
    if c['known_at_ms'] > as_of_ms or rows[end][6]+1 > c['known_at_ms']:
        raise ValueError('formation unavailable')
    bars = [tuple(Decimal(str(v)) for v in r[1:5]) for r in rows[:end+1]]
    def inside(value, on_support=support):
        return value > price if on_support else value < price
    def boundary(bar, on_support=support):
        return bar[2] if on_support else bar[1]
    def defended(bar, on_support):
        # Exact touch, or one-bar penetration and return from defended side.
        p = boundary(bar, on_support)
        return inside(bar[3], on_support) and (
            p == price or (not inside(p, on_support) and inside(bar[0], on_support)))
    kind = c['primary_type']
    checks = {}
    if kind == 'LIMIT':
        checks = {'three_or_more_consecutive_exact_extrema': end-origin+1 >= 3 and
                  all(boundary(b) == price for b in bars[origin:end+1])}
    elif kind == 'CONSOLIDATION':
        checks = {
            'origin_and_confirmation_exact': boundary(bars[origin]) == price and boundary(bars[end]) == price,
            'three_or_more_strictly_one_sided_between': end-origin-1 >= 3 and
                all(inside(boundary(b)) for b in bars[origin+1:end]),
        }
    elif kind == 'MIRROR':
        old_support = not support
        # Scan the FULL interval, not only the detector's chosen witnesses.
        defenses = [origin] if boundary(bars[origin], old_support) == price and inside(bars[origin][3], old_support) else []
        broken = None
        failed_after_break = False
        for i in range(origin+1, end):
            b = bars[i]
            if broken is None:
                if inside(b[3]):
                    broken = i
                elif defended(b, old_support):
                    defenses.append(i)
            elif not inside(b[3]):
                failed_after_break = True
        checks = {
            'old_side_two_defenses_research_policy': len(defenses) >= 2,
            'closed_role_change': broken is not None,
            'no_failed_role_change_bridged': not failed_after_break,
            'opposite_exact_retest': boundary(bars[end]) == price and
                inside(bars[end][0]) and inside(bars[end][3]),
        }
    elif kind == 'TREND_BREAK':
        return result(panel, 'QUALITATIVE_REVIEW_REQUIRED', {}, [],
                      ['Meaningful reversal/new extreme needs independent contextual review'])
    elif kind == 'PARANORMAL_BAR':
        return result(panel, 'POLICY_UNAPPROVED', {}, [],
                      ['20-bar non-ATR anomaly reference is an unapproved research hypothesis'])
    else:
        return result(panel, 'UNSUPPORTED_REVIEW_REQUIRED', {}, [], [kind])
    # Subsequent exact touches: observations for reviewer, never auto-confirmed proofs.
    # Formation witnesses cannot also become strengthening evidence.
    used = set(c['witness_indices'])
    touches = []
    for i, row in enumerate(rows):
        if i <= end or i in used or row[0] < c['known_at_ms'] or row[6]+1 > as_of_ms:
            continue
        b = tuple(Decimal(str(v)) for v in row[1:5])
        if boundary(b) == price and inside(b[3]):
            touches.append(i)
    return result(panel, 'SHAPE_PASS_REVIEW_PENDING' if all(checks.values()) else 'SHAPE_FAIL',
                  checks, touches, [])


def result(panel, status, checks, touches, notes):
    return {'evidence_id': panel['evidence_id'], 'timeframe': panel['candidate']['timeframe'],
            'primary_type': panel['candidate']['primary_type'], 'status': status,
            'checks': checks, 'subsequent_exact_touch_indices': touches,
            'notes': notes, 'admitted': False, 'independent_review_created': False}


def audit_panels(panels, rows_by_tf, *, as_of_ms):
    results = [audit_panel(p, rows_by_tf[p['candidate']['timeframe']], as_of_ms=as_of_ms)
               for p in panels]
    return {'schema': 'ktrader.level_semantic_audit.v1',
            'scope': 'RULE_SHAPE_DIAGNOSTIC_NOT_INDEPENDENT_LABEL',
            'as_of_ms': as_of_ms, 'scheduler_used': False,
            'counts': dict(Counter(r['status'] for r in results)),
            'admitted_levels': 0, 'results': results}
