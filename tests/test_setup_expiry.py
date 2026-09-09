from datetime import datetime, timedelta, timezone

import pytest

from ktrader.engine.service import setup_is_expired
from ktrader.runtime.models import RuntimeScannerConfig


UTC = timezone.utc


def test_runtime_setup_expiry_defaults_to_60_minutes() -> None:
    config = RuntimeScannerConfig()
    assert config.setup_interval == "5m"
    assert config.setup_max_age_bars == 12
    assert config.setup_max_age_bars * 5 * 60 == 3600


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
