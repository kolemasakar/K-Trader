from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
import json

P=Path(__file__).parents[1]/"scripts"/"phase11g_pause_runner.py"
spec=spec_from_file_location("pause_runner",P); m=module_from_spec(spec); spec.loader.exec_module(m)


def state(as_of="2026-09-17T01:15:00Z", resolved=48, unresolved=1):
    return {
        "status":"PASS", "strategy_id":"candidate_rule_set_v2_2", "resolver_version":"v1.3",
        "holdout_opened":False, "production_action":False, "unique_families":resolved+unresolved,
        "resolved_primary_families":resolved, "unresolved_primary_families":unresolved, "as_of":as_of,
    }


def test_floor_m15():
    assert m.iso_z(m.floor_m15(m.parse_utc("2026-09-17T01:29:59Z"))) == "2026-09-17T01:15:00Z"


def test_accept_reject_state(tmp_path):
    p=tmp_path/"state.json"; p.write_text(json.dumps(state()))
    assert m.accepted_state(p) is not None
    s=state(); s["holdout_opened"]=True; p.write_text(json.dumps(s)); assert m.accepted_state(p) is None
    s=state(); s["production_action"]=True; p.write_text(json.dumps(s)); assert m.accepted_state(p) is None


def test_latest_accepted_skips_bad_newer(tmp_path):
    good=tmp_path/"20260917T011500Z.json"; good.write_text(json.dumps(state()))
    bad=tmp_path/"20260917T013000Z.json"; s=state("2026-09-17T01:30:00Z"); s["status"]="FAIL"; bad.write_text(json.dumps(s))
    p,s=m.latest_accepted(tmp_path); assert p==good; assert s["as_of"]=="2026-09-17T01:15:00Z"


def test_runtime_manifest_verification(tmp_path):
    root=tmp_path/"runtime"; root.mkdir(); f=root/"x.py"; f.write_text("print('ok')\n")
    manifest=tmp_path/"manifest.json"; manifest.write_text(json.dumps({"root":str(root),"files":{"x.py":m.sha256(f)}}))
    m.verify_manifest(manifest)
    f.write_text("changed\n")
    try: m.verify_manifest(manifest)
    except RuntimeError: pass
    else: raise AssertionError("manifest mismatch must fail closed")


def test_pipeline_command_is_execute_and_sequential(tmp_path):
    runtime=tmp_path/"rt"; prior=tmp_path/"prior"
    cmd=m.build_pipeline_command(runtime,m.parse_utc("2026-09-17T01:30:00Z"),prior,"2026-09-16T13:00:00Z")
    assert "--execute" in cmd; assert "--prior-outcomes" in cmd; assert str(prior) in cmd; assert "--script-dir" in cmd
