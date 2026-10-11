"""Synthetic deterministic checks for ATR-free research validation."""
import importlib.util
from pathlib import Path

spec=importlib.util.spec_from_file_location("validator",Path(__file__).resolve().parents[1]/"scripts/research/atr_free_level_validation_v1.py")
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)

def bars(highs):
    return [dict(t=i*86400000,h=float(h),l=float(h)-1,c=float(h)-.5,
                 v=1.,close_t=(i+1)*86400000-1) for i,h in enumerate(highs)]

def test_pivot_requires_three_right_completed_bars():
    h=[10]*25+[11,12,13,19,13,12,11]+[10]*40
    b=bars(h)
    p=[x for x in m.pivots(b) if x["side"]=="R" and x["price"]==19]
    assert len(p)==1
    assert p[0]["known"]==31
    assert p[0]["known_close_t"]==b[31]["close_t"]

def test_no_lookahead_at_end():
    b=bars([10]*25+[11,12,13,19])
    assert not any(x["price"]==19 for x in m.pivots(b))

def test_random_baseline_deterministic_and_prior_only():
    b=bars([10+(i%4) for i in range(90)])
    e=[dict(i=30,known=33,known_close_t=b[33]["close_t"],side="R",price=13.,anomaly=True)]
    a=m.random_controls(b,e)
    assert a==m.random_controls(b,e)
    assert b[14]["l"]<=a[0]["price"]<=max(x["h"] for x in b[14:34])
