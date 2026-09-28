import pytest
from scripts.research.gerchik_historical_candidates_v0_1 import historical_candidates


def bundle(eid, barid, day='2026-09-01', **changes):
    event=dict(event_id=eid, symbol='SUIUSDT', timeframe='1d', source_field='high',
               source_bar_id=barid, price='2.125', tick_size='0.001',
               observed_at=day+'T00:00:00Z')
    event.update(changes)
    return dict(event=event,
                source_bar=dict(bar_id=barid, symbol='SUIUSDT', timeframe='1d',
                                high='2.125', low='2.000', closed_at=day+'T00:00:00Z'),
                review=dict(event_id=eid, reviewer_id='independent-reviewer',
                            decision='APPROVED', reviewed_at=day+'T12:00:00Z'))


def test_two_independent_reviewed_events_are_candidates():
    result=historical_candidates([bundle('a','bar1'),bundle('b','bar2','2026-09-02')],
                                  '2026-09-03T00:00:00Z')
    assert len(result)==1 and result[0]['state']=='CANDIDATE'
    assert result[0]['independent_bar_count']==2


def test_one_event_insufficient():
    assert historical_candidates([bundle('a','bar1')], '2026-09-03T00:00:00Z')==[]


def test_future_review_rejected():
    with pytest.raises(ValueError):
        historical_candidates([bundle('a','bar1','2026-09-04')], '2026-09-03T00:00:00Z')


@pytest.mark.parametrize('changes', [
    {'source_field':'close'}, {'timeframe':'1h'}, {'price':'2.126'},
    {'tick_size':'0.002'}
])
def test_invalid_event_rejected(changes):
    with pytest.raises(ValueError):
        historical_candidates([bundle('a','bar1',**changes)], '2026-09-03T00:00:00Z')


def test_duplicate_event_rejected():
    with pytest.raises(ValueError, match='Duplicate'):
        historical_candidates([bundle('a','bar1'),bundle('a','bar2')], '2026-09-03T00:00:00Z')


@pytest.mark.parametrize('qualification', ['EXTERNALLY_VALIDATED','INDEPENDENT_REVIEW_VERIFIED'])
def test_direct_assertion_bypass_rejected(qualification):
    raw=bundle('a','bar1')['event']
    raw['structural_qualification']=qualification
    with pytest.raises(ValueError, match='bundle'):
        historical_candidates([raw], '2026-09-03T00:00:00Z')


def test_forged_approval_rejected():
    b=bundle('a','bar1')
    b['event']['structural_qualification']='INDEPENDENT_REVIEW_VERIFIED'
    b['review']['decision']='REJECTED'
    with pytest.raises(ValueError):
        historical_candidates([b], '2026-09-03T00:00:00Z')
