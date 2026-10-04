import unittest
from scripts.research.gerchik_strict_candidates_v0_1 import detect, inspect_later


def bars(highs):
    return [[i*10, '5', str(h), '1', '5', '1', i*10+9] for i,h in enumerate(highs)]


class HistoricalCandidatesTests(unittest.TestCase):
    def test_limit_available_only_third_close(self):
        r = bars([10,10,10])
        self.assertFalse([x for x in detect(r[:2],'D1') if x['side']=='RESISTANCE'])
        x = next(x for x in detect(r,'D1') if x['side']=='RESISTANCE')
        self.assertEqual((x['primary_type'],x['known_at_ms']),('LIMIT',30))

    def test_consolidation_needs_three_strict_bars(self):
        for highs, expected in (([10,9,8,10],False),([10,9,8,9,10],True),([10,9,11,9,10],False)):
            candidates = [x for x in detect(bars(highs),'D1') if x['side']=='RESISTANCE']
            self.assertEqual(bool(candidates),expected)

    def test_decimal_exact_no_tolerance(self):
        self.assertFalse([x for x in detect(bars(['10','10','10.0001']),'D1') if x['side']=='RESISTANCE'])

    def test_primary_identity_retained(self):
        x = next(x for x in detect(bars([10,10,10,9,8,9,10]),'D1') if x['side']=='RESISTANCE')
        self.assertEqual(x['primary_type'],'LIMIT')
        self.assertEqual(x['known_at_ms'],30)

    def test_gap_rejected(self):
        r=bars([10,10,10]); r[1][0]+=1
        with self.assertRaises(ValueError): detect(r,'D1')

    def test_later_wick_separate_from_close(self):
        r=bars([10,10,10,11]); x=next(x for x in detect(r,'D1') if x['side']=='RESISTANCE')
        self.assertEqual(inspect_later(r,x),dict(exact_later_touches=0,first_penetration_ms=40,first_close_beyond_ms=None))

    def test_all_prefixes(self):
        r=bars([10,9,8,9,10,11,11,11]); full=detect(r,'D1')
        for n in range(1,len(r)+1):
            self.assertEqual(detect(r[:n],'D1'),[x for x in full if x['known_at_ms']<=r[n-1][6]+1])
