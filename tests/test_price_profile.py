from copy import deepcopy
import pytest
from ktrader.price_profile import profile_blockers


def profile():
    return dict(point='.01',tick_size='.01',digits=2,broker_symbol='ACHC.us',
                asset_class='us_equity',provenance='synthetic test evidence',
                historical_price_geometry_verified=True,level_universe_reviewed=True)


def test_valid_declared_geometry():
    assert profile_blockers(profile(),'ACHC.us')==[]


@pytest.mark.parametrize('key',['historical_price_geometry_verified','level_universe_reviewed'])
@pytest.mark.parametrize('value',['false','true',1,None,False])
def test_truthy_values_do_not_establish_verification(key,value):
    p=profile();p[key]=value
    assert key in profile_blockers(p,'ACHC.us')


@pytest.mark.parametrize('value',['NaN','Infinity','-1','0',True,None])
def test_invalid_point_cannot_enter_replay(value):
    p=profile();p['point']=value
    assert 'point' in profile_blockers(p,'ACHC.us')


def test_incompatible_price_units_or_symbol_rejected():
    p=profile();p['tick_size']='.001'
    assert 'tick_not_multiple_of_point' in profile_blockers(p,'ACHC.us')
    p=profile();p['digits']=3
    assert 'point_digits_mismatch' in profile_blockers(p,'ACHC.us')
    assert 'broker_symbol' in profile_blockers(profile(),'OTHER')
