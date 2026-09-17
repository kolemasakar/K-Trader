import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "phase11g_pause_preflight.py"


def write(path, value):
    path.write_text(json.dumps(value))
    return path


def base_docs(tmp_path):
    as_of = "2026-09-17T01:15:00Z"
    state = {"as_of": as_of, "status": "PASS", "strategy_id": "candidate_rule_set_v2_2", "resolver_version": "v1.3", "holdout_opened": False, "production_action": False, "unique_families": 49, "resolved_primary_families": 48, "unresolved_primary_families": 1, "confirmation_family_count": 5}
    outcomes = {"as_of": as_of, "strategy_id": "candidate_rule_set_v2_2", "resolver_version": "v1.3", "holdout_opened": False, "production_action": False, "network_used": False}
    evidence = {"as_of": as_of, "status": "PASS", "holdout_opened": False, "production_action": False, "network_used": False, "prereg_boundary": "2026-09-16T13:00:00Z"}
    risk = {"as_of": as_of, "status": "PASS", "holdout_opened": False, "production_action": False, "diagnostic_only": True, "production_enforcement": False}
    return [write(tmp_path / f"{name}.json", value) for name, value in (("state", state), ("outcomes", outcomes), ("evidence", evidence), ("risk", risk))]


def run(paths):
    return subprocess.run([sys.executable, str(SCRIPT), "--state", str(paths[0]), "--outcomes", str(paths[1]), "--evidence", str(paths[2]), "--risk", str(paths[3])], capture_output=True, text=True)


def test_pause_preflight_passes_valid_state(tmp_path):
    proc = run(base_docs(tmp_path))
    assert proc.returncode == 0
    report = json.loads(proc.stdout)
    assert report["status"] == "PASS"
    assert report["data_collection_authorized"] is True
    assert report["production_trading_authorized"] is False


def test_pause_preflight_fails_open_holdout(tmp_path):
    paths = base_docs(tmp_path)
    state = json.loads(paths[0].read_text())
    state["holdout_opened"] = True
    paths[0].write_text(json.dumps(state))
    proc = run(paths)
    assert proc.returncode == 2
    assert json.loads(proc.stdout)["status"] == "FAIL_CLOSED"
