from ktrader.s1_equity_level_rows import completed_daily,completed_weekly

def day(date):
    return dict(open_time=date+"T00:00:00",close_time=date+"T23:59:59",
                open=100,high=105,low=99,close=101,closed=True,volume=1)

def test_session_gaps_do_not_imply_missing_d1():
    rows=completed_daily([day("2026-10-02"),day("2026-10-05")])
    assert len(rows)==2 and rows[0][6]<rows[1][0]

def test_weekly_requires_next_week_observation():
    rows=completed_weekly([day("2026-10-01"),day("2026-10-02"),day("2026-10-05")])
    assert len(rows)==1
    assert rows[0][2]=="105" and rows[0][3]=="99"

def test_weekly_incomplete_latest_excluded():
    assert completed_weekly([day("2026-10-01"),day("2026-10-02")])==[]
