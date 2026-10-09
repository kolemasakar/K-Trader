from decimal import Decimal as D
import pytest
from ktrader.s1_atr5 import ATRUnavailable,filtered_atr5

def bars(ranges):
    return [{"high":str(x),"low":"0"} for x in ranges]

def test_five_normal_bars():
    assert filtered_atr5(bars([10,11,9,10,10]))==D(10)

def test_outlier_replaced_from_older_history():
    v=filtered_atr5(bars([10,10,10,10,10,10,100]))
    assert v==D(10)

def test_insufficient_history_blocks():
    with pytest.raises(ATRUnavailable):
        filtered_atr5(bars([10,10,10]))
