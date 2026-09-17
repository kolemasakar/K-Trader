from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
import json
import subprocess, sys

P=Path(__file__).parents[1]/"scripts"/"phase11g_data_quality_watchdog.py"
spec=spec_from_file_location("dq",P); m=module_from_spec(spec); spec.loader.exec_module(m)


def write_bundle(root, bad=False):
    sym=root/"AAAUSDT"; sym.mkdir(parents=True)
    steps={"5m":300,"15m":900,"1h":3600,"4h":14400,"1d":86400}
    base=1_789_595_200  # 2026-09-17T00:00:00Z
    for tf,step in steps.items():
        vals=[base-2*step,base-step]
        if bad and tf=="15m": vals=[base-step,base-step]
        (sym/f"{tf}.jsonl").write_text("".join(json.dumps({"timestamp":v})+"\n" for v in vals))


def test_good_bundle_passes(tmp_path):
    write_bundle(tmp_path)
    rc=m.main if False else None
    p=subprocess.run([sys.executable,str(P),str(tmp_path),"--as-of","2026-09-17T00:15:00Z"],capture_output=True,text=True)
    assert p.returncode==0; assert '"status": "PASS"' in p.stdout


def test_duplicate_timestamp_fails_closed(tmp_path):
    write_bundle(tmp_path,bad=True)
    p=subprocess.run([sys.executable,str(P),str(tmp_path),"--as-of","2026-09-17T00:15:00Z"],capture_output=True,text=True)
    assert p.returncode==2; assert "DUPLICATE_TIMESTAMP" in p.stdout; assert '"status": "FAIL_CLOSED"' in p.stdout
