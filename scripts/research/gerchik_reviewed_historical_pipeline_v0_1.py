"""Safe research entrypoint: independently verify all structural events before aggregation.

Do not call historical_candidates directly on untrusted event dictionaries.
"""
from .gerchik_structural_review_gate_v0_1 import verify_reviewed_extremum
from .gerchik_historical_candidates_v0_1 import historical_candidates


def reviewed_historical_candidates(items, as_of, min_independent=2):
    verified = []
    for item in items:
        if set(item) != {'event', 'source_bar', 'review'}:
            raise ValueError('Require complete event/bar/review evidence bundle')
        verified.append(verify_reviewed_extremum(
            item['event'], item['source_bar'], item['review'], as_of))
    return historical_candidates(verified, as_of, min_independent)
