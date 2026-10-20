from dataclasses import replace
from decimal import Decimal as D
import pytest
from ktrader.approved_models import Bar,Context,ModelState,make_order,rebound,gates,consolidation,large_bar,trend
from ktrader.approved_execution import prefix,replay_order
from ktrader.research_risk import RiskProfile,size_position
from ktrader.level_admission import admit,fingerprint


def b(o=100,h=101,l=99,c=100):
    return Bar(*map(lambda x:D(str(x)),(o,h,l,c)))


def ctx(side=1):
    return Context(D(100),side,D('.04'),D('.01'),D('.01'),D(10),'us_equity',True,True,
                   ('DOWN',)*3 if side==1 else ('UP',)*3,'UP' if side==1 else 'DOWN',True,
                   technical_stop=D('99.90') if side==1 else D('100.10'))


def test_unknown_activity_not_pass():
    assert large_bar(b(),[b()]*19) is None
    assert 'ACTIVITY_UNKNOWN' in gates(ctx(),'S1',D(100),b(),[b()]*19)


def test_threshold_equality_rejected():
    assert large_bar(b(h=102,l=98),[b()]*20) is True


@pytest.mark.parametrize('side',[1,-1])
def test_rebound_first_exact_partial_second(side):
    c=ctx(side)
    first=b(100.1,100.2,100,100.1) if side==1 else b(99.9,100,99.8,99.9)
    partial=b(100.1,100.2,100.02,100.1) if side==1 else b(99.9,99.98,99.8,99.9)
    assert rebound(c,first,partial,[b()]*20)==[]
    penetrated=b(100.1,100.2,99.99,100.1) if side==1 else b(99.9,100.01,99.8,99.9)
    assert 'BPU2_TOUCH_OR_PENETRATION' in rebound(c,first,penetrated,[b()]*20)


def test_no_score_or_unreviewed_admission():
    c=replace(ctx(),admitted=False)
    assert 'LEVEL_NOT_ADMITTED_OR_STRENGTH_UNCONFIRMED' in gates(c,'S1',D(100),b(),[b()]*20)


@pytest.mark.parametrize('side',[1,-1])
def test_s3_stop_only_two_luft(side):
    order=make_order(ctx(side),'S3',b(h=110,l=90))
    assert order.stop==D(100)-side*D('.08')
    assert order.distance==D('.12')


@pytest.mark.parametrize('model',['S2A','S4','S5A','S5B'])
@pytest.mark.parametrize('side',[1,-1])
def test_stop_uses_known_tail(model,side):
    order=make_order(ctx(side),model,b(h=102,l=98))
    assert order.stop==(D('97.98') if side==1 else D('102.02'))


def test_s2b_frozen_range_anchor():
    c=ctx()
    order=make_order(c,'S2B',b(),bounds=(D(99),D('100.03')))
    assert order.entry==D('100.07')


def test_channel_uses_80_percent_no_atr_reserve():
    c=replace(ctx(),atr=D('.01'),channel=(D(100),D(110)))
    assert gates(c,'CHANNEL',D(105),b(),[b()]*20)==[]
    assert make_order(c,'CHANNEL',b()).target<=D(110)


def test_channel_boundary_blocks_target():
    c=replace(ctx(),channel=(D(100),D('100.2')))
    with pytest.raises(ValueError,match='channel'):
        make_order(c,'CHANNEL',b())


def test_prefix_does_not_see_future_low():
    bar=b(100,104,98,101)
    assert prefix(bar,'A',D('.2')).low==100
    assert prefix(bar,'B',D('.2')).high==100


def test_scenarios_independent_and_no_net_fabrication():
    order=make_order(ctx(),'S3',b())
    bars=[b(100.04,101,99,100)]
    assert replay_order(order,bars,'A',activation=D(0))['status']=='TP'
    assert replay_order(order,bars,'B',activation=D(0))['status']=='SL'
    assert replay_order(order,bars,'A',activation=D(0))['net_r'] is None


def test_early_touch_never_fills_after_activation():
    order=make_order(ctx(),'S3',b())
    assert replay_order(order,[b(100.2,101,100,100.5)],'B',activation=D('.9'))['status']=='UNFILLED'


