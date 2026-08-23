from datetime import datetime, timedelta, timezone
from decimal import Decimal

from ktrader.models import NormalizedCandle
from ktrader.structure import (
    SwingPoint,
    build_mtf_level_map,
    classify_mtf_regime,
    classify_regime,
    classify_sessions,
    classify_strength,
    cluster_swing_levels,
    detect_consolidation_level,
    detect_swings,
    explicit_level,
    update_level,
)


UTC = timezone.utc
STEP_SECONDS = {"1d": 86400, "4h": 14400, "1h": 3600, "15m": 900, "5m": 300}


def make_wave(
    n: int,
    *,
    interval: str = "1h",
    direction: int = 1,
    volume: str = "100",
) -> list[NormalizedCandle]:
    start = datetime(2026, 1, 1, tzinfo=UTC)
    oscillation = [Decimal("0"), Decimal("2"), Decimal("-1"), Decimal("1")]
    result: list[NormalizedCandle] = []

    for index in range(n):
        trend = Decimal(str(direction)) * Decimal("0.7") * Decimal(index)
        wave = oscillation[index % 4] * Decimal(str(direction))
        close = Decimal("1000") + trend + wave
        open_price = close - Decimal("0.1") * Decimal(str(direction))
        high = max(open_price, close) + Decimal("0.5")
        low = min(open_price, close) - Decimal("0.5")
        open_time = start + timedelta(seconds=STEP_SECONDS[interval] * index)
        result.append(
            NormalizedCandle(
                provider_id="test",
                symbol="XUSDT",
                interval=interval,
                open_time=open_time,
                close_time=open_time
                + timedelta(seconds=STEP_SECONDS[interval])
                - timedelta(milliseconds=1),
                open=open_price,
                high=high,
                low=low,
                close=close,
                volume=Decimal(volume),
                closed=True,
            )
        )
    return result


def make_bar(
    interval: str,
    open_time: datetime,
    open_price: str | int,
    high: str | int,
    low: str | int,
    close: str | int,
) -> NormalizedCandle:
    return NormalizedCandle(
        provider_id="test",
        symbol="XUSDT",
        interval=interval,
        open_time=open_time,
        close_time=open_time
        + timedelta(seconds=STEP_SECONDS[interval])
        - timedelta(milliseconds=1),
        open=Decimal(str(open_price)),
        high=Decimal(str(high)),
        low=Decimal(str(low)),
        close=Decimal(str(close)),
        volume=Decimal("100"),
        closed=True,
    )


def test_swings_detect_two_sides() -> None:
    swings = detect_swings(make_wave(40), left=1, right=1)
    assert len([swing for swing in swings if swing.kind == "HIGH"]) >= 2
    assert len([swing for swing in swings if swing.kind == "LOW"]) >= 2


def test_bullish_regime_and_strength() -> None:
    candles = make_wave(220, direction=1)
    regime = classify_regime(candles, pivot_left=1, pivot_right=1)
    assert regime.regime == "BULLISH"

    strength = classify_strength(candles, regime)
    assert strength.classification == "STRONG"
    assert strength.evidence_count == 3


def test_bearish_regime() -> None:
    regime = classify_regime(
        make_wave(220, direction=-1),
        pivot_left=1,
        pivot_right=1,
    )
    assert regime.regime == "BEARISH"


def test_mtf_regime_requires_htf_alignment() -> None:
    candles_by_interval = {
        interval: make_wave(220, interval=interval, direction=1)
        for interval in ("1d", "4h", "1h")
    }
    snapshot = classify_mtf_regime(
        candles_by_interval,
        pivot_left=1,
        pivot_right=1,
    )
    assert snapshot.regime == "BULLISH"


def test_session_context_handles_dst_overlap() -> None:
    timestamp = datetime(2026, 8, 23, 13, 0, tzinfo=UTC)
    context = classify_sessions(timestamp)
    assert "LONDON" in context.active_sessions
    assert "NEW_YORK" in context.active_sessions
    assert context.overlap is True


def test_historical_cluster_confirmation_and_strength() -> None:
    started = datetime(2026, 1, 1, tzinfo=UTC)
    swings = (
        SwingPoint("HIGH", 1, started, Decimal("110"), "1h"),
        SwingPoint("HIGH", 5, started + timedelta(hours=4), Decimal("110.1"), "1h"),
        SwingPoint("HIGH", 9, started + timedelta(hours=8), Decimal("109.95"), "1h"),
    )

    levels = cluster_swing_levels(
        swings,
        provider_id="test",
        symbol="XUSDT",
        atr14=Decimal("2"),
        zone_atr_fraction=Decimal("0.1"),
    )
    assert len(levels) == 1
    assert levels[0].status == "CONFIRMED"
    assert levels[0].strength == "STRONG"


