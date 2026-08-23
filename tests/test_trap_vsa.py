from datetime import datetime, timedelta, timezone
from decimal import Decimal

import pytest

from ktrader.evidence.trap import detect_level_traps
from ktrader.evidence.vsa import detect_vsa_events, validate_vsa_context
from ktrader.models import NormalizedCandle
from ktrader.structure.levels import MTFLevelMap, PriceLevel
from ktrader.structure.regime import MTFRegimeSnapshot

UTC = timezone.utc


def candle(i, o, h, l, cl, v):
    open_time = datetime(2026, 1, 1, tzinfo=UTC) + timedelta(minutes=5 * i)
    return NormalizedCandle(
        provider_id="p",
        symbol="X",
        interval="5m",
        open_time=open_time,
        close_time=open_time + timedelta(minutes=5) - timedelta(milliseconds=1),
        open=Decimal(str(o)),
        high=Decimal(str(h)),
        low=Decimal(str(l)),
        close=Decimal(str(cl)),
        volume=Decimal(str(v)),
        closed=True,
    )


def level(level_id, side, lower, upper, status="CONFIRMED"):
    return PriceLevel(
        level_id=level_id,
        provider_id="p",
        symbol="X",
        timeframe="1h",
        lower=Decimal(str(lower)),
        upper=Decimal(str(upper)),
        side=side,
        status=status,
        types=("HISTORICAL",),
        touches=2,
        strength="MODERATE",
        created_at=datetime(2025, 12, 31, tzinfo=UTC),
    )


def baseline():
    return [candle(i, 100, 101, 99, 100.2, 100) for i in range(20)]


def event_types(bar):
    return {event.event_type for event in detect_vsa_events(baseline() + [bar])}


def test_long_trap_confirmed():
    support = level("L", "SUPPORT", 99, 100)
    bars = [
        candle(0, 101, 102, 100, 101, 100),
        candle(1, 100, 100.2, 98, 98.4, 100),
        candle(2, 98.5, 101, 98.3, 100.2, 100),
        candle(3, 100.2, 102, 100, 101.5, 100),
    ]
    event = detect_level_traps(bars, support, atr14=Decimal("10"))[0]
    assert event.direction == "LONG"
    assert event.status == "CONFIRMED"
    assert event.confirmed


def test_short_trap_confirmed():
    resistance = level("R", "RESISTANCE", 100, 101)
    bars = [
        candle(0, 99, 100, 98, 99, 100),
        candle(1, 101, 102.2, 100.8, 101.7, 100),
        candle(2, 101.5, 101.8, 99.7, 100.5, 100),
        candle(3, 100.4, 100.5, 98.8, 99.2, 100),
    ]
    event = detect_level_traps(bars, resistance, atr14=Decimal("10"))[0]
    assert event.direction == "SHORT"
    assert event.status == "CONFIRMED"


def test_trap_expires_without_return():
    support = level("L", "SUPPORT", 99, 100)
    bars = [
        candle(0, 101, 102, 100, 101, 100),
        candle(1, 100, 100.2, 98, 98.4, 100),
        candle(2, 98.5, 98.8, 97.5, 98.0, 100),
        candle(3, 98, 98.5, 97, 97.5, 100),
        candle(4, 97.5, 98, 96.5, 97, 100),
    ]
    event = detect_level_traps(bars, support, atr14=Decimal("10"), max_return_bars=3)[0]
    assert event.status == "EXPIRED"
    assert not event.confirmed


@pytest.mark.parametrize(
    ("event_type", "bar"),
    [
        ("NS", candle(20, 100.6, 100.7, 99.7, 100.4, 60)),
        ("ND", candle(20, 99.8, 100.7, 99.7, 100.0, 60)),
        ("T", candle(20, 100.2, 100.5, 98.5, 100.0, 90)),
        ("UT", candle(20, 100.5, 102.0, 99.0, 99.7, 130)),
        ("BC", candle(20, 99.0, 102.0, 99.0, 101.0, 200)),
        ("SC", candle(20, 102.0, 102.0, 99.0, 100.0, 200)),
        ("SV", candle(20, 100.5, 101.0, 99.5, 100.3, 160)),
    ],
)
def test_vsa_pattern_detection(event_type, bar):
    assert event_type in event_types(bar)


def test_vsa_context_confirms_long_near_support():
    bars = baseline() + [
        candle(20, 100.6, 100.7, 99.7, 100.4, 60),
        candle(21, 100.4, 101.1, 100.3, 101, 110),
    ]
    events = [event for event in detect_vsa_events(bars) if event.event_type == "NS"]
    support = level("SUP", "SUPPORT", 99.5, 100)
    out = validate_vsa_context(
        events,
        bars,
        levels=MTFLevelMap((support,)),
        mtf_regime=MTFRegimeSnapshot("BULLISH", {}, {}),
        atr14=Decimal("2"),
    )
    assert out[0].confirmed
    assert out[0].reference_level_id == "SUP"


def test_vsa_context_ignores_wrong_htf():
    bars = baseline() + [
        candle(20, 100.6, 100.7, 99.7, 100.4, 60),
        candle(21, 100.4, 101.1, 100.3, 101, 110),
    ]
    events = [event for event in detect_vsa_events(bars) if event.event_type == "NS"]
    support = level("SUP", "SUPPORT", 99.5, 100)
    out = validate_vsa_context(
        events,
        bars,
        levels=MTFLevelMap((support,)),
        mtf_regime=MTFRegimeSnapshot("BEARISH", {}, {}),
        atr14=Decimal("2"),
    )
    assert out[0].context_status == "IGNORED"
    assert out[0].invalidation_reason == "HTF_CONTEXT_MISMATCH"


def test_vsa_context_ignores_no_confirmed_level():
    bars = baseline() + [
        candle(20, 100.6, 100.7, 99.7, 100.4, 60),
        candle(21, 100.4, 101.1, 100.3, 101, 110),
    ]
    events = [event for event in detect_vsa_events(bars) if event.event_type == "NS"]
    out = validate_vsa_context(
        events,
        bars,
        levels=MTFLevelMap(()),
        mtf_regime=MTFRegimeSnapshot("BULLISH", {}, {}),
        atr14=Decimal("2"),
    )
    assert out[0].context_status == "IGNORED"
    assert out[0].invalidation_reason == "NO_CONFIRMED_LEVEL_LOCATION"


def test_vsa_context_waits_for_confirmation():
    bars = baseline() + [
        candle(20, 100.6, 100.7, 99.7, 100.4, 60),
        candle(21, 100.4, 100.6, 100.0, 100.5, 90),
    ]
    events = [event for event in detect_vsa_events(bars) if event.event_type == "NS"]
    support = level("SUP", "SUPPORT", 99.5, 100)
    out = validate_vsa_context(
        events,
        bars,
        levels=MTFLevelMap((support,)),
        mtf_regime=MTFRegimeSnapshot("BULLISH", {}, {}),
        atr14=Decimal("2"),
    )
    assert out[0].context_status == "VALID_CONTEXT"
    assert not out[0].confirmed