def test_pending_cancel_at_close_and_censor():
    order=make_order(ctx(),'S3',b())
    assert replay_order(order,[b(101,102,101,102)],'A',cancel_at_close=lambda bar,o:abs(bar.close-o.level)>=2*o.distance)['status']=='CANCELLED_CLOSE'
    assert replay_order(order,[b(100.04,100.05,100.03,100.04)],'A',activation=D(0))['status']=='CENSORED'


def test_gap_stop_adverse_actual_open():
    order=make_order(ctx(),'S3',b())
    result=replay_order(order,[b(100.04,100.05,100.03,100.04),b(99,99.5,98,99)],'A',activation=D(0))
    assert result['status']=='SL_GAP' and D(result['gross_r'])<-1


def test_s5b_three_total_not_three_additional():
    state=ModelState('S5B',ctx())
    history=[b()]*20+[b(100.1,100.2,99.9,99.95)]
    state.on_closed(history)
    assert state.phase=='OUTSIDE'
    history.append(b(99.95,100,99.9,99.95));state.on_closed(history)
    assert state.phase=='OUTSIDE'
    history.append(b(99.95,100,99.9,99.95));state.on_closed(history)
    assert state.phase=='ARMED' and len(state.structure)==3


def test_s5b_rejects_return_before_three():
    state=ModelState('S5B',ctx(),phase='OUTSIDE',structure=[b(100.1,100.2,99.9,99.95)])
    state.on_closed([b()]*20+[b(99.95,100.01,99.9,100)])
    assert state.phase=='CANCELLED'


def test_s3_no_six_bar_limit():
    state=ModelState('S3',ctx(),phase='RETEST_WAIT')
    for _ in range(20):
        state.on_closed([b()]*20+[b(100.5,101,100.1,100.5)])
    assert state.phase=='RETEST_WAIT'


def test_after_fill_not_cancelled():
    state=ModelState('S1',ctx(),phase='FILLED',order=make_order(ctx(),'S1',b()))
    state.on_closed([b(c=101)])
    assert state.phase=='FILLED'


def test_missing_cost_not_zero():
    assert size_position(1,1000,None)['volume'] is None
    p=RiskProfile(1,1,1,100,None,'test')
    assert size_position(1,1000,p)['status']=='UNKNOWN_METADATA_OR_COSTS'
    assert size_position(1,1000,replace(p,estimated_round_trip_cost_per_unit=D('.2')))['volume']=='4'


def test_admission_review_and_tick_cannot_be_fabricated():
    candidate=dict(price='100',timeframe='D1',side='SUPPORT',primary_type='LIMIT',
                   source_index=0,source_open_ms=0,known_at_ms=30,witness_indices=[0,1,2])
    rows=[[i*10,'101','102','100','101','0',i*10+9] for i in range(4)]
    review=dict(evidence_id=fingerprint(candidate),source_sha256='test',decision='CONFIRMED',
                reviewer='independent-fixture',method='INDEPENDENT_LABEL',known_at_ms=30,
                strengthening=[dict(kind='TOUCH',confirmed=True,known_at_ms=40,witness_indices=[3],
                                    rule_id='exact-touch',reviewer='independent-fixture')])
    assert not admit(candidate,None,rows,as_of_ms=40,tick=None,source_hash='test').admitted
    assert admit(candidate,review,rows,as_of_ms=40,tick='.01',source_hash='test').admitted
    assert not admit(candidate,review,rows,as_of_ms=39,tick='.01',source_hash='test').admitted
    assert not admit(candidate,review,rows,as_of_ms=40,tick='.01',source_hash='other').admitted

from ktrader.approved_replay import run_model

@pytest.mark.parametrize('scenario',['A','B'])
def test_full_s1_event_loop(scenario):
    seed=[b()]*20+[b(100.1,100.2,100,100.1)]
    bars=[b(100.1,100.15,100.01,100.04),b(100.1,100.6,100.05,100.5)]
    report=run_model(bars,'S1',lambda i,h:ctx(),scenario,seed_history=seed)
    assert len(report)==1 and report[0]['status']=='TP'
    assert report[0]['activation_fraction']=='.9' or D(report[0]['activation_fraction'])==D('.9')
    assert report[0]['gross_r']=='3' and report[0]['size']['volume'] is None

