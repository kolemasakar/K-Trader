import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from scripts.research.gerchik_seven_types_v0_1 import ResearchPolicy, detect_all, provisional_rating

DAY = 86400000
POLICY = ResearchPolicy('synthetic-fixtures-only', 2, 2, 2, 2, 2, '2', 'UTC_CONTINUOUS_24_7')


def rows(values):
    return [[i*DAY, *map(str, v), '1', (i+1)*DAY-1] for i, v in enumerate(values)]


def claims(levels, kind):
    return [x for x in levels if x['primary_type'] == kind or
            kind in x['competing_primary_types'] or
            any(y['type'] == kind for y in x['additional_patterns'])]


class SevenTypesTests(unittest.TestCase):
    def test_limit_and_consolidation(self):
        r=rows([(10,15,8,12),(12,15,9,13),(13,15,10,12)])
        self.assertTrue(claims(detect_all(r,'D1',POLICY),'LIMIT'))
        r=rows([(10,15,8,12),(12,14,9,13),(13,14,10,12),(12,13,10,11),(12,15,9,13)])
        self.assertTrue(claims(detect_all(r,'D1',POLICY),'CONSOLIDATION'))

    def test_trend_requires_reversal_new_extreme_and_defenses(self):
        r=rows([(10,15,8,12),(12,18,10,16),(16,20,12,18),
                (17,19,11,12),(12,17,7,9),(10,20,8,12),(12,21,9,11)])
        self.assertFalse(claims(detect_all(r[:5],'D1',POLICY),'TREND_BREAK'))
        found=claims(detect_all(r,'D1',POLICY),'TREND_BREAK')
        self.assertTrue(found)
        self.assertEqual(found[0]['known_at_ms'],7*DAY)
        changed=[list(x) for x in r];changed[4][3]='9'
        self.assertFalse(claims(detect_all(changed[:5],'D1',POLICY),'TREND_BREAK'))

    def test_historical_uses_full_structural_witnesses(self):
        r=rows([(10,15,8,12),(12,18,10,16),(16,20,12,18),
                (17,19,11,12),(12,17,7,9),(18,22,6,9),
                (8,14,6,11),(11,17,8,14),(14,20,10,18),
                (17,19,9,12),(12,16,5,8)])
        self.assertTrue(claims(detect_all(r,'D1',POLICY),'HISTORICAL'))
        # Equal naked extrema cannot establish a historical primary.
        naked=rows([(10,15,8,12),(12,14,9,13),(13,15,10,12)])
        self.assertFalse(claims(detect_all(naked,'D1',POLICY),'HISTORICAL'))

    def test_mirror_is_defense_break_retest_and_has_new_side(self):
        r=rows([(10,15,8,12),(12,15,10,13),(16,20,14,19),(19,20,15,18)])
        self.assertFalse(claims(detect_all(r[:3],'D1',POLICY),'MIRROR'))
        x=claims(detect_all(r,'D1',POLICY),'MIRROR')[0]
        self.assertEqual((x['price'],x['side'],x['source_field']),('15','SUPPORT','high'))
        # A close breaking the old side before the retest aborts the role change.
        fail=rows([(10,15,8,12),(12,15,10,13),(16,20,14,19),(16,18,12,13),(19,20,15,18)])
        self.assertFalse(claims(detect_all(fail,'D1',POLICY),'MIRROR'))

    def test_paranormal_needs_separate_touch_falsebreak_per_end(self):
        r=rows([(11,12,10,11),(11,12,10,11),(11,20,5,12),
                (10,20,7,11),(11,21,8,10),(8,17,5,9),(9,18,4,8)])
        self.assertFalse(claims(detect_all(r[:4],'D1',POLICY),'PARANORMAL_BAR'))
        found=claims(detect_all(r,'D1',POLICY),'PARANORMAL_BAR')
        self.assertEqual({x['price'] for x in found},{'5','20'})
        # Formation bar is excluded from the reference average.
        self.assertEqual(next(x for x in found if x['price']=='20')['known_at_ms'],5*DAY)

    def test_gap_has_two_real_extremum_boundaries(self):
        r=rows([(10,12,9,11),(15,18,14,17),(17,19,14,18),(15,18,12,16)])
        found=claims(detect_all(r,'D1',POLICY),'GAP')
        self.assertEqual({x['price'] for x in found},{'12','14'})
        self.assertFalse(claims(detect_all(r[:2],'D1',POLICY),'GAP'))
        missing=[list(x) for x in r];missing[1][0]+=DAY
        with self.assertRaises(ValueError): detect_all(missing,'D1',POLICY)

    def test_reflect_price_reverses_support_resistance(self):
        values=[(10,15,8,12),(12,15,10,13),(16,20,14,19),(19,20,15,18)]
        reflected=[(30-o,30-l,30-h,30-c) for o,h,l,c in values]
        x=claims(detect_all(rows(reflected),'D1',POLICY),'MIRROR')[0]
        self.assertEqual((x['price'],x['side']),('15','RESISTANCE'))

    def test_every_prefix_primary_and_evidence_invariant(self):
        r=rows([(11,12,10,11),(11,12,10,11),(11,20,5,12),
                (10,20,7,11),(11,21,8,10),(8,17,5,9),(9,18,4,8)])
        full=detect_all(r,'D1',POLICY)
        for n in range(1,len(r)+1):
            expected=[]
            for x in full:
                if x['known_at_ms']<=n*DAY:
                    y=dict(x);y['additional_patterns']=[e for e in x['additional_patterns'] if e['known_at_ms']<=n*DAY]
                    expected.append(y)
            self.assertEqual(detect_all(r[:n],'D1',POLICY),expected)

    def test_simultaneous_types_do_not_use_strength_tiebreak(self):
        # Two defenses before break; later gap retest also creates a mirror.
        r=rows([(10,12,9,11),(11,12,10,11),(15,18,14,17),(15,18,12,16)])
        x=next(x for x in detect_all(r,'D1',POLICY) if x['price']=='12')
        self.assertEqual(x['primary_type'],'AMBIGUOUS')
        self.assertEqual(set(x['competing_primary_types']),{'GAP','MIRROR'})
        self.assertIsNone(provisional_rating(r,x,[],as_of_ms=4*DAY)['provisional_score'])

    def test_score_birth_and_future_exclusion(self):
        r=rows([(10,15,8,12),(12,15,9,13),(13,15,10,12),(12,16,10,11)])
        x=next(x for x in detect_all(r,'D1',POLICY) if x['price']=='15')
        birth=provisional_rating(r,x,[],as_of_ms=3*DAY)
        self.assertEqual(birth['provisional_score'],20)
        later=provisional_rating(r,x,[],as_of_ms=4*DAY)
        self.assertEqual(later['first_limit_penetration_ms'],4*DAY)
        self.assertIsNone(later['provisional_score'])
        self.assertIsNone(later['confirmed_score'])

    def test_score_freezes_after_close_beyond(self):
        r=rows([(10,15,8,12),(12,15,9,13),(13,15,10,12),
                (16,18,14,17),(12,15,9,13)])
        x=next(x for x in detect_all(r,'D1',POLICY) if x['price']=='15')
        x=dict(x,primary_type='HISTORICAL')  # generic close diagnostic, not limit penetration
        score=provisional_rating(r,x,[],as_of_ms=5*DAY)
        self.assertIsNone(score['provisional_score'])
        self.assertEqual(score['counts']['TOUCH'],0)
        self.assertEqual(score['first_close_beyond_ms'],4*DAY)

    def test_unapproved_calendar_and_nonclosed_bar_fail(self):
        from dataclasses import replace
        with self.assertRaises(ValueError): detect_all([], 'D1',replace(POLICY,calendar='FOREX'))
        r=rows([(10,15,8,12)]);r[0][6]-=1
        with self.assertRaises(ValueError): detect_all(r,'D1',POLICY)

    def test_same_tf_never_reinforces_and_future_cross_tf_excluded(self):
        r=rows([(10,15,8,12),(12,15,9,13),(13,15,10,12)])
        x=next(x for x in detect_all(r,'D1',POLICY) if x['price']=='15')
        future=dict(x,timeframe='W1',known_at_ms=4*DAY,first_close_beyond_ms=None)
        self.assertEqual(provisional_rating(r,x,[x,future],as_of_ms=3*DAY)['provisional_score'],20)
        present=dict(future,known_at_ms=3*DAY)
        self.assertEqual(provisional_rating(r,x,[present],as_of_ms=3*DAY)['provisional_score'],25)
        breached=dict(present,first_close_beyond_ms=3*DAY)
        self.assertEqual(provisional_rating(r,x,[breached],as_of_ms=3*DAY)['provisional_score'],20)

    def test_prior_audit_rejects_backdate_and_changed_witness(self):
        from scripts.research.gerchik_seven_type_replay_v0_1 import verify_previous
        r=rows([(10,15,8,12),(12,14,9,13),(13,14,10,12),(12,13,10,11),(12,15,9,13)])
        old=dict(price='15',side='RESISTANCE',source_open_ms=0,
                 confirmation_index=4,known_at_ms=5*DAY,formation_bars=r)
        self.assertEqual(verify_previous(r,old)['status'],'AUTOMATED_PATTERN_PASS')
        self.assertEqual(verify_previous(r,dict(old,known_at_ms=4*DAY))['status'],'REJECTED')
        self.assertEqual(verify_previous(r,dict(old,formation_bars=r[:-1]))['status'],'REJECTED')

    def test_preview_formula_matches_reviewed_model_on_synthetic_evidence(self):
        from scripts.research.gerchik_level_strength_v0_1 import Formation, SourceBar, Proof, Policy, rate
        r=rows([(10,15,8,12),(12,15,9,13),(13,15,10,12),(12,15,10,11)])
        x=next(x for x in detect_all(r,'D1',POLICY) if x['price']=='15')
        preview=provisional_rating(r,x,[],as_of_ms=4*DAY)
        source=SourceBar('source','FIXTURE','1d',0,DAY,10,15,8,12)
        touch=SourceBar('touch','FIXTURE','1d',3*DAY,4*DAY,12,15,10,11)
        level=Formation('L','FIXTURE',15,'1','LIMIT','source','high',DAY,3*DAY,
                        'synthetic-reviewer','synthetic-review',3*DAY,'APPROVED','synthetic','CONFIRMED')
        proof=Proof('P','TOUCH','touch','RESISTANCE',4*DAY,4*DAY,'synthetic-reviewer','APPROVED')
        score=rate(level,[source,touch],[proof],Policy('synthetic',0,0,None,0,''),as_of=4*DAY)
        self.assertEqual(preview['provisional_score'],score['score'])
