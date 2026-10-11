"""Experimental v3 tests; no change to approved v2."""
from datetime import date,timedelta
from scripts.research.gerchik_filtered_atr5_v1 import DailyBar,filtered_atr5
from scripts.research.gerchik_adaptive_atr5_v3_experiment import adaptive_atr5_v3

def bars(spans):
    start=date(2026,9,30)
    return [DailyBar((start-timedelta(days=i)).isoformat(),float(s),0.)
            for i,s in enumerate(spans)]

def test_one_spike_does_not_confirm_regime():
    r=adaptive_atr5_v3(bars([100,10,10]+[10]*20))
    assert not r["regime_confirmed"]
    assert r["status"]=="V2_BASELINE"

def test_three_new_bars_confirm_but_five_required_for_atr():
    r=adaptive_atr5_v3(bars([50]*3+[10]*20))
    assert r["status"]=="NEW_REGIME_WARMUP"
    assert r["atr5"] is None
    assert r["regime_bars"]==3

def test_five_new_bars_form_local_atr_without_old_bars():
    r=adaptive_atr5_v3(bars([50]*5+[10]*20))
    assert r["status"]=="NEW_REGIME_READY"
    assert r["atr5"]==50
    assert r["regime_bars"]==5

def test_contraction_and_no_future_bar():
    r=adaptive_atr5_v3(bars([10]*5+[50]*20))
    assert r["direction"]=="CONTRACTION"
    assert r["atr5"]==10

def test_unmodified_v2_remains_available():
    data=bars([50]*5+[10]*20)
    before=filtered_atr5(data)
    adaptive_atr5_v3(data)
    assert filtered_atr5(data)==before
