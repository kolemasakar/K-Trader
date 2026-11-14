"""Causal automatic classification and strong-level screening.

Geometry for orders is validated separately. The scanner never fabricates
a review, tick specification, or approval of an unresolved archetype.
"""
from decimal import Decimal

from ktrader.level_admission import fingerprint
from ktrader.level_semantic_audit import audit_panel
from scripts.research.gerchik_seven_types_v0_1 import ResearchPolicy, detect_all

POLICY = ResearchPolicy(
    provenance="GERCHIK_AUTOMATIC_BASELINE_V1", directional_transitions=2,
    trend_defenses=2, historical_repetitions=2, mirror_defenses=2,
    paranormal_reference_bars=20, paranormal_multiple="2",
    calendar="US_EQUITY_SESSION_WALL_CLOCK",
)


def contextual_luft(price, asset_class, symbol):
    if asset_class in ("us_equity", "crypto"):
        return price * Decimal(".0004")
    if asset_class == "energy":
        return Decimal(".03")
    if asset_class == "metals" and symbol in ("XAUUSD", "XAGUSD"):
        return Decimal(".15")
    return None


def contact_evidence(candidate, rows, available, formation_at, luft):
    """One contact class per event. A wick describes rejection, not a new touch."""
    p = Decimal(candidate["price"])
    sign = 1 if candidate["side"] == "SUPPORT" else -1
    used = set(candidate["witness_indices"])
    events = []
    excursion = []
    for i, row in enumerate(rows):
        if i <= candidate["confirmation_index"] or i in used or row[0] < formation_at:
            continue
        o,h,l,c = map(Decimal, row[1:5])
        distance = sign*((l if sign == 1 else h)-p)
        defended = sign*(c-p)>0
        if candidate["primary_type"] == "LIMIT" and distance < 0:
            # A penetration invalidates the exact-touch limit archetype.
            return events, available[i]
        if not defended:
            if sign*(c-p)<0:
                if excursion or sign*(o-p)>0:
                    excursion.append(i)
            else:
                excursion.clear()
            continue
        if excursion:
            kind, indices = "FALSE_BREAKOUT", [*excursion,i]
        elif distance < 0 and sign*(o-p)>0:
            kind, indices = "FALSE_BREAKOUT", [i]
        elif distance == 0:
            kind, indices = "TOUCH", [i]
        elif luft is not None and 0 < distance <= luft:
            kind, indices = "NEAR_MISS", [i]
        else:
            excursion.clear()
            continue
        excursion.clear()
        wick = min(o,c)-l if sign == 1 else h-max(o,c)
        events.append(dict(kind=kind, indices=indices, known_at_ms=available[i],
                           rejection_wick_ratio=str(wick/(h-l)) if h>l else None))
    return events, None


def atr_large_bars(rows):
    from scripts.research.gerchik_filtered_atr5_v1 import DailyBar, filtered_atr5
    bars = [DailyBar(str(r[0]).zfill(20),float(r[2]),float(r[3])) for r in rows]
    large = {}
    for i in range(5,len(rows)):
        try:
            audit = filtered_atr5(bars[max(0,i-250):i][::-1])
        except ValueError:
            continue  # No usable preceding ATR: no classification.
        reference = Decimal(str(audit["atr5"]))
        if Decimal(rows[i][2])-Decimal(rows[i][3]) >= 2*reference:
            large[i] = {"atr5":str(reference),"reference_opens_ms":[int(b["timestamp"]) for b in audit["accepted"]]}
    return large


def reaction_evidence(candidate, rows, available, formation):
    """Confirmed 2+2 swings, in the direction of the reaction."""
    support = candidate["side"] == "SUPPORT"
    field = 2 if support else 3
    sign = 1 if support else -1
    ref = None
    for i in range(2,len(rows)-2):
        value = sign*Decimal(rows[i][field])
        if not all(value > sign*Decimal(rows[j][field]) for j in (i-2,i-1,i+1,i+2)):
            continue
        if available[i+2] <= available[candidate["source_index"]]:
            ref = (i,value)
        elif ref and rows[i-2][0] >= formation and value > ref[1]:
            return [dict(kind="NEW_EXTREME",indices=[ref[0],*range(i-2,i+3)],
                         known_at_ms=available[i+2])]
    return []


