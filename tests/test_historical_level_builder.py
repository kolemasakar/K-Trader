import importlib.util
from pathlib import Path
import pytest

spec=importlib.util.spec_from_file_location("historical_level_builder",Path(__file__).resolve().parents[1]/"scripts/research/historical_level_builder.py")
mod=importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
confirmed_pivots=mod.confirmed_pivots

def candles(highs):
    return [dict(open_ms=i*100,close_ms=i*100+99,high=h,low=0) for i,h in enumerate(highs)]

def test_confirmation_only_at_rightmost_candle_close():
    b=candles([1,2,3,9,4,3,2])
    levels=[x for x in confirmed_pivots(b,"1d") if x["kind"]=="resistance"]
    assert len(levels)==1
    assert levels[0]["pivot_open_ms"]==300
    assert levels[0]["confirmed_close_ms"]==699

def test_no_future_bars():
    assert confirmed_pivots(candles([1,2,3,9,4,3]),"1d")==[]

def test_reject_lower_timeframe():
    with pytest.raises(ValueError):
        confirmed_pivots(candles([1,2,3,9,4,3,2]),"1h")

def test_reject_overlapping_source(tmp_path):
    p=tmp_path/"1d.jsonl"
    import json
    p.write_text("\n".join(json.dumps(x) for x in [
        [0,"1","2","0","1","1",200],
        [100,"1","2","0","1","1",199]])+"\n")
    with pytest.raises(ValueError):
        mod.read_bars(p)

def test_builder_d1_only_when_w1_missing(tmp_path):
    import json
    d=tmp_path/"BTCUSDT";d.mkdir()
    rows=[[i*100,"1",str(h),"0","1","1",i*100+99]
          for i,h in enumerate([1,2,3,9,4,3,2])]
    (d/"1d.jsonl").write_text("\n".join(map(json.dumps,rows))+"\n")
    out=mod.build(tmp_path,"CRYPTO","BTCUSDT")
    assert {x["tf"] for x in out["levels"]}=={"1d"}
    assert out["status"]=="D1_W1_PIVOTS_ONLY_UNMERGED_NO_ATR"
