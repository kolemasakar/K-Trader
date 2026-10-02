import importlib.util
from pathlib import Path
import pytest

spec=importlib.util.spec_from_file_location("clusters",Path(__file__).resolve().parents[1]/"scripts/research/structural_level_clusters_v1.py")
mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)

def pivot(price,t,tf="1d",kind="support"):
    return {"price":price,"confirmed_close_ms":t,"tf":tf,"kind":kind}

def test_no_future_levels_or_lookahead():
    x=mod.cluster_confirmed([pivot(100,100),pivot(100.1,200)],100)
    assert len(x)==1 and x[0]["pivot_count"]==1

def test_d1_w1_cluster():
    x=mod.cluster_confirmed([pivot(100,100),pivot(100.2,200,"1w")],300)
    assert len(x)==1 and x[0]["pivot_count"]==2
    assert x[0]["timeframes"]==["1d","1w"]

def test_no_chain_merge():
    x=mod.cluster_confirmed([pivot(100,100),pivot(100.2,200),pivot(100.4,300)],400)
    assert len(x)==2

def test_resistance_and_support_separate():
    x=mod.cluster_confirmed([pivot(100,100),pivot(100.1,200,kind="resistance")],300)
    assert len(x)==2

def test_lower_tf_prohibited_even_when_future():
    with pytest.raises(ValueError):
        mod.cluster_confirmed([pivot(100,400,"1h")],300)
