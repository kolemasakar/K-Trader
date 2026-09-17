import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "phase11g_replay_consistency.py"


def dump(path, rows):
    path.write_text("\n".join(json.dumps(r) for r in rows) + "\n")


def run(prior, current):
    return subprocess.run([sys.executable, str(SCRIPT), "--prior", str(prior), "--current", str(current)], capture_output=True, text=True)


def test_resolved_prior_family_is_immutable(tmp_path):
    row = {"setup_family_id":"f1","resolved":True,"primary_symbol":"ADAUSDT","primary_side":"SHORT","primary_entry_time":"2026-09-16T13:15:00Z","terminal_state":"STOP","realized_R":-1.08,"mfe_R":0.2,"mae_R":1.1}
    a=tmp_path/"a.jsonl"; b=tmp_path/"b.jsonl"; dump(a,[row]); dump(b,[row])
    p=run(a,b); assert p.returncode==0; assert json.loads(p.stdout)["status"]=="PASS"


def test_changed_terminal_fails_closed(tmp_path):
    old = {"setup_family_id":"f1","resolved":True,"primary_symbol":"ADAUSDT","primary_side":"SHORT","primary_entry_time":"2026-09-16T13:15:00Z","terminal_state":"STOP","realized_R":-1.08,"mfe_R":0.2,"mae_R":1.1}
    new = dict(old); new["terminal_state"]="TARGET"
    a=tmp_path/"a.jsonl"; b=tmp_path/"b.jsonl"; dump(a,[old]); dump(b,[new])
    p=run(a,b); assert p.returncode==2; assert json.loads(p.stdout)["status"]=="FAIL_CLOSED"
