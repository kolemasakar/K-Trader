"""Compatibility alias for the mandatory review-enforcing historical entrypoint."""
from .gerchik_historical_candidates_v0_1 import historical_candidates


def reviewed_historical_candidates(items, as_of, min_independent=2):
    return historical_candidates(items, as_of, min_independent)
