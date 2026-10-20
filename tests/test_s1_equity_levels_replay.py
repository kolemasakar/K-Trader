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

def test_weekly_availability_is_not_backdated(monkeypatch):
    import ktrader.s1_equity_levels_replay as module
    from datetime import datetime,timezone
    def detector(rows,tf,*args,**kwargs):
        if tf=='D1':return []
        return [dict(known_at_ms=rows[0][6]+1,confirmation_index=0,additional_patterns=[])]
    monkeypatch.setattr(module,'detect_existing_levels',detector)
    data=[candle('2026-10-01'),candle('2026-10-02'),candle('2026-10-05')]
    report=module.candidate_levels(data)
    expected=int(datetime.fromisoformat(data[-1]['close_time']).replace(tzinfo=timezone.utc).timestamp()*1000)
    assert report['W1'][0]['known_at_ms']==expected
