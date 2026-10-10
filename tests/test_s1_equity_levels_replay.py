from ktrader.s1_equity_levels_replay import candidate_levels

def candle(date, high=105, low=99):
    return {"open_time":date+"T00:00:00","close_time":date+"T23:59:59",
            "open":100,"high":high,"low":low,"close":101,"closed":True}

def test_equity_replay_reuses_detectors_without_review_claim():
    x=candidate_levels([candle("2026-09-29"),candle("2026-09-30"),
                        candle("2026-10-01"),candle("2026-10-02"),
                        candle("2026-10-05"),candle("2026-10-06")])
    assert x["daily_bars"]==6
    assert x["closed_weekly_bars"]==1
    assert x["level_evidence_status"]=="AUTOMATED_RESEARCH_CANDIDATE_NOT_REVIEWED"
