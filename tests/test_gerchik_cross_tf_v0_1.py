import pytest
from dataclasses import dataclass
from decimal import Decimal
from scripts.research.gerchik_cross_tf_v0_1 import associate

@dataclass
class L:
    symbol: str = 'SUIUSDT'
    timeframe: str = '1d'
    price: Decimal = Decimal('2.125')
    tick_size: str = '0.001'
    primary_type: str = 'HISTORICAL'
    formed_at: str = '2026-09-01T00:00:00Z'
    formation_event_id: str = 'a'
    state: str = 'CANDIDATE'

def test_same_exact_price_associates_without_merging_types():
    result = associate([L(), L(timeframe='1w', tick_size='0.0005', primary_type='MIRROR', formation_event_id='b')], '2026-09-03T00:00:00Z')
    assert len(result) == 1 and result[0]['cross_tf']
    assert [x['primary_type'] for x in result[0]['candidates']] == ['HISTORICAL', 'MIRROR']
    assert result[0]['state'] == 'CANDIDATE_ONLY'

def test_nearby_prices_not_merged():
    result = associate([L(), L(timeframe='1w', price=Decimal('2.126'))], '2026-09-03T00:00:00Z')
    assert len(result) == 2 and not any(x['cross_tf'] for x in result)

def test_future_confirmation_not_backdated():
    result = associate([L(), L(timeframe='1w', formed_at='2026-09-04T00:00:00Z')], '2026-09-03T00:00:00Z')
    assert len(result) == 1 and not result[0]['cross_tf']

def test_other_symbol_not_merged():
    assert len(associate([L(), L(symbol='XRPUSDT', timeframe='1w')], '2026-09-03T00:00:00Z')) == 2

@pytest.mark.parametrize('bad', ['2026-09-03T00:00:00', '2026-09-03T03:00:00+03:00'])
def test_invalid_asof(bad):
    with pytest.raises(ValueError): associate([L()], bad)

def test_reject_confirmed_input():
    with pytest.raises(ValueError): associate([L(state='CONFIRMED')], '2026-09-03T00:00:00Z')

def test_reject_invalid_tick():
    with pytest.raises(ValueError): associate([L(price=Decimal('2.1255'))], '2026-09-03T00:00:00Z')