def test_single_touch_floating_level_is_not_active() -> None:
    started = datetime(2026, 1, 1, tzinfo=UTC)
    level = explicit_level(
        provider_id="test",
        symbol="XUSDT",
        timeframe="1h",
        lower=Decimal("99"),
        upper=Decimal("101"),
        side="SUPPORT",
        level_type="LIMIT",
        created_at=started,
        confirmed=False,
    )
    assert build_mtf_level_map({"1h": [level]}).active() == ()


def test_support_break_to_mirror_to_invalidation() -> None:
    started = datetime(2026, 1, 1, tzinfo=UTC)
    level = explicit_level(
        provider_id="test",
        symbol="XUSDT",
        timeframe="1h",
        lower=Decimal("99"),
        upper=Decimal("101"),
        side="SUPPORT",
        level_type="HISTORICAL",
        created_at=started,
        confirmed=True,
        touches=2,
    )

    broken = update_level(
        level,
        make_bar("1h", started + timedelta(hours=1), 100, 100, 96, 98),
    )
    assert broken.status == "BROKEN"
    assert "TREND_BREAK" in broken.types

    mirror = update_level(
        broken,
        make_bar("1h", started + timedelta(hours=2), 98, 100, 97, 98),
    )
    assert mirror.status == "MIRROR"
    assert mirror.side == "RESISTANCE"

    invalidated = update_level(
        mirror,
        make_bar("1h", started + timedelta(hours=3), 100, 103, 99, 102),
    )
    assert invalidated.status == "INVALIDATED"


def test_broken_level_is_not_active_validation_level() -> None:
    started = datetime(2026, 1, 1, tzinfo=UTC)
    level = explicit_level(
        provider_id="test",
        symbol="XUSDT",
        timeframe="1h",
        lower=Decimal("99"),
        upper=Decimal("101"),
        side="SUPPORT",
        level_type="HISTORICAL",
        created_at=started,
        confirmed=True,
        touches=2,
    )
    broken = update_level(
        level,
        make_bar("1h", started + timedelta(hours=1), 100, 100, 96, 98),
    )
    assert build_mtf_level_map({"1h": [broken]}).active() == ()


def test_mtf_nearest_support_and_resistance() -> None:
    started = datetime(2026, 1, 1, tzinfo=UTC)
    support = explicit_level(
        provider_id="test",
        symbol="XUSDT",
        timeframe="4h",
        lower=Decimal("89"),
        upper=Decimal("91"),
        side="SUPPORT",
        level_type="HISTORICAL",
        created_at=started,
        confirmed=True,
        touches=2,
    )
    resistance = explicit_level(
        provider_id="test",
        symbol="XUSDT",
        timeframe="1h",
        lower=Decimal("109"),
        upper=Decimal("111"),
        side="RESISTANCE",
        level_type="HISTORICAL",
        created_at=started,
        confirmed=True,
        touches=2,
    )
    level_map = build_mtf_level_map({"4h": [support], "1h": [resistance]})
    assert level_map.nearest_support(Decimal("100")) == support
    assert level_map.nearest_resistance(Decimal("100")) == resistance


def test_consolidation_level_detection() -> None:
    candles = make_wave(30, interval="1h", direction=1)
    for index in range(18, 30):
        candles[index] = make_bar(
            "1h",
            candles[index].open_time,
            115,
            115.5,
            114.5,
            115.1,
        )

    level = detect_consolidation_level(
        candles,
        window=12,
        max_width_atr=Decimal("2"),
    )
    assert level is not None
    assert "CONSOLIDATION" in level.types
    assert level.status == "CONFIRMED"


def test_limit_level_requires_explicit_input() -> None:
    started = datetime(2026, 1, 1, tzinfo=UTC)
    level = explicit_level(
        provider_id="test",
        symbol="XUSDT",
        timeframe="1h",
        lower=Decimal("99"),
        upper=Decimal("100"),
        side="SUPPORT",
        level_type="LIMIT",
        created_at=started,
    )
    assert level.status == "FLOATING"
    assert level.types == ("LIMIT",)
