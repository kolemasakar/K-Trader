"""The runner never turns incomplete readiness into strategy results."""
import json
from ktrader.s1_research_runner import main
from test_mt4_research import make_source

def test_runner_fails_closed(tmp_path,capsys):
    root=make_source(tmp_path)
    code=main(["--root",str(root),"--symbol","SUIUSDt","--as-of","2026-01-01T00:10:00"])
    assert code==2
    result=json.loads(capsys.readouterr().out)
    assert result["run_kind"]=="READ_ONLY_S1_READINESS_NOT_BACKTEST"
    assert result["trades"] is None and result["returns"] is None
    assert "NO_APPROVED_REVIEWED_LEVELS" in result["reasons"]
