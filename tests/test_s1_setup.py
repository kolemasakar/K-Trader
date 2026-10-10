from decimal import Decimal as D
from ktrader.s1_setup import Bar, trend, activity, inspect_readiness

def b(h,l=1):
    return Bar(D(2),D(h),D(l),D(2))

def test_unknown_trend_without_confirmations():
    assert trend([b(3)]*10)=="UNKNOWN"

def test_activity_requires_full_20():
    assert activity([b(3)]*19,b(3)) is None

def test_no_unreviewed_levels():
    x=inspect_readiness([b(3)]*30,[b(3)]*30,[b(3)]*30)
    assert not x["eligible"]
    assert "NO_APPROVED_REVIEWED_LEVELS" in x["reasons"]

from ktrader.s1_setup import causal_candidate

def test_unreviewed_level_never_eligible():
    p=[b(3)]*20
    x=causal_candidate(level=1,side=1,bpu1=b(3),bpu2_observed=b(3),
       previous20=p,last_closed_m5=b(3),
       confirmed_d1="DOWN",confirmed_h1="DOWN",confirmed_m5="DOWN",
       level_is_reviewed=False,strengthening_confirmed=False,
       filtered_atr5=D(2),broker_point=D(".01"),tick_size=D(".01"),session_status="UNKNOWN")
    assert not x["eligible"]
    assert "UNVERIFIED_LEVEL_OR_STRENGTH" in x["reasons"]
    assert x["session_verified"] is False

def test_large_bpu2_rejected():
    p=[b(3)]*20
    x=causal_candidate(level=1,side=1,bpu1=b(3),bpu2_observed=b(10),
       previous20=p,last_closed_m5=b(3),
       confirmed_d1="DOWN",confirmed_h1="DOWN",confirmed_m5="DOWN",
       level_is_reviewed=True,strengthening_confirmed=True,
       filtered_atr5=D(10),broker_point=D(".01"),tick_size=D(".01"),session_status="PASS")
    assert "BPU2_TOO_LARGE" in x["reasons"]
