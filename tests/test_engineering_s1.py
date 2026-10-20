from copy import deepcopy
from decimal import Decimal as D
import random
import pytest
from ktrader.engineering_s1 import pool, trend_prefixes, validate_profile
from ktrader.approved_models import Bar, Context, trend, make_order
from ktrader.level_admission import fingerprint
from ktrader.price_profile import profile_blockers
from ktrader.approved_replay import run_model


def profile():
    return dict(mode='OWNER_AUTHORIZED_ENGINEERING',broker_symbol='ACHC.us',
        owner_approval_id='OWNER_20261020_POINT002_TICK002',point='.02',tick_size='.02',
        historical_price_geometry_verified=False,level_universe_reviewed=False)


def test_authorized_point_is_not_a_verified_terminal_profile():
    p=profile();validate_profile(p)
    assert 'historical_price_geometry_verified' in profile_blockers(p,'ACHC.us')
    p['point']='.01'
    with pytest.raises(ValueError): validate_profile(p)


def test_incremental_directions_equal_every_original_prefix_including_plateaus():
    rng=random.Random(731)
    bars=[]
    for _ in range(150):
        base=D(rng.randrange(90,110));bars.append(Bar(base,base+2,base-2,base))
    assert trend_prefixes(bars)==[trend(bars[:n]) for n in range(len(bars)+1)]
    flat=[Bar(D(100),D(101),D(99),D(100))]*20
    assert trend_prefixes(flat)==['UNKNOWN']*21


def test_raw_off_assumed_grid_level_preserved_and_touch_is_causal():
    rows=[[i*10,'99','100.01','98','99','0',i*10+9] for i in range(4)]
    c=dict(price='100.01',side='RESISTANCE',primary_type='LIMIT',timeframe='D1',
        source_index=0,confirmation_index=2,source_open_ms=0,known_at_ms=30,witness_indices=[0,1,2])
    p=dict(candidate=c,evidence_id=fingerprint(c),source_sha256='hash',witness_rows=rows[:3])
    accepted,blocked=pool([p],{'D1':rows,'W1':[]},[],'hash',39)
    assert not accepted and blocked[0]['reason']=='NO_SUBSEQUENT_EXACT_TOUCH'
    accepted,_=pool([p],{'D1':rows,'W1':[]},[],'hash',40)
    assert accepted[0]['candidate']['price']=='100.01'
    assert accepted[0]['available_at']==40
    assert accepted[0]['independent_human_review'] is False
    assert p['witness_rows']==rows[:3]


def test_point002_can_make_existing_equity_stop_cap_impossible():
    ctx=Context(D('28'),1,D('.0112'),D('.02'),D('.02'),D(1),'us_equity',
        True,True,('DOWN',)*3,'DOWN',True,technical_stop=D('27.94'))
    with pytest.raises(ValueError,match='equity technical stop cap'):
        make_order(ctx,'S1',Bar(D(28),D('28.1'),D(28),D(28)))


@pytest.mark.parametrize('scenario',['A','B'])
def test_point002_full_lifecycle_and_optional_diagnostics_preserve_result(scenario):
    def b(o=100,h=101,l=99,c=100):
        return Bar(*map(lambda x:D(str(x)),(o,h,l,c)))
    ctx=Context(D(100),1,D('.04'),D('.02'),D('.02'),D(10),'us_equity',
                True,True,('DOWN',)*3,'UP',True)
    seed=[b()]*20+[b(100.1,100.2,100,100.1)]
    bars=[b(100.1,100.15,100.02,100.04),b(100.1,100.6,100.05,100.5)]
    diagnostic={}
    first=run_model(bars,'S1',lambda i,h:ctx,scenario,seed_history=seed,diagnostics=diagnostic)
    assert first==run_model(bars,'S1',lambda i,h:ctx,scenario,seed_history=seed)
    assert len(first)==1 and first[0]['status']=='TP' and first[0]['gross_r']=='3'
    assert first[0]['order']['stop']=='99.94'
    assert diagnostic['ORDERS_CREATED']==1
