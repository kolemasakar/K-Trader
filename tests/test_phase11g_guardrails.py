from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path

P=Path(__file__).parents[1]/"scripts"/"phase11g_guardrails.py"
spec=spec_from_file_location("guardrails",P); m=module_from_spec(spec); spec.loader.exec_module(m)

def state(n=48):
    return {"status":"PASS","strategy_id":"candidate_rule_set_v2_2","resolver_version":"v1.3","holdout_opened":False,"production_action":False,"unique_families":n,"resolved_primary_families":n,"unresolved_primary_families":0,"as_of":"2026-09-16T21:15:00Z"}

def test_current_tier_and_shortfall():
    r=m.evaluate(state()); assert r["status"]=="PASS"; assert r["closure_path_a_shortfall"]==52; assert r["evidence_tier"]=="DIAGNOSTIC_30_49"

def test_50_and_100_boundaries():
    assert m.evaluate(state(50))["evidence_tier"]=="HYPOTHESES_ABLATION_50_99"; assert m.evaluate(state(100))["closure_path_a_shortfall"]==0

def test_fail_closed_on_holdout_or_production():
    s=state(); s["holdout_opened"]=True; assert m.evaluate(s)["status"]=="FAIL_CLOSED"
    s=state(); s["production_action"]=True; assert m.evaluate(s)["status"]=="FAIL_CLOSED"
