# D1/W1 luft confirmation physical independence — implementation

Research branch `research/dual-market-historical-levels-v0-1`.

`gerchik_cross_tf_luft_v0_2.py` now requires qualified source levels to provide `source_opened_at` and `source_closed_at` in UTC. Reject invalid intervals and bars closing after the level's formation time. Cross-timeframe matching within inclusive symmetric luft requires **non-overlapping** source-bar intervals in addition to distinct formation event IDs. Reciprocal ambiguity checks apply the same condition. The original prices and primary types are preserved.

Updated the existing cross-TF test fixture with causal intervals and added regressions for overlapping intervals, missing provenance, and noncausal bars. The historical aggregator's corresponding conservative overlap gate was added separately.

**Verification pending:** new code and tests committed, but no full GitHub checkout or test run has yet verified these exact commits. Do not reuse earlier 12/12 or 14/14 results as evidence for this version. Container cannot resolve GitHub; production server and HP-OMEN remain untouched.

Limitation: disjoint bars are only a conservative proxy for distinct physical market moves, not a guarantee. A D1 and W1 bar often overlap by construction, so this policy deliberately withholds cross-TF confirmation for overlapping windows pending finer-grained independent structural event evidence. Do not promote or trade automatically.
