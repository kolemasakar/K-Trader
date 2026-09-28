import pytest
from scripts.research.gerchik_level_event_ledger_v0_1 import LevelLedger
from scripts.research.gerchik_ledger_cross_tf_evidence_v0_1 import ledger_cross_tf_evidence

ASOF='2026-09-05T00:00:00Z'

def setup():
    ledger=LevelLedger()
    d=ledger.record_formation(symbol='SUIUSDT',timeframe='1d',price='2.125',
        tick_size='0.001',primary_type='MIRROR',formed_at='2026-09-02T00:00:00Z',
        formation_event_id='d',source_field='high')
    w=ledger.record_formation(symbol='SUIUSDT',timeframe='1w',price='2.128',
        tick_size='0.001',primary_type='HISTORICAL',formed_at='2026-09-03T00:00:00Z',
        formation_event_id='w',source_field='high')
    sources={
        'd':dict(symbol='SUIUSDT',timeframe='1d',source_opened_at='2026-09-01T00:00:00Z',
                 source_closed_at='2026-09-01T23:59:59Z',verified_at='2026-09-02T12:00:00Z',
                 reviewed_formation_event_id='d'),
        'w':dict(symbol='SUIUSDT',timeframe='1w',source_opened_at='2026-08-31T00:00:00Z',
                 source_closed_at='2026-09-02T23:59:59Z',verified_at='2026-09-03T12:00:00Z',
                 reviewed_formation_event_id='w')
    }
    return ledger,d,w,sources

def test_overlapping_bars_reinforce_without_mutating_ledger():
    ledger,d,w,sources=setup()
    result=ledger_cross_tf_evidence(ledger,sources,ASOF,{'SUIUSDT':'0.004'})
    assert len(result)==1
    assert result[0]['primary_types']==['MIRROR','HISTORICAL']
    assert result[0]['confirmed_at']=='2026-09-03T12:00:00+00:00'
    assert d.primary_type=='MIRROR' and w.primary_type=='HISTORICAL'
    assert d.state==w.state=='CANDIDATE'
    assert d.evidence==w.evidence==[]

def test_future_review_not_visible():
    ledger,d,w,sources=setup()
    assert ledger_cross_tf_evidence(ledger,sources,'2026-09-03T06:00:00Z',
                                   {'SUIUSDT':'0.004'})==[]

def test_missing_review_cannot_confirm():
    ledger,d,w,sources=setup()
    del sources['w']
    assert ledger_cross_tf_evidence(ledger,sources,ASOF,{'SUIUSDT':'0.004'})==[]

def test_mismatched_review_identity_rejected():
    ledger,d,w,sources=setup()
    sources['w']['reviewed_formation_event_id']='different'
    with pytest.raises(ValueError,match='identity'):
        ledger_cross_tf_evidence(ledger,sources,ASOF,{'SUIUSDT':'0.004'})

def test_missing_review_fields_rejected():
    ledger,d,w,sources=setup()
    del sources['w']['source_closed_at']
    with pytest.raises(ValueError,match='Incomplete'):
        ledger_cross_tf_evidence(ledger,sources,ASOF,{'SUIUSDT':'0.004'})
