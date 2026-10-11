"""Archived algorithm regression; preserved but excluded from active CI."""
import pytest
pytest.skip("ARCHIVED_LEVEL_ALGORITHM_DO_NOT_USE", allow_module_level=True)

import importlib.util
from pathlib import Path
import pytest
p=Path(__file__).resolve().parents[1]/"scripts/research"
def load(name):
    spec=importlib.util.spec_from_file_location(name,p/(name+".py"))
    m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
g=load("structural_gradient_zones_v1")
v=load("internal_extreme_zone_rebuild_v2")
D=86400000
def bar(i,lo=90,hi=110):
    return {"t":i*D,"close_t":(i+1)*D-1,"o":100,"h":hi,"l":lo,"c":100,"v":1}
def pivot(price,day,confirm,kind="support"):
    return {"tf":"1d","kind":kind,"price":price,"pivot_open_ms":day*D,
            "confirmed_close_ms":(confirm+1)*D-1}
def identity(p,daily):
    return (p["kind"],p["pivot_open_ms"],p["price"])
def test_levels_use_confirmed_extremes_not_close():
    daily=[bar(i) for i in range(15)]
    x=v.rebuild(daily,[pivot(100,1,3),pivot(100.2,2,4)],g,identity,band=.003,horizon=2)
    assert x["independent_extremes"]==2
    assert x["zones_created"]==1 and x["geometry_revisions"]==1
    assert x["changes"][0]["new_high"]==100.2
def test_first_range_contact_can_overshoot():
    daily=[bar(i,lo=110,hi=120) for i in range(15)]
    daily[5]=bar(5,lo=95,hi=110)
    x=v.rebuild(daily,[pivot(100,1,3)],g,identity,horizon=2)
    assert x["counts"]["first_contacts"]==1
    assert x["counts"]["extreme_below"]==1
    assert x["observations"][0]["directional_extreme"]==95
def test_future_confirmation_never_backdates():
    daily=[bar(i) for i in range(15)]
    x=v.rebuild(daily,[pivot(100,1,20)],g,identity,horizon=2)
    assert x["zones_created"]==0 and not x["observations"]
def test_lower_tf_rejected():
    daily=[bar(i) for i in range(15)]
    bad=pivot(100,1,3);bad["tf"]="15m"
    with pytest.raises(ValueError):v.rebuild(daily,[bad],g,identity)
