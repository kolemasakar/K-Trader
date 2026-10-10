from dataclasses import dataclass
from decimal import Decimal
import pytest
from scripts.research.gerchik_cross_tf_luft_v0_2 import confirm_pairs

@dataclass
class L:
    symbol: str = 'SUIUSDT'
    timeframe: str = '1d'
    price: Decimal = Decimal('2.125')
    tick_size: str = '0.001'
    primary_type: str = 'HISTORICAL'
    formed_at: str = '2026-09-01T00:00:00Z'
    formation_event_id: str = 'd1'
    state: str = 'CANDIDATE'
    structurally_qualified: bool = True
    source_opened_at: str = '2026-08-31T00:00:00Z'
    source_closed_at: str = '2026-08-31T23:59:59Z'

def pair(delta='0', when='2026-09-02T00:00:00Z', qualified=True):
    return [L(), L(timeframe='1w', price=Decimal('2.125')+Decimal(delta),
                   formation_event_id='w1', formed_at=when,
                   source_opened_at='2026-09-01T00:00:00Z',
                   source_closed_at='2026-09-01T23:59:59Z',
                   structurally_qualified=qualified)]

@pytest.mark.parametrize('delta', ['0', '0.004', '-0.004'])
def test_symmetric_inclusive_luft_confirmation(delta):
    result=confirm_pairs(pair(delta), '2026-09-03T00:00:00Z', {'SUIUSDT':'0.004'})
    assert len(result)==1 and result[0]['cross_tf_confirmed']
    assert result[0]['confirmed_at']=='2026-09-02T00:00:00+00:00'

@pytest.mark.parametrize('delta', ['0.005', '-0.005'])
def test_outside_luft_not_confirmed(delta):
    assert confirm_pairs(pair(delta), '2026-09-03T00:00:00Z', {'SUIUSDT':'0.004'})==[]

def test_future_not_backdated():
    assert confirm_pairs(pair(when='2026-09-04T00:00:00Z'), '2026-09-03T00:00:00Z', {'SUIUSDT':'0.004'})==[]

def test_unqualified_not_confirmed():
    assert confirm_pairs(pair(qualified=False), '2026-09-03T00:00:00Z', {'SUIUSDT':'0.004'})==[]

def test_ambiguous_pairs_not_arbitrarily_confirmed():
    levels=pair()+[L(timeframe='1w', price=Decimal('2.126'), formation_event_id='w2',
                     source_opened_at='2026-09-01T00:00:00Z',
                     source_closed_at='2026-09-01T23:59:59Z',
                     formed_at='2026-09-02T00:00:00Z')]
    assert confirm_pairs(levels, '2026-09-03T00:00:00Z', {'SUIUSDT':'0.004'})==[]

@pytest.mark.parametrize('luft', ['-0.01', 'NaN'])
def test_bad_luft_rejected(luft):
    with pytest.raises(ValueError):
        confirm_pairs(pair(), '2026-09-03T00:00:00Z', {'SUIUSDT':luft})

def test_missing_luft_rejected():
    with pytest.raises(ValueError, match='Missing'):
        confirm_pairs(pair(), '2026-09-03T00:00:00Z', {})

def test_source_prices_and_types_preserved():
    result=confirm_pairs(pair('0.003'), '2026-09-03T00:00:00Z', {'SUIUSDT':'0.004'})[0]
    assert result['d1_price']=='2.125' and result['w1_price']=='2.128'
    assert result['primary_types']==['HISTORICAL', 'HISTORICAL']


def test_overlapping_source_bars_can_confirm():
    levels=pair()
    levels[1].source_opened_at='2026-08-31T00:00:00Z'
    assert len(confirm_pairs(levels, '2026-09-03T00:00:00Z', {'SUIUSDT':'0.004'}))==1


def test_missing_source_interval_rejected():
    levels=pair()
    levels[1].source_opened_at=''
    with pytest.raises(ValueError, match='source bar interval'):
        confirm_pairs(levels, '2026-09-03T00:00:00Z', {'SUIUSDT':'0.004'})


def test_noncausal_source_bar_rejected():
    levels=pair()
    levels[1].source_closed_at='2026-09-04T00:00:00Z'
    with pytest.raises(ValueError, match='noncausal'):
        confirm_pairs(levels, '2026-09-05T00:00:00Z', {'SUIUSDT':'0.004'})
