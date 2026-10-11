"""Parameterized S1-S6 research candidates, NOT owner-frozen strategies.

Prices are integer ticks. All policy/parameter choices are explicit inputs;
no ATR14 coefficient is converted to D1 ATR5. Callers must independently
establish level validity, contextual admission and parameter provenance.
"""
from dataclasses import dataclass
from decimal import Decimal
from typing import Sequence

if __package__:
    from .gerchik_execution_v0_1 import Setup
else:
    from gerchik_execution_v0_1 import Setup

PRIMARY_TYPES = ("TREND_BREAK", "HISTORICAL", "MIRROR", "LIMIT",
                 "PARANORMAL_BAR", "CONSOLIDATION", "GAP")


@dataclass(frozen=True)
class TickBar:
    start: int
    end: int
    open: int
    high: int
    low: int
    close: int


@dataclass(frozen=True)
class LevelContext:
    symbol: str
    price_ticks: int
    tick_size: str
    timeframe: str
    primary_type: str
    known_at: int
    state: str
    formation_provenance: str
    admission_provenance: str


@dataclass(frozen=True)
class Parameters:
    specification: str
    parameter_provenance: str
    interval_ms: int
    breakout_ticks: int
    penetration_ticks: int
    entry_tolerance_ticks: int
    stop_buffer_ticks: int
    confirmation_policy: str
    s3_retest_bars: int
    s3_resume_policy: str
    s5_min_outside: int
    s5_max_outside: int
    s5_max_structure_bars: int
    s6_range_bars: int
    s6_ema_period: int
    s6_ema_seed: str
    s6_trend_policy: str
    s6_stop_mode: str
    s6_local_bars: int
    s6_atr_stop_ticks: int | None


