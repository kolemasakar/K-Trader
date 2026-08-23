from datetime import datetime, timedelta, timezone
from decimal import Decimal

import pytest

from ktrader.indicators.atr import wilder_atr_series
from ktrader.market.validation import CandleValidationError, FreshnessPolicy, assess_freshness
from ktrader.models import NormalizedCandle
from ktrader.replay import canonical_digest, replay_level_lifecycle, replay_trap_states, validate_replay_series
from ktrader.structure.levels import explicit_level


UTC = timezone.utc
START = datetime(2026, 1, 1, tzinfo=UTC)


def bar(index, o, h, l, c, *, interval="5m", provider="p", symbol="X"):
    seconds = {"5m": 300, "1h": 3600, "1d": 86400}[interval]
    opened = START + timedelta(seconds=seconds * index)
    return NormalizedCandle(
        provider_id=provider,
        symbol=symbol,
        interval=interval,
        open_time=opened,
        close_time=opened + timedelta(seconds=seconds) - timedelta(milliseconds=1),
        open=Decimal(str(o)),
        high=Decimal(str(h)),
        low=Decimal(str(l)),
        close=Decimal(str(c)),
        volume=Decimal("100"),
        closed=True,
    )


def support():
    return explicit_level(
        provider_id="p",
        symbol="X",
        timeframe="5m",
        lower=Decimal("99"),
        upper=Decimal("100"),
        side="SUPPORT",
        level_type="HISTORICAL",
        created_at=START - timedelta(days=1),
        confirmed=True,
        touches=2,
    )


def test_trap_replay_is_causal_broken_returned_confirmed():
    candles = [
        bar(0, 101, 102, 100, 101),
        bar(1, 100, 100.2, 98, 98.4),
        bar(2, 98.5, 101, 98.3, 100.2),
        bar(3, 100.2, 102, 100, 101.5),
    ]
    states = [item.state for item in replay_trap_states(candles, support(), atr14=Decimal("10"))]
    assert states == ["NONE", "BROKEN", "RETURNED", "CONFIRMED"]


def test_trap_expires_only_after_full_return_window():
    candles = [
        bar(0, 101, 102, 100, 101),
        bar(1, 100, 100.2, 98, 98.4),
        bar(2, 98.4, 98.8, 97.5, 98.0),
        bar(3, 98.0, 98.5, 97.0, 97.5),
        bar(4, 97.5, 98.0, 96.5, 97.0),
    ]
    states = [item.state for item in replay_trap_states(candles, support(), atr14=Decimal("10"), max_return_bars=3)]
    assert states[1:4] == ["BROKEN", "BROKEN", "BROKEN"]
    assert states[4] == "EXPIRED"


def test_level_lifecycle_replay_is_ordered():
    level = explicit_level(
        provider_id="p",
        symbol="X",
        timeframe="1h",
        lower=Decimal("99"),
        upper=Decimal("101"),
        side="SUPPORT",
        level_type="HISTORICAL",
        created_at=START - timedelta(hours=1),
        confirmed=True,
        touches=2,
    )
    candles = [
        bar(0, 100, 100, 96, 98, interval="1h"),
        bar(1, 98, 100, 97, 98, interval="1h"),
        bar(2, 100, 103, 99, 102, interval="1h"),
    ]
    states = [item.state for item in replay_level_lifecycle(level, candles)]
    assert states == ["BROKEN", "MIRROR", "INVALIDATED"]


def test_replay_rejects_gap_and_cross_provider_mix():
    with pytest.raises(CandleValidationError):
        validate_replay_series([bar(0, 100, 101, 99, 100), bar(2, 100, 101, 99, 100)])
    with pytest.raises(CandleValidationError):
        validate_replay_series([bar(0, 100, 101, 99, 100), bar(1, 100, 101, 99, 100, provider="other")])


def test_wilder_atr_history_has_no_future_lookahead():
    prefix = [bar(i, 100, 101.5, 98.5, 100, interval="1d") for i in range(30)]
    future = bar(30, 100, 150, 50, 100, interval="1d")
    before = wilder_atr_series(prefix, period=14)
    after = wilder_atr_series(prefix + [future], period=14)
    assert after[len(prefix) - 1] == before[-1]


def test_freshness_boundary_is_fail_closed_after_limit():
    candle = bar(0, 100, 101, 99, 100)
    policy = FreshnessPolicy(max_age_intervals=2)
    exact_limit = candle.close_time + timedelta(seconds=600)
    assert assess_freshness(candle, policy=policy, now=exact_limit).stale is False
    assert assess_freshness(candle, policy=policy, now=exact_limit + timedelta(milliseconds=1)).stale is True


def test_replay_digest_is_deterministic():
    observations = replay_trap_states(
        [bar(0, 101, 102, 100, 101), bar(1, 100, 100.2, 98, 98.4)],
        support(),
        atr14=Decimal("10"),
    )
    assert canonical_digest(observations) == canonical_digest(observations)
    assert len(canonical_digest(observations)) == 64
