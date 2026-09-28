import pytest
from scripts.research.gerchik_reviewed_historical_pipeline_v0_1 import reviewed_historical_candidates

def bundle(eid, barid, day):
    return {'event': {'event_id':eid,'symbol':'SUIUSDT','timeframe':'1d',
                      'source_field':'high','source_bar_id':barid,'price':'2.125',
                      'tick_size':'0.001','observed_at':day+'T00:00:00Z'},
            'source_bar': {'bar_id':barid,'symbol':'SUIUSDT','timeframe':'1d',
                           'high':'2.125','low':'2.000','closed_at':day+'T00:00:00Z'},
            'review': {'event_id':eid,'reviewer_id':'reviewer-1',
                       'decision':'APPROVED','reviewed_at':day+'T12:00:00Z'}}

def test_verified_independent_events_only():
    result=reviewed_historical_candidates([bundle('e1','b1','2026-09-01'),
                                           bundle('e2','b2','2026-09-02')],
                                           '2026-09-03T00:00:00Z')
    assert len(result)==1 and result[0]['independent_bar_count']==2
    assert result[0]['state']=='CANDIDATE'

def test_reject_unverified_assertion():
    forged=bundle('e1','b1','2026-09-01')
    forged['event']['structural_qualification']='INDEPENDENT_REVIEW_VERIFIED'
    forged['review']['decision']='REJECTED'
    with pytest.raises(ValueError):
        reviewed_historical_candidates([forged], '2026-09-03T00:00:00Z')

def test_no_future_review():
    with pytest.raises(ValueError):
        reviewed_historical_candidates([bundle('e1','b1','2026-09-02')],
                                       '2026-09-02T10:00:00Z')

def test_reject_incomplete_bundle():
    with pytest.raises(ValueError):
        reviewed_historical_candidates([{'event':bundle('e1','b1','2026-09-01')['event']}],
                                       '2026-09-03T00:00:00Z')
