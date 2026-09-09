from datetime import datetime, timedelta, timezone

import pytest

from ktrader.engine.service import setup_is_expired
from ktrader.runtime.models import RuntimeScannerConfig, setup_interval_seconds


UTC = timezone.utc


def test_runtime_setup_expiry_defaults_to_60_minutes() -> None:
    config = RuntimeScannerConfig()
    assert config.setup_interval == "5m"
    assert config.setup_max_age_bars == 12
    assert config.setup_max_age_seconds == 3600


def test_runtime_setup_expiry_supports_research_timeframes() -> None:
    intraday = RuntimeScannerConfig(setup_interval="15m", setup_max_age_bars=16)
    medium = RuntimeScannerConfig(setup_interval="1h", setup_max_age_bars=8)

    assert setup_interval_seconds("15m") == 900
    assert intraday.setup_max_age_seconds == 4 * 60 * 60
    assert medium.setup_max_age_seconds == 8 * 60 * 60


def test_runtime_setup_expiry_rejects_unsupported_setup_interval() -> None:
    with pytest.raises(ValueError, match="unsupported setup_interval"):
        RuntimeScannerConfig(setup_interval="30m")


def test_runtime_setup_expiry_requires_setup_interval_in_history_plan() -> None:
    from ktrader.market.bootstrap import HistoryPlan

    with pytest.raises(ValueError, match="setup_interval must be present in history plan"):
        RuntimeScannerConfig(
            setup_interval="15m",
            history=HistoryPlan({"1d": 250, "4h": 250, "1h": 250, "5m": 300}),
        )


def test_runtime_setup_expiry_requires_positive_bar_count() -> None:
    with pytest.raises(ValueError, match="setup_max_age_bars must be positive"):
        RuntimeScannerConfig(setup_max_age_bars=0)


def test_setup_expiry_boundary_is_strictly_greater_than_60_minutes() -> None:
    confirmation = datetime(2026, 9, 9, 12, 0, tzinfo=UTC)

    assert not setup_is_expired(
        confirmation,
        generated_at=confirmation + timedelta(minutes=60),
        max_age_seconds=3600,
    )
    assert setup_is_expired(
        confirmation,
        generated_at=confirmation + timedelta(minutes=60, microseconds=1),
        max_age_seconds=3600,
    )


def test_setup_expiry_boundary_semantics_are_profile_independent() -> None:
    confirmation = datetime(2026, 9, 9, 12, 0, tzinfo=UTC)
    config = RuntimeScannerConfig(setup_interval="15m", setup_max_age_bars=16)

    assert not setup_is_expired(
        confirmation,
        generated_at=confirmation + timedelta(hours=4),
        max_age_seconds=config.setup_max_age_seconds,
    )
    assert setup_is_expired(
        confirmation,
        generated_at=confirmation + timedelta(hours=4, microseconds=1),
        max_age_seconds=config.setup_max_age_seconds,
    )


def test_setup_expiry_rejects_invalid_age_context() -> None:
    confirmation = datetime(2026, 9, 9, 12, 0, tzinfo=UTC)

    with pytest.raises(ValueError, match="max_age_seconds must be positive"):
        setup_is_expired(confirmation, generated_at=confirmation, max_age_seconds=0)

    with pytest.raises(ValueError, match="setup confirmation cannot be in the future"):
        setup_is_expired(
            confirmation,
            generated_at=confirmation - timedelta(seconds=1),
            max_age_seconds=3600,
        )