@pytest.mark.parametrize('scenario',['A','B'])
def test_full_s2_programmatic_loop(scenario):
    c=replace(ctx(),approach=('UP',)*3)
    seed=[b()]*20+[b(99.5,99.65,99.4,99.6),b(99.6,99.75,99.5,99.7),b(99.7,99.85,99.6,99.8)]
    report=run_model([b(99.8,100.2,99.7,100.1),b(100.1,102,100.05,101)],'S2A',lambda i,h:c,scenario,seed_history=seed)
    assert report and report[0]['order']['kind']=='PROGRAMMATIC_STOP'
    assert report[0]['order']['entry']=='100.04'
    assert report[0]['status'] in ('TP','SL')

@pytest.mark.parametrize('scenario',['A','B'])
def test_full_s4_same_bar_return(scenario):
    report=run_model([b(100.1,100.2,99.9,100.15),b(100.15,101,100.05,100.8)],'S4',lambda i,h:ctx(),scenario,seed_history=[b()]*20)
    assert report and report[0]['created_bar']==0
    assert report[0]['order']['stop']=='99.88'

@pytest.mark.parametrize('scenario',['A','B'])
def test_full_s5a_second_bar_return(scenario):
    bars=[b(100.1,100.2,99.9,99.95),b(99.95,100.2,99.9,100.15),b(100.15,101,100.05,100.8)]
    report=run_model(bars,'S5A',lambda i,h:ctx(),scenario,seed_history=[b()]*20)
    assert report and report[0]['created_bar']==1

@pytest.mark.parametrize('scenario',['A','B'])
def test_full_s5b_fourth_bar_return(scenario):
    bars=[b(100.1,100.2,99.9,99.95),b(99.95,100,99.9,99.95),b(99.95,100,99.9,99.95),b(99.95,100.2,99.9,100.15),b(100.15,101,100.05,100.8)]
    report=run_model(bars,'S5B',lambda i,h:ctx(),scenario,seed_history=[b()]*20)
    assert report and report[0]['created_bar']==3

@pytest.mark.parametrize('side',[1,-1])
def test_target_space_measured_not_boolean_only(side):
    c=replace(ctx(side),opposing_level=D('100.1') if side==1 else D('99.9'))
    with pytest.raises(ValueError,match='opposing'):
        make_order(c,'S3',b())


def test_s2b_loop_selects_range_entry():
    c=replace(ctx(),approach=('UP',)*3,atr=D('3.3'))
    seed=[b(99.5,100.03,99,99.5)]*20
    seed += [b(99.5,99.65,99.4,99.6),b(99.6,99.75,99.5,99.7),b(99.7,99.85,99.6,99.8)]
    report=run_model([b(99.8,100.2,99.7,100.1),b(100.1,102,100.05,101)],'S2B',lambda i,h:c,'A',seed_history=seed)
    assert report and report[0]['order']['entry']=='100.07'


def test_s3_loop_waits_for_closed_break_then_retest():
    c=replace(ctx(),approach=('UP',)*3)
    seed=[b()]*20+[b(99.5,99.65,99.4,99.6),b(99.6,99.75,99.5,99.7),b(99.7,99.85,99.6,99.8)]
    bars=[b(99.8,100.3,99.8,100.2),b(100.2,100.3,100,100.1),b(100.1,100.15,100.01,100.04),b(100.1,100.6,100.05,100.5)]
    report=run_model(bars,'S3',lambda i,h:c,'A',seed_history=seed)
    assert report and report[0]['created_bar']==2
    assert report[0]['order']['stop']=='99.92'

def test_s1_scheduler_deterministic_and_suffix_does_not_change_signal():
    seed=[b()]*20+[b(100.1,100.2,100,100.1)]
    bars=[b(100.1,100.15,100.01,100.04),b(100.1,100.6,100.05,100.5)]
    first=run_model(bars,'S1',lambda i,h:ctx(),'A',seed_history=seed)
    second=run_model(bars,'S1',lambda i,h:ctx(),'A',seed_history=seed)
    assert first==second
    extended=run_model(bars+[b(100.5,1000,1,100)],'S1',lambda i,h:ctx(),'A',seed_history=seed)
    assert extended[0]==first[0]

@pytest.mark.parametrize('scenario',['A','B'])
def test_s5b_next_strong_level_cancels_before_return(scenario):
    c=replace(ctx(),breakout_next_level=D('99.9'))
    bars=[b(100.1,100.2,99.9,99.95),b(99.95,100,99.9,99.95),
          b(99.95,100,99.9,99.95),b(99.95,100.2,99.9,100.15)]
    assert run_model(bars,'S5B',lambda i,h:c,scenario,seed_history=[b()]*20)==[]
