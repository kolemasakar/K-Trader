import json
import os
from pathlib import Path
import subprocess
import sys
from scripts.run_approved_backtest import code_manifest, logical_coordinates


def test_current_test_path_never_imports_scheduler():
    code='''
import sys
class RejectScheduler:
    def find_spec(self, fullname, path=None, target=None):
        if fullname == 'ktrader.approved_scheduler':
            raise AssertionError('scheduler imported')
sys.meta_path.insert(0, RejectScheduler())
from ktrader.approved_replay import run_model
from scripts.run_approved_backtest import logical_coordinates
assert run_model([], 'S1', lambda i,h: None, 'A') == []
assert 'ktrader.approved_scheduler' not in sys.modules
'''
    root=Path(__file__).resolve().parents[1]
    subprocess.run([sys.executable,'-c',code],cwd=root,
                   env={**os.environ,'PYTHONPATH':str(root/'src')},check=True)


def test_source_coordinates_keep_local_indices_and_require_no_calendar():
    record={'created_bar':2,'activation_fraction':'0.9','fill_bar':3,'exit_bar':5}
    r=logical_coordinates(record,100)
    assert r['created_bar']==2
    assert r['logical_coordinates']=={'basis':'SOURCE_M5_INDEX','created_bar':102,
        'activation_fraction':'0.9','fill_bar':103,'exit_bar':105}
    assert record=={'created_bar':2,'activation_fraction':'0.9','fill_bar':3,'exit_bar':5}


def test_code_identity_changes_when_implementation_changes(tmp_path,monkeypatch):
    import scripts.run_approved_backtest as runner
    (tmp_path/'scripts').mkdir();(tmp_path/'src/ktrader').mkdir(parents=True)
    p=tmp_path/'src/ktrader/example.py';p.write_text('value=1\n')
    monkeypatch.setattr(runner,'__file__',str(tmp_path/'scripts/run.py'))
    first=code_manifest(); assert first==code_manifest()
    p.write_text('value=2\n')
    assert first['sha256']!=code_manifest()['sha256']
