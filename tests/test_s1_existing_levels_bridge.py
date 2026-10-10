import pytest
from ktrader.s1_existing_levels_bridge import detect_existing_levels, ExistingLevelEngineUnavailable

def test_us_equity_does_not_get_crypto_calendar():
    with pytest.raises(ExistingLevelEngineUnavailable, match="session-aware"):
        detect_existing_levels([], "D1", None, asset_class="us_equity", calendar="BROKER_WALL_CLOCK")