def origin_wick(candidate, rows, formation):
    i = candidate["source_index"]
    o,h,l,c = map(Decimal,rows[i][1:5])
    p = Decimal(candidate["price"])
    if candidate["side"] == "SUPPORT":
        matches, wick, opposite = l == p and c > p, min(o,c)-l, h-max(o,c)
    else:
        matches, wick, opposite = h == p and c < p, h-max(o,c), min(o,c)-l
    if matches and wick > max(abs(o-c),opposite):
        return [dict(kind="REJECTION_WICK",indices=[i],known_at_ms=formation,
                     rejection_wick_ratio=str(wick/(h-l)))]
    return []


def scan_levels(rows, timeframe, *, timeframe_ms, as_of_ms, availability=None, asset_class=None, symbol=None, round_grid=None, verified_gap_pairs=()):
    """Read one asset/timeframe of closed bars in the Gerchik row format.

    Row end is the inclusive availability time; delayed aggregates must
    supply their actual availability, or be excluded by the caller.
    Duration describes the timeframe, not the elapsed span of a session bar.
    """
    if not timeframe or type(timeframe_ms) is not int or timeframe_ms <= 0:
        raise ValueError("explicit timeframe and positive nominal duration required")
    if timeframe_ms < 86400000:
        return []  # Do not consume lower-timeframe data or invoke the detector.
    rows = list(rows)
    available = [r[6]+1 for r in rows] if availability is None else availability
    if (len(available)!=len(rows) or any(a<r[6]+1 for r,a in zip(rows,available))
            or any(a>=b for a,b in zip(available,available[1:]))):
        raise ValueError("invalid bar availability")
    from bisect import bisect_right
    n = bisect_right(available,as_of_ms)
    closed = rows[:n]
    available = available[:n]
    levels = []
    atr_large = atr_large_bars(closed)
    if round_grid is not None:
        step = Decimal(str(round_grid["step"]))
        offset = Decimal(str(round_grid.get("offset",0)))
        if not step.is_finite() or step<=0 or not offset.is_finite() or not round_grid.get("provenance"):
            raise ValueError("round grid requires positive step and provenance")
    for candidate in detect_all(closed,timeframe,POLICY,bar_series=True,
                                atr_large_indices=atr_large,verified_gap_pairs=verified_gap_pairs):
        identity = fingerprint(candidate)
        audit = audit_panel(dict(candidate=candidate, evidence_id=identity),
                            closed, as_of_ms=as_of_ms)
        verified = audit["status"] == "SHAPE_PASS_REVIEW_PENDING"
        structural = candidate["primary_type"] in ("TREND_BREAK", "HISTORICAL", "PARANORMAL_BAR", "GAP")
        confirmed = verified or structural
        price = Decimal(candidate["price"])
        formation = available[candidate["confirmation_index"]]
        tolerance = contextual_luft(price,asset_class,symbol)
        evidence, invalidated = contact_evidence(candidate,closed,available,formation,tolerance) if confirmed else ([],None)
        if confirmed:
            evidence.extend(origin_wick(candidate,closed,formation))
            evidence.extend(reaction_evidence(candidate,closed,available,formation))
            if round_grid is not None and (price-offset)%step==0:
                evidence.append(dict(kind="ROUND_PRICE",indices=[candidate["source_index"]],
                                     known_at_ms=formation,provenance=round_grid["provenance"]))
        evidence = sorted((e for e in evidence if invalidated is None or e["known_at_ms"]<invalidated),
                          key=lambda e:e["known_at_ms"])
        first = evidence[0]["known_at_ms"] if evidence else None
        strong = first is not None
        close = Decimal(str(closed[-1][4]))
        defended = (close > price if candidate["side"] == "SUPPORT"
                    else close < price)
        levels.append({
            "candidate": candidate, "evidence_id": identity,
            "confirmation": ("AUTOMATIC_RULE_CHECK" if verified else
                             "AUTOMATIC_STRUCTURAL_RULE" if structural else audit["status"]),
            "formation_available_at_ms": formation,
            "invalidated_at_ms": invalidated,
            "strengthening": evidence,
            "strong": strong, "defended_as_of": defended,
            "trade_level_eligible": strong and defended and invalidated is None,
            "strong_known_at_ms": first,
            "available_at_ms": first,
            "strengthening_indices": sorted({i for e in evidence for i in e["indices"]}),
            "checks": audit["checks"] if not structural else {},
            "atr_evidence": atr_large.get(candidate["source_index"]) if candidate["primary_type"]=="PARANORMAL_BAR" else None,
        })
    return levels


