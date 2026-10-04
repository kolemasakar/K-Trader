import sys
import unittest
from dataclasses import asdict
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from scripts.research.gerchik_methodology_audit_v0_1 import witness_check, contextual_zone
from scripts.research.gerchik_seven_types_v0_1 import ResearchPolicy, detect_all

DAY=86400000
POLICY=ResearchPolicy('synthetic',2,2,2,2,2,'2','UTC_CONTINUOUS_24_7')


def rows(values):
    return [[i*DAY,*map(str,v),'1',(i+1)*DAY-1] for i,v in enumerate(values)]


class MethodologyAuditTests(unittest.TestCase):
    def test_second_checker_and_adversarial_provenance(self):
        r=rows([(10,15,8,12),(12,18,10,16),(16,20,12,18),
                (17,19,11,12),(12,17,7,9),(10,20,8,12),(12,21,9,11)])
        x=next(x for x in detect_all(r,'D1',POLICY) if x['primary_type']=='TREND_BREAK')
        self.assertEqual(witness_check(r,x,asdict(POLICY))['status'],'SECOND_IMPLEMENTATION_PASS')
        for altered in (dict(x,known_at_ms=x['known_at_ms']-DAY),dict(x,price='20.1'),
                        dict(x,witness_indices=x['witness_indices']+[len(r)]),
                        dict(x,witness_bars=[]),dict(x,source_index=-1)):
            self.assertEqual(witness_check(r,altered,asdict(POLICY))['status'],'REJECTED')

    def test_secondary_positive_mirror_paranormal_gap_limit_consolidation(self):
        cases=[[(10,15,8,12),(12,15,10,13),(16,20,14,19),(19,20,15,18)],
               [(11,12,10,11),(11,12,10,11),(11,20,5,12),(10,20,7,11),(11,21,8,10)],
               [(10,12,9,11),(15,18,14,17),(17,19,14,18),(15,18,12,16)],
               [(10,15,8,12),(12,15,9,13),(13,15,10,12)],
               [(10,15,8,12),(12,14,9,13),(13,14,10,12),(12,13,10,11),(12,15,9,13)]]
        for values in cases:
            r=rows(values)
            for x in detect_all(r,'D1',POLICY):
                if x['primary_type']!='AMBIGUOUS':
                    self.assertEqual(witness_check(r,x,asdict(POLICY))['status'],'SECOND_IMPLEMENTATION_PASS',x)

    def zone(self,**kwargs):
        defaults=dict(price='100',asset_class='CRYPTO',anchor_price='100',anchor_known_at_ms=1,
                      as_of_ms=2,forex_point_size=None,tick_size=None,radius_rounding='RAW',provenance='synthetic')
        defaults.update(kwargs)
        return contextual_zone(**defaults)

    def test_symmetric_context_and_exact_percentage(self):
        z=self.zone()
        self.assertEqual((z['radius'],z['lower'],z['upper']),('0.0400','99.9600','100.0400'))
        self.assertEqual(z['significance'],'EQUAL_THROUGHOUT')
        self.assertFalse(z['tick_rounded'])
        self.assertEqual(self.zone(anchor_price='200')['radius'],'0.0800')

    def test_anchor_and_tick_policy_are_not_inferred(self):
        for params in (dict(anchor_price=None),dict(anchor_known_at_ms=3),
                       dict(radius_rounding='CEILING'),dict(radius_rounding='AUTOMATIC')):
            with self.assertRaises(ValueError): self.zone(**params)
        z=self.zone(tick_size='0.03',price='99.99',radius_rounding='CEILING')
        self.assertEqual(z['radius'],'0.06')
        with self.assertRaises(ValueError): self.zone(tick_size='0.03',radius_rounding='CEILING')

    def test_fixed_exceptions_and_forex_point_convention(self):
        self.assertEqual(self.zone(asset_class='GOLD',anchor_price=None)['radius'],'0.15')
        self.assertEqual(self.zone(asset_class='OIL',anchor_price=None)['radius'],'0.03')
        self.assertEqual(self.zone(asset_class='FOREX',forex_point_size='0.00001')['radius'],'0.00003')
        with self.assertRaises(ValueError): self.zone(asset_class='FOREX')
