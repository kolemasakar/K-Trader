import importlib.util
from pathlib import Path
import pytest

spec=importlib.util.spec_from_file_location("gradient",Path(__file__).resolve().parents[1]/"scripts/research/structural_gradient_zones_v1.py")
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)

def p(price,known,identity):
    return {"kind":"support","price":price,"pivot_open_ms":known,
            "confirmed_close_ms":known,"independent_event_id":identity}

def test_gradient_edges_and_center():
    z=m.geometry([p(100,10,"a"),p(102,20,"b")],30)
    assert (z["low"],z["center"],z["high"])==(100,101,102)
    assert m.gradient(z,100)==0 and m.gradient(z,101)==1 and m.gradient(z,102)==0
    assert m.gradient(z,100.5)==pytest.approx(.5)
    assert m.gradient(z,101.5)==pytest.approx(.5)

def test_singleton_zero_width_not_artificially_expanded():
    z=m.geometry([p(100,10,"a")],10)
    assert z["low"]==z["high"]==100
    assert m.gradient(z,100)==1 and m.gradient(z,100.1)==0

def test_same_event_and_future_confirmation():
    a=p(100,10,"a");w=p(100,50,"a");future=p(102,70,"b")
    z=m.geometry([a,w,future],60)
    assert z["independent_event_count"]==1
    assert z["low"]==z["high"]==100

def test_stable_id_and_revisions():
    a=p(100,10,"a");b=p(102,20,"b")
    z=m.geometry([a],10)
    z2=m.revise(z,[a,b],20)
    assert z["zone_id"]==z2["zone_id"] and z2["revision"]==1
    assert z2["previous_geometry"]["center"]==100
    with pytest.raises(ValueError):m.revise(z2,[b],30)

def test_invalid_inputs():
    with pytest.raises(ValueError):m.geometry([p(0,10,"a")],10)
    with pytest.raises(ValueError):m.gradient({"low":101,"center":100,"high":102},100)