def detect(strategy_id: str, side: str, level: LevelContext,
           bars: Sequence[TickBar], parameters: Parameters, *, as_of: int) -> dict:
    """Evaluate only the latest completed bar; return explicit candidate evidence.

    This is the pattern layer. It neither creates Gerchik levels nor asserts
    that a caller's CONFIRMED/context admission declarations are validated.
    Future bars are rejected, never silently sliced. Setup is emitted at bar
    end so an executor may enter at the next contiguous bar open.
    """
    p = parameters
    if strategy_id not in tuple(f"S{i}" for i in range(1, 7)) or side not in ("LONG", "SHORT"):
        raise ValueError("unknown strategy or side")
    ints = (level.price_ticks, level.known_at, as_of, p.interval_ms, p.breakout_ticks,
            p.penetration_ticks, p.entry_tolerance_ticks, p.stop_buffer_ticks,
            p.s3_retest_bars, p.s5_min_outside, p.s5_max_outside,
            p.s5_max_structure_bars, p.s6_range_bars, p.s6_ema_period, p.s6_local_bars)
    if any(type(x) is not int for x in ints):
        raise ValueError("integer ticks/timestamps/counts required")
    if (level.price_ticks <= 0 or p.interval_ms <= 0 or p.breakout_ticks <= 0
            or p.penetration_ticks <= 0 or p.entry_tolerance_ticks < 0
            or p.stop_buffer_ticks <= 0 or p.s3_retest_bars != 6
            or p.s5_min_outside != 2 or not 2 <= p.s5_max_outside <= 5
            or not 3 <= p.s5_max_structure_bars <= 6
            or p.s6_range_bars != 20 or p.s6_ema_period != 50 or p.s6_local_bars <= 0):
        raise ValueError("invalid explicit parameters or restored strategy constants")
    if (p.confirmation_policy not in ("DIRECTIONAL_CLOSE", "CLOSE_BEYOND_PREVIOUS_EXTREME")
            or p.s3_resume_policy not in ("RETEST_BAR", "NEXT_BAR")
            or p.s6_ema_seed != "FIRST_CLOSE"
            or p.s6_trend_policy not in ("CLOSE_SIDE", "EMA_SLOPE")
            or p.s6_stop_mode not in ("LOCAL_EXTREME", "ATR_DISTANCE")):
        raise ValueError("explicit supported engineering policy required")
    if not all(isinstance(x, str) and x.strip() for x in
               (p.specification, p.parameter_provenance, level.symbol,
                level.formation_provenance, level.admission_provenance)):
        raise ValueError("missing specification/parameter/level/context provenance")
    tick = Decimal(level.tick_size)
    if not tick.is_finite() or tick <= 0:
        raise ValueError("invalid tick size")
    if p.s6_atr_stop_ticks is not None and (type(p.s6_atr_stop_ticks) is not int
                                           or p.s6_atr_stop_ticks <= 0):
        raise ValueError("ATR stop distance must be supplied in positive ticks")
    if p.s6_stop_mode == "ATR_DISTANCE" and p.s6_atr_stop_ticks is None:
        raise ValueError("no inferred ATR stop distance")
    if level.timeframe not in ("1d", "1w") or level.primary_type not in PRIMARY_TYPES:
        raise ValueError("confirmed D1/W1 Gerchik context required")
    for i, bar in enumerate(bars):
        if (any(type(x) is not int for x in (bar.start, bar.end, bar.open, bar.high, bar.low, bar.close))
                or bar.end - bar.start != p.interval_ms or bar.end > as_of
                or (i > 0 and bar.start != bars[i - 1].end)
                or bar.low <= 0 or not bar.low <= min(bar.open, bar.close)
                <= max(bar.open, bar.close) <= bar.high):
            raise ValueError("invalid, gapped or future input bars")
    base = {"strategy_id": strategy_id, "side": side,
            "specification": p.specification, "parameter_provenance": p.parameter_provenance,
            "authority": "PARAMETERIZED_ENGINEERING_CANDIDATE", "setup": None,
            "evidence": None}
    if not bars:
        return dict(base, status="INSUFFICIENT_HISTORY")
    # A level discovered after a pattern began cannot retrospectively admit it.
    if level.state != "CONFIRMED" or level.known_at > bars[-1].end:
        return dict(base, status="LEVEL_UNAVAILABLE")
    sign = 1 if side == "LONG" else -1
    price = sign * level.price_ticks
    rows = [(sign*b.open, b.high if sign == 1 else -b.low,
             b.low if sign == 1 else -b.high, sign*b.close) for b in bars]
    n = len(rows)
    stop = None
    indices = []

    def confirm(index):
        current = rows[index]
        return (current[3] > current[0] if p.confirmation_policy == "DIRECTIONAL_CLOSE"
                else index > 0 and current[3] > rows[index - 1][1])

    if strategy_id == "S1":
        if n < 3:
            return dict(base, status="INSUFFICIENT_HISTORY")
        # Proposed two-bar precision variant; not a full sourced BSU/BPU automaton.
        before, first, second = rows[-3:]
        if (before[3] > price and first[2] == price and first[3] > price
                and price <= second[2] <= price + p.entry_tolerance_ticks
                and second[3] > price and confirm(n-1)):
            stop, indices = min(first[2], second[2])-p.stop_buffer_ticks, [n-2, n-1]
    elif strategy_id == "S2":
        if n < 3:
            return dict(base, status="INSUFFICIENT_HISTORY")
        if (rows[-3][3] <= price and rows[-2][3] >= price+p.breakout_ticks
                and rows[-1][3] > rows[-2][3] and confirm(n-1)):
            stop, indices = price-p.stop_buffer_ticks, [n-2, n-1]
    elif strategy_id == "S3":
        if n < 3:
            return dict(base, status="INSUFFICIENT_HISTORY")
        retest = n-1 if p.s3_resume_policy == "RETEST_BAR" else n-2
        for breakout in range(retest-1, max(-1, retest-p.s3_retest_bars-1), -1):
            if breakout < 1:
                continue
            if (rows[breakout-1][3] <= price and rows[breakout][3] >= price+p.breakout_ticks
                    and all(row[3] > price for row in rows[breakout+1:retest])
                    and price-p.entry_tolerance_ticks <= rows[retest][2] <= price+p.entry_tolerance_ticks
                    and rows[retest][3] > price and rows[-1][3] > price and confirm(n-1)):
                stop, indices = price-p.stop_buffer_ticks, list(range(breakout, n))
                break
    elif strategy_id == "S4":
        if n < 2:
            return dict(base, status="INSUFFICIENT_HISTORY")
        if rows[-2][3] > price and rows[-1][2] <= price-p.penetration_ticks and rows[-1][3] > price:
            stop, indices = rows[-1][2]-p.stop_buffer_ticks, [n-1]
    elif strategy_id == "S5":
        if n < p.s5_min_outside+2:
            return dict(base, status="INSUFFICIENT_HISTORY")
        outside = n-2
        while outside >= 0 and rows[outside][3] < price:
            outside -= 1
        count = n-2-outside
        if (outside >= 0 and rows[outside][3] > price and rows[-1][3] > price
                and p.s5_min_outside <= count <= p.s5_max_outside
                and count+1 <= p.s5_max_structure_bars):
            indices = list(range(outside+1, n))
            stop = min(rows[i][2] for i in indices)-p.stop_buffer_ticks
    else:
        required = max(p.s6_range_bars+1, p.s6_ema_period+1, p.s6_local_bars)
        if n < required:
            return dict(base, status="INSUFFICIENT_HISTORY")
        alpha = Decimal(2)/Decimal(p.s6_ema_period+1)
        ema = Decimal(rows[0][3])
        previous_ema = ema
        for row in rows[1:]:
            previous_ema = ema
            ema += alpha*(Decimal(row[3])-ema)
        trend = Decimal(rows[-1][3]) > ema if p.s6_trend_policy == "CLOSE_SIDE" else ema > previous_ema
        if rows[-1][3] > max(row[1] for row in rows[-p.s6_range_bars-1:-1]) and trend:
            indices = list(range(n-p.s6_range_bars-1, n))
            stop = (min(row[2] for row in rows[-p.s6_local_bars:])-p.stop_buffer_ticks
                    if p.s6_stop_mode == "LOCAL_EXTREME" else rows[-1][3]-p.s6_atr_stop_ticks)
    if stop is None:
        return dict(base, status="NO_PATTERN")
    # Level must be known before the first qualifying pattern bar opens, not only at entry.
    if level.known_at > bars[indices[0]].start:
        return dict(base, status="LEVEL_UNAVAILABLE_AT_PATTERN_START")
    stop_ticks = sign*stop
    if stop_ticks <= 0:
        return dict(base, status="INVALID_STOP")
    setup = Setup(strategy_id, p.specification, bars[-1].end, level.known_at,
                  level.formation_provenance+" | "+level.admission_provenance,
                  side, float(Decimal(stop_ticks)*tick))
    return dict(base, status="CANDIDATE", setup=setup,
                evidence={"bar_starts": [bars[i].start for i in indices],
                          "stop_ticks": stop_ticks, "level_ticks": level.price_ticks,
                          "confirmation_policy": p.confirmation_policy,
                          "s3_resume_policy": p.s3_resume_policy,
                          "s6_stop_mode": p.s6_stop_mode})
