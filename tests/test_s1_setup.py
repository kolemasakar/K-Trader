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
