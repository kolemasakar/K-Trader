# Approved correction: overlapping D1/W1 candles are valid reinforcing level evidence

User clarification 2026-09-28: Whether D1/W1 observations reflect the same or distinct underlying market event is irrelevant to **cross-timeframe level confirmation**. Repeated market activity near strong levels reinforces the level; overlapping candle intervals MUST NOT block D1/W1 confirmation within symmetric approved luft.

Changes on research branch:
- `gerchik_cross_tf_luft_v0_2.py`: remove interval-overlap exclusion; preserve independently formed D1/W1 source records, causal source-bar checks, tick precision, symmetric inclusive luft, reciprocal ambiguity safeguards and provenance. Distinct event record IDs remain a record-deduplication safeguard, not a requirement for different physical market events.
- `gerchik_historical_candidates_v0_1.py`: remove overlap exclusion; retain independently reviewed source records, distinct bar IDs for historical repeated-extremum counting, and source-bar chronology. The HISTORICAL aggregator still matches exact price; cross-TF confirmation separately uses symmetric luft. Different D1/W1 observations may reinforce a level even when their candles overlap.
- Update regressions to expect overlap to count, not reject.

Important nuance: deduplication of identical input records is retained, but **physical event identity is not a reason to reject cross-TF evidence**. No automatic live-trading promotion. The earlier overlap-exclusion docs are superseded on this specific point.

Verification: code and regression tests committed; updated tests have **not yet been executed** against the corrected commits. Do not cite earlier pass counts as verification.
