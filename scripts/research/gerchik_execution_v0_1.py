"""Pure research execution model; no strategy detection or order execution.

Times are integer UTC epoch milliseconds; bar ends are exclusive. Prices and
per-unit costs must be finite. Config is an explicit experiment assumption.
"""
from dataclasses import dataclass
from math import isfinite
from typing import Sequence


@dataclass(frozen=True)
class Bar:
    start: int
    end: int
    open: float
    high: float
    low: float
    close: float


@dataclass(frozen=True)
class Setup:
    strategy_id: str
    specification: str
    known_at: int
    level_known_at: int
    level_provenance: str
    side: str
    stop: float


@dataclass(frozen=True)
class Config:
    target_r: int
    horizon_bars: int
    interval_ms: int
    fee_rate: float
    adverse_fill_cost: float  # combined spread/slippage per fill, price units
    funding_cost_per_unit: float  # signed total for this declared horizon
    cost_provenance: str
    collision_policy: str = "AMBIGUOUS"


def simulate(setup: Setup, bars: Sequence[Bar], config: Config) -> dict:
    """Simulate one externally confirmed setup, with risk at actual entry open.

    Funding is a supplied horizon estimate, not inferred historical payments.
    Pending/censored/ambiguous observations have no realized R. Stop-first is
    an explicitly selected sensitivity, never the default primary result.
    """
    if (any(type(value) is not int for value in (setup.known_at, setup.level_known_at,
                                               config.horizon_bars, config.interval_ms))
            or setup.strategy_id not in {f"S{i}" for i in range(1, 7)}
            or not setup.specification or not setup.level_provenance
            or setup.side not in {"LONG", "SHORT"}
            or setup.level_known_at > setup.known_at):
        raise ValueError("invalid or noncausal setup")
    if (config.target_r not in (1, 3) or config.horizon_bars <= 0
            or config.interval_ms <= 0 or not config.cost_provenance
            or config.collision_policy not in {"AMBIGUOUS", "STOP_FIRST"}):
        raise ValueError("explicit experiment configuration required")
    if (not all(isfinite(x) for x in (setup.stop, config.fee_rate,
            config.adverse_fill_cost, config.funding_cost_per_unit))
            or setup.stop <= 0 or config.fee_rate < 0
            or config.adverse_fill_cost < 0):
        raise ValueError("invalid price or cost")
    for index, bar in enumerate(bars):
        if (type(bar.start) is not int or type(bar.end) is not int
                or bar.start != setup.known_at + index * config.interval_ms
                or bar.end != bar.start + config.interval_ms
                or not all(isfinite(x) and x > 0 for x in
                           (bar.open, bar.high, bar.low, bar.close))
                or not bar.low <= min(bar.open, bar.close)
                <= max(bar.open, bar.close) <= bar.high):
            raise ValueError("bars must be valid and contiguous from next open")
    base = {"strategy_id": setup.strategy_id, "specification": setup.specification,
            "level_provenance": setup.level_provenance,
            "target_r": config.target_r, "collision_policy": config.collision_policy,
            "cost_provenance": config.cost_provenance,
            "funding_model": "DECLARED_HORIZON_ESTIMATE",
            "gross_r": None, "net_r": None}
    if not bars:
        return dict(base, status="PENDING_ENTRY")
    sign = 1 if setup.side == "LONG" else -1
    entry = bars[0].open
    risk = sign * (entry - setup.stop)
    if risk <= 0:
        return dict(base, status="INVALID_ENTRY_GEOMETRY", entry=entry)
    target = entry + sign * config.target_r * risk
    if target <= 0:
        return dict(base, status="INVALID_TARGET_GEOMETRY", entry=entry)
    base.update(entry=entry, stop=setup.stop, target=target, risk=risk)

    def finish(status, price, bar):
        gross = sign * (price - entry) / risk
        cost = (config.fee_rate * (entry + price)
                + 2 * config.adverse_fill_cost + config.funding_cost_per_unit)
        return dict(base, status=status, exit_price=price, exit_bar_end=bar.end,
                    gross_r=gross, net_r=gross - cost / risk, cost_per_unit=cost)

    for bar in bars[:config.horizon_bars]:
        # Open is observed before the intrabar range; adverse stop gaps fill at open.
        if sign * (bar.open - setup.stop) <= 0:
            return finish("STOP_GAP", bar.open, bar)
        if sign * (bar.open - target) >= 0:
            return finish("TARGET_GAP", target, bar)
        stop_hit = bar.low <= setup.stop if sign == 1 else bar.high >= setup.stop
        target_hit = bar.high >= target if sign == 1 else bar.low <= target
        if stop_hit and target_hit and config.collision_policy == "AMBIGUOUS":
            return dict(base, status="AMBIGUOUS", exit_bar_end=bar.end)
        if stop_hit:
            return finish("STOP", setup.stop, bar)
        if target_hit:
            return finish("TARGET", target, bar)
    if len(bars) < config.horizon_bars:
        return dict(base, status="CENSORED")
    last = bars[config.horizon_bars - 1]
    return finish("TIME_EXIT", last.close, last)