def s1_level_book(candles, as_of_ms, *, asset_class=None, symbol=None, round_grid=None, verified_gap_pairs=None):
    """Return strong candidates with causal D1/W1 activation and side state."""
    from bisect import bisect_left
    from ktrader.s1_equity_level_rows import completed_daily, completed_weekly

    daily = [r for r in completed_daily(candles) if r[6] < as_of_ms]
    closed_candles = candles[:len(daily)]
    rows = {"D1": daily, "W1": completed_weekly(closed_candles)}
    starts = [r[0] for r in daily]
    availability = {
        "D1": [r[6]+1 for r in daily],
        "W1": [daily[bisect_left(starts, r[6]+1)][6]+1 for r in rows["W1"]],
    }
    levels = []
    for tf, duration in (("D1", 86400000), ("W1", 604800000)):
        levels.extend(scan_levels(rows[tf],tf,timeframe_ms=duration,as_of_ms=as_of_ms,
                                  availability=availability[tf],asset_class=asset_class,symbol=symbol,
                                  round_grid=round_grid,
                                  verified_gap_pairs={tuple(pair) for pair in (verified_gap_pairs or {}).get(tf,[])}))
    # Cross-timeframe reinforcement only when both confirmed roles are defended
    # at their common availability, using the tighter of the two approved zones.
    confirmed = [x for x in levels if x["confirmation"].startswith("AUTOMATIC_")]
    for item in confirmed:
        c = item["candidate"]
        p = Decimal(c["price"])
        for other in confirmed:
            d = other["candidate"]
            if c["timeframe"] == d["timeframe"] or c["side"] != d["side"]:
                continue
            q = Decimal(d["price"])
            width = min(contextual_luft(p,asset_class,symbol) or 0,
                        contextual_luft(q,asset_class,symbol) or 0)
            if abs(p-q)>width:
                continue
            when = max(item["formation_available_at_ms"],other["formation_available_at_ms"])
            if not all(_defended(x,rows,availability,when) for x in (item,other)):
                continue
            item["strengthening"].append(dict(kind="CROSS_TF",known_at_ms=when,
                                              other_evidence_id=other["evidence_id"],
                                              other_timeframe=d["timeframe"]))
        item["strengthening"].sort(key=lambda x:x["known_at_ms"])
        if item["strengthening"]:
            item["strong"] = True
            item["available_at_ms"] = item["strong_known_at_ms"] = item["strengthening"][0]["known_at_ms"]
        item["trade_level_eligible"] = s1_level_active(item,rows,availability,as_of_ms)
    return levels, rows, availability


def s1_level_active(item, rows, availability, now):
    return bool(item["strong"] and item["available_at_ms"] <= now
                and _defended(item,rows,availability,now))


def _defended(item,rows,availability,now):
    from bisect import bisect_right

    invalidated = item["invalidated_at_ms"]
    if invalidated is not None and invalidated <= now:
        return False
    candidate = item["candidate"]
    tf = candidate["timeframe"]
    n = bisect_right(availability[tf], now)
    if not n:
        return False
    close = Decimal(rows[tf][n-1][4])
    price = Decimal(candidate["price"])
    return close > price if candidate["side"] == "SUPPORT" else close < price
