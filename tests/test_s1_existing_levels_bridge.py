import pytest
from ktrader.s1_existing_levels_bridge import detect_existing_levels, ExistingLevelEngineUnavailable

def test_us_equity_does_not_get_crypto_calendar():
    with pytest.raises(ExistingLevelEngineUnavailable, match="unsupported"):
        detect_existing_levels([], "D1", None, asset_class="us_equity", calendar="BROKER_WALL_CLOCK")


def test_us_equity_session_daily_bars_supported():
    from scripts.research.gerchik_seven_types_v0_1 import ResearchPolicy
    ms=86400000
    # Intentional gap between daily sessions, all source bars closed and ordered.
    starts=[0,ms,4*ms]
    rows=[[t,"100","105","99","101","0",t+ms-1] for t in starts]
    policy=ResearchPolicy(provenance="explicit synthetic test",directional_transitions=2,
       trend_defenses=2,historical_repetitions=2,mirror_defenses=2,
       paranormal_reference_bars=2,paranormal_multiple="2",
       calendar="US_EQUITY_SESSION_WALL_CLOCK")
    result=detect_existing_levels(rows,"D1",policy,asset_class="us_equity",calendar=policy.calendar)
    assert isinstance(result,list)
