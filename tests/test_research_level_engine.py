from ktrader.research_level_engine import research_admit

def test_all_models_share_one_causal_level_decision():
    rows = [(100, 'x', '100', '90', '95', '95', 200)]
    candidate = dict(timeframe='D1', primary_type='MIRROR', known_at_ms=201,
                     source_index=0, source_open_ms=100, price='100',
                     witness_indices=[0, 0])
    models = ('S1', 'S2A', 'S2B', 'S3', 'S4', 'S5A', 'S5B')
    decisions = [research_admit(candidate, rows, as_of_ms=201,
                 source_hash='fixed', verified_strength=True) for _ in models]
    assert all(x.admitted for x in decisions)
    assert len({x.evidence_id for x in decisions}) == 1
    assert not research_admit(candidate, rows, as_of_ms=200,
               source_hash='fixed', verified_strength=True).admitted
    assert not research_admit(candidate, rows, as_of_ms=201,
               source_hash='fixed', verified_strength=False).admitted

def test_unsupported_strength_and_noncausal_witness_fail_closed():
    rows = [(100, 'x', '100', '90', '95', '95', 200)]
    c = dict(timeframe='W1', primary_type='TREND_BREAK', known_at_ms=201,
             source_index=0, source_open_ms=100, price='100',
             witness_indices=[0, 0])
    assert not research_admit(c, rows, as_of_ms=201, source_hash='x',
                              verified_strength=True).admitted
    c['primary_type'] = 'MIRROR'
    c['known_at_ms'] = 199
    assert not research_admit(c, rows, as_of_ms=201, source_hash='x',
                              verified_strength=True).admitted
