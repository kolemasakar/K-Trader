from copy import deepcopy
import pytest
from ktrader.level_semantic_audit import audit_panel


def rows(prices):
    return [[i*10, *map(str, p), '0', i*10+9] for i, p in enumerate(prices)]


def panel(kind, end, side='RESISTANCE'):
    return {'evidence_id': 'test', 'candidate': {
        'price': '100', 'side': side, 'primary_type': kind,
        'source_index': 0, 'confirmation_index': end,
        'known_at_ms': (end+1)*10, 'timeframe': 'D1',
        'witness_indices': list(range(end+1))}}


def test_limit_does_not_self_approve_and_future_touch_excluded():
    rr=rows([(99,100,98,99)]*4)
    r=audit_panel(panel('LIMIT',2),rr,as_of_ms=30)
    assert r['status']=='SHAPE_PASS_REVIEW_PENDING'
    assert not r['admitted'] and not r['independent_review_created']
    assert r['subsequent_exact_touch_indices']==[]
    assert audit_panel(panel('LIMIT',2),rr,as_of_ms=40)['subsequent_exact_touch_indices']==[3]


def test_consolidation_requires_full_strictly_one_sided_interval():
    rr=rows([(99,100,98,99)]+[(98,99,97,98)]*3+[(99,100,98,99)])
    p=panel('CONSOLIDATION',4)
    assert audit_panel(p,rr,as_of_ms=50)['status']=='SHAPE_PASS_REVIEW_PENDING'
    rr[2][2]='100.01'
    assert audit_panel(p,rr,as_of_ms=50)['status']=='SHAPE_FAIL'


def test_mirror_cannot_bridge_failed_role_change_hidden_from_witnesses():
    rr=rows([(99,100,98,99),(99,100,98,99),(101,102,101,102),
             (101,102,100.5,101),(101,102,100,101)])
    p=panel('MIRROR',4,'SUPPORT');p['candidate']['witness_indices']=[0,1,2,4]
    assert audit_panel(p,rr,as_of_ms=50)['status']=='SHAPE_PASS_REVIEW_PENDING'
    rr[3]=[30,'99','99.5','98','99','0',39]
    r=audit_panel(p,rr,as_of_ms=50)
    assert r['status']=='SHAPE_FAIL' and not r['checks']['no_failed_role_change_bridged']


@pytest.mark.parametrize('kind,status',[('TREND_BREAK','QUALITATIVE_REVIEW_REQUIRED'),
                                       ('PARANORMAL_BAR','POLICY_UNAPPROVED')])
def test_shape_does_not_resolve_qualitative_or_unapproved_rules(kind,status):
    r=audit_panel(panel(kind,2),rows([(99,100,98,99)]*3),as_of_ms=30)
    assert r['status']==status and not r['admitted']


def test_future_formation_rejected():
    with pytest.raises(ValueError,match='unavailable'):
        audit_panel(panel('LIMIT',2),rows([(99,100,98,99)]*3),as_of_ms=29)
