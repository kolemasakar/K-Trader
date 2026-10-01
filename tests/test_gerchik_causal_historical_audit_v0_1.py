"""Causal audit: no future pivots, one ATR attempt per historical cutoff."""
from datetime import datetime, timedelta, timezone
import pytest
from scripts.research import gerchik_causal_historical_audit_v0_1 as audit

DAY = 86400000

def bars(n):
    start = int(datetime(2026, 1, 1, tzinfo=timezone.utc).timestamp()*1000)
    return [dict(t=start+i*DAY,close_t=start+(i+1)*DAY-1,
                 o=100.,h=102.+(i%3)*0.1,l=99.,c=100.,v=1.)
            for i in range(n)]

def test_every_closed_cutoff_and_future_pivot_visibility(tmp_path, monkeypatch):
    source=tmp_path/'1d.jsonl'
    source.write_text('isolated fixture')
    daily=bars(14)
    monkeypatch.setattr(audit,'native_d1',lambda path: daily)
    monkeypatch.setattr(audit,'complete_w1',lambda rows: [])
    monkeypatch.setattr(audit,'pivots',lambda rows,tf:[
        dict(tf=tf,kind='support',price=99.,
             confirmed_close_ms=daily[8]['close_t'])] if tf=='1d' else [])
    result=audit.audit_symbol(source)
    assert result['d1_bars']==14
    assert result['atr5_valid_cutoffs']+result['atr5_insufficient_cutoffs']==14
    assert result['exploratory_d1_pivots']==1
    assert result['status']=='CAUSAL_DIAGNOSTIC_NOT_LEVEL_QUALITY_VALIDATION'

def test_future_confirmed_event_rejected(tmp_path, monkeypatch):
    source=tmp_path/'1d.jsonl'
    source.write_text('isolated fixture')
    daily=bars(8)
    monkeypatch.setattr(audit,'native_d1',lambda path: daily)
    monkeypatch.setattr(audit,'complete_w1',lambda rows: [])
    monkeypatch.setattr(audit,'pivots',lambda rows,tf:[
        dict(tf=tf,kind='support',price=99.,
             confirmed_close_ms=daily[-1]['close_t']+DAY)] if tf=='1d' else [])
    with pytest.raises(ValueError,match='outside available'):
        audit.audit_symbol(source)


def test_real_pivot_detector_is_prefix_stable():
    from scripts.research.internal_level_structure_diagnostics_v1 import pivots
    rows = bars(20)
    # Introduce deterministic strict highs/lows, with confirmation after 3 closes.
    for i, row in enumerate(rows):
        row["h"] = 120. if i in (4, 12) else 100. + (i % 2)
        row["l"] = 80. if i in (7, 16) else 90. - (i % 2)
    full = pivots(rows, "1d")
    for n in range(1, len(rows) + 1):
        cutoff = rows[n - 1]["close_t"]
        visible = [e for e in full if e["confirmed_close_ms"] <= cutoff]
        assert pivots(rows[:n], "1d") == visible


def test_audit_rejects_confirmed_pivot_before_source(tmp_path, monkeypatch):
    source = tmp_path / "1d.jsonl"
    source.write_text("isolated fixture")
    daily = bars(8)
    monkeypatch.setattr(audit, "native_d1", lambda path: daily)
    monkeypatch.setattr(audit, "complete_w1", lambda rows: [])
    monkeypatch.setattr(audit, "pivots", lambda rows, tf: [dict(
        tf=tf, kind="support", price=99.,
        confirmed_close_ms=daily[0]["close_t"] - DAY)] if tf == "1d" else [])
    with pytest.raises(ValueError, match="outside available"):
        audit.audit_symbol(source)


def test_complete_w1_pivots_are_prefix_stable_across_daily_cutoffs():
    from scripts.research.native_internal_d1_w1_v1 import complete_w1
    from scripts.research.internal_level_structure_diagnostics_v1 import pivots
    # Monday-aligned synthetic daily history, including a partial final week.
    monday = int(datetime(2026, 1, 5, tzinfo=timezone.utc).timestamp() * 1000)
    daily = []
    for i in range(7 * 13 + 3):
        week = i // 7
        high = 130. if week == 4 else 110. + week % 2
        low = 70. if week == 8 else 90. - week % 2
        daily.append(dict(t=monday+i*DAY, close_t=monday+(i+1)*DAY-1,
                          o=100., h=high, l=low, c=100., v=1.))
    full = pivots(complete_w1(daily), "1w")
    assert full, "Fixture must contain at least one confirmed weekly pivot"
    for n in range(1, len(daily)+1):
        cutoff = daily[n-1]["close_t"]
        visible = [e for e in full if e["confirmed_close_ms"] <= cutoff]
        assert pivots(complete_w1(daily[:n]), "1w") == visible
    # The last three daily bars cannot create an unfinished W1 candle.
    assert complete_w1(daily) == complete_w1(daily[:-3])
