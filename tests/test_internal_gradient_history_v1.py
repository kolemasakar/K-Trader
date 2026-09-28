import importlib.util
from pathlib import Path
import pytest

ROOT=Path(__file__).resolve().parents[1]/"scripts/research"
def load(name):
    spec=importlib.util.spec_from_file_location(name,ROOT/(name+".py"))
    m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
g=load("structural_gradient_zones_v1")
h=load("internal_gradient_history_v1")
D=86400000
def bar(i,close=100,high=101,low=99):
    return {"t":i*D,"close_t":(i+1)*D-1,"o":close,"h":high,"l":low,"c":close,"v":1}
def pivot(price,at,known,kind="support"):
    return {"tf":"1d","kind":kind,"price":price,"pivot_open_ms":at*D,
            "confirmed_close_ms":(known+1)*D-1}

def test_no_future_pivots_and_no_singleton_reaction():
    daily=[bar(i) for i in range(20)]
    r=h.run(daily,[pivot(100,2,50)],g,horizon=2)
    assert r["zones_created"]==0 and not r["observations"]

def test_stable_zone_revisions_and_no_duplicate_touch():
    daily=[bar(i) for i in range(25)]
    # Strictly descriptive synthetic pivots: test the event ledger, not pivot detector.
    daily[7]["c"]=101
    daily[8]["c"]=101
    r=h.run(daily,[pivot(100,2,4),pivot(102,3,6)],g,band=.03,horizon=2)
    assert r["zones_created"]==1 and r["geometry_revisions"]==1
    assert len(r["observations"])<=1

def test_reject_invalid_band():
    with pytest.raises(ValueError):
        h.run([],[],g,band=0)
