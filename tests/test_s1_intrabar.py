"""Isolated S1 execution-path tests. No live orders."""
from decimal import Decimal as D
from ktrader.s1_intrabar import Order, replay

def bar(o,h,l,c):
    return dict(open=o,high=h,low=l,close=c)

def test_scenario_order_is_not_optimized():
    o=Order(1,D("100"),D("99"),D("103"))
    b=[bar(100,104,98,100)]
    assert replay(o,b,"A",D(0))["status"]=="TP"
    assert replay(o,b,"B",D(0))["status"]=="SL"

def test_no_future_early_touch():
    o=Order(1,D("99"),D("98"),D("101"))
    assert replay(o,[bar(100,102,99,102)],"A",D("0.9"))["status"]=="UNFILLED"

def test_open_position_is_censored():
    o=Order(1,D("100"),D("90"),D("110"))
    assert replay(o,[bar(100,102,99,101)],"A",D(0))["status"]=="CENSORED"

def test_gross_not_net():
    o=Order(1,D("100"),D("99"),D("103"))
    assert replay(o,[bar(100,104,98,100)],"A",D(0))["net_r"] is None

def test_bad_input_fails_closed():
    o=Order(1,D("100"),D("99"),D("103"))
    import pytest
    with pytest.raises(ValueError):
        replay(o,[bar(100,90,110,100)],"A",D(0))
