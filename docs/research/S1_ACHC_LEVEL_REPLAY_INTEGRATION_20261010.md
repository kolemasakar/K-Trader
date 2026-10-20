# S1 ACHC.us D1/W1 integration checkpoint — 2026-10-10

Status: INTEGRATED IN RESEARCH PR #95, REAL RUN AND FULL S1 OUTCOME NOT YET VERIFIED.

Reuses modules imported from PR #94:
- `scripts/research/gerchik_seven_types_v0_1.py` and original source pattern algorithms;
- `scripts/research/gerchik_strict_candidates_v0_1.py` for causal strict archetypes;
- `scripts/research/gerchik_level_strength_v0_1.py` for research rating;
- `scripts/research/gerchik_filtered_atr5_v1.py` with approved iterative ATR5 v2.

New US-equity bridge:
- `s1_equity_level_rows.py`: closed MT4 D1 -> ordered legacy source rows, finalized W1 only once next ISO week observed;
- `s1_existing_levels_bridge.py`: explicit 24/7 or equity-session dispatch;
- `s1_equity_levels_replay.py`: calls original `detect_all` for both D1 and W1; outputs provisional RESEARCH_CANDIDATE counts, not owner-approved levels;
- `s1_research_runner.py`: now invokes D1/W1 candidate research on `*.us` source series, keeps outcome fields null and missing review/Point/SL gates closed.

Safety: no source write, no live trading, no inferred timezone, no invented independent reviews. Session-dependent GAP classification is deferred; original crypto 24/7 branch retained. Real ACHC.us integrated detector run and CI acceptance still require verification. Full strategy/financial backtest is NOT EXECUTED.
