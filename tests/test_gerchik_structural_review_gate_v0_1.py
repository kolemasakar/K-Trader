import pytest
from scripts.research.gerchik_structural_review_gate_v0_1 import verify_reviewed_extremum

def fixture():
    event=dict(event_id='e1',symbol='SUIUSDT',timeframe='1d',source_field='high',
               source_bar_id='bar1',price='2.125',tick_size='0.001',
               observed_at='2026-09-02T00:00:00Z')
    bar=dict(bar_id='bar1',symbol='SUIUSDT',timeframe='1d',
             high='2.125',low='2.000',closed_at='2026-09-01T23:59:59Z')
    review=dict(event_id='e1',reviewer_id='human-review-1',decision='APPROVED',
                reviewed_at='2026-09-02T12:00:00Z')
    return event,bar,review

def test_reviewed_event_becomes_eligible_only_at_review():
    e,b,r=fixture()
    with pytest.raises(ValueError):
        verify_reviewed_extremum(e,b,r,'2026-09-02T11:59:59Z')
    out=verify_reviewed_extremum(e,b,r,'2026-09-02T12:00:00Z')
    assert out['structural_qualification']=='INDEPENDENT_REVIEW_VERIFIED'
    assert out['observed_at']=='2026-09-02T12:00:00+00:00'

@pytest.mark.parametrize('change', [
    ('event',{'source_field':'close'}),
    ('event',{'price':'2.126'}),
    ('event',{'tick_size':'0.002'}),
    ('event',{'source_bar_id':'wrong'}),
    ('review',{'decision':'REJECTED'}),
    ('review',{'reviewer_id':''}),
    ('review',{'event_id':'other'}),
    ('review',{'reviewed_at':'2026-09-01T00:00:00Z'}),
    ('bar',{'closed_at':'2026-09-03T00:00:00Z'}),
])
def test_reject_invalid_provenance(change):
    e,b,r=fixture()
    {'event':e,'bar':b,'review':r}[change[0]].update(change[1])
    with pytest.raises(ValueError):
        verify_reviewed_extremum(e,b,r,'2026-09-03T12:00:00Z')
