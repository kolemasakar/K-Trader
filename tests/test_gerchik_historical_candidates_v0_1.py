import pytest
from scripts.research.gerchik_historical_candidates_v0_1 import historical_candidates

def e(event_id, bar_id, **changes):
    item = dict(symbol='SUIUSDT', timeframe='1d', source_field='high',
                price='2.125', tick_size='0.001', observed_at='2026-09-01T00:00:00Z',
                event_id=event_id, source_bar_id=bar_id,
                structural_qualification='EXTERNALLY_VALIDATED')
    item.update(changes)
    return item

def test_two_independent_qualified_events_create_candidate_only():
    out = historical_candidates([e('a', 'bar1'), e('b', 'bar2', timeframe='1w')], '2026-09-02T00:00:00Z')
    assert len(out) == 1 and out[0]['type'] == 'HISTORICAL'
    assert out[0]['state'] == 'CANDIDATE' and out[0]['independent_bar_count'] == 2

def test_single_or_shared_bar_not_sufficient():
    assert not historical_candidates([e('a', 'bar1')], '2026-09-02T00:00:00Z')
    assert not historical_candidates([e('a', 'bar1'), e('b', 'bar1')], '2026-09-02T00:00:00Z')

def test_future_event_does_not_backdate_candidate():
    assert not historical_candidates([e('a', 'bar1'), e('b', 'bar2', observed_at='2026-09-03T00:00:00Z')], '2026-09-02T00:00:00Z')

@pytest.mark.parametrize('changes', [
    {'source_field': 'close'}, {'timeframe': '1h'},
    {'structural_qualification': ''}, {'price': '2.1255'},
])
def test_reject_unqualified_sources(changes):
    with pytest.raises(ValueError):
        historical_candidates([e('a', 'bar1', **changes)], '2026-09-02T00:00:00Z')

def test_duplicate_event_rejected():
    with pytest.raises(ValueError, match='Duplicate'):
        historical_candidates([e('a', 'bar1'), e('a', 'bar2')], '2026-09-02T00:00:00Z')
