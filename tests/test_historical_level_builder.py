from historical_level_builder import confirmed_pivots
def test_confirmation_not_early():
    b=[dict(open_ms=i,high=h,low=0) for i,h in enumerate([1,2,5,3,2])]
    levels=[x for x in confirmed_pivots(b,"1d") if x["kind"]=="resistance"]
    assert len(levels)==1
    assert levels[0]["pivot_open_ms"]==2
    assert levels[0]["confirmed_open_ms"]==4
def test_no_future_bars():
    b=[dict(open_ms=i,high=h,low=0) for i,h in enumerate([1,2,5,3])]
    assert confirmed_pivots(b,"1d")==[]
