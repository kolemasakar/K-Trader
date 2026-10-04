# Gerchik S1–S6 backtest protocol v0.1
Date: 2026-10-04. Status: COMMON REQUIREMENTS RECORDED / RUN SPECIFICATION NOT YET FROZEN.

## Purpose and authority
Prepared under the owner's instruction to continue the approved research plan. This document makes the required execution inputs reviewable; it does not invent unresolved strategy definitions, select numeric parameters from outcomes or authorize production changes.

## Verified data
Existing retrospective crypto cohort: BTCUSDT, ETHUSDT, SOLUSDT, XRPUSDT, BNBUSDT, ADAUSDT, DOGEUSDT.
Window: [2025-09-25T00:00:00Z, 2026-09-25T00:00:00Z).
Intervals: 15m, 30m, 1h, 4h, 1d, 1w. 42 files; 447489 source bars; 42 SHA256 matches, zero internal gaps, zero invalid OHLC rows.
M15 is available for current entry models; M5 is absent, and cannot be derived from M15.
Per symbol: 35040 M15, 17520 M30, 8760 H1, 2190 H4, 365 D1, 52 raw W1.
Raw W1 includes one final partial week. Derive W1 from seven consecutive fully closed UTC Monday–Sunday D1 bars; 51 derived completed weeks per symbol. Generated deterministic weekly hashes and D1 lineage are in the inventory report. Derived arrays were computed in memory; no source file was changed.
The year exceeds the minimum six-month requirement, but warmup reduces eligible trade coverage. Equity, Forex, metals and energy archives were not accessed or validated here.

## Required freeze manifest BEFORE strategy outcome evaluation
- Exact code commit, strategy ID/version mapping, executable prerequisites and parameter values, level-event ledger provenance and causal known-at timestamps.
- Input manifest hash, accepted symbol/timeframe coverage, market/calendar/tick metadata and exclusion accounting.
- Exact UTC development/validation/control boundaries plus documented evidence that the reserved control has not been used. Old inspected late segments cannot be an independent holdout.
- Per-strategy entry confirmation, order type/fill convention, technical SL and horizon/expiry. S3 stop remains beyond level.
- Fee, spread, slippage, funding/borrow cost and their provenance/availability. Missing historic spread or funding must be explicitly flagged; 0.12% proxy is not actual measured historical cost.
- Portfolio/exposure assumptions, simultaneous-signal handling, re-entry rules and position sizing if a portfolio result is claimed.
- Collision policy and diagnostics for same-bar entry/exit or stop/target. Existing production outcome evaluator returns AMBIGUOUS. A research-only loss-first sensitivity may be separately declared; never count the assumed order as observed OHLC order.
- Execution gaps, time exits, censored positions and market-session treatment. Existing production evaluator is a touch/outcome resolver; it does not provide a complete next-open, gap-aware cost-inclusive simulator.
- Resource budget, read-only archive access, distinct research output and reproducibility checks.

## Evaluation stages
1. Compute causal setups with confirmed levels and canonical ATR5 v2 diagnostics. Missing ATR stays explicit; do not reinstate a blanket volatility-transition prohibition.
2. Run 1R study under a frozen configuration, preserving all eligible/excluded events and actual reasons.
3. Run 3R under the declared comparable setup/execution model. Record changes in holding and overlap; do not assume equal portfolio exposure. Never require an intermediate 2R stage.
4. Analyze net expectancy, profit factor, drawdown, count, long/short, asset/regime concentration, cost sensitivity, ambiguity/censoring and uncertainty. Label cost-proxy results accordingly.
5. Develop Level Strength v2 only after baseline analysis, then retest and independently validate pre-reserved control. Avoid tuning on control outcomes.

## Current run blockers
Primary owner interaction subsequently restored S1–S6 identities and original historical parameter excerpts; the erroneous draft mapping is corrected. Remaining blockers: exact confirmation predicates/current numeric migration and variant definitions; obsolete S6 level builder; unresolved contextual tolerance/entry precision/stop parameters; historical costs/funding and untouched-control provenance not verified. H1 <=12h is recovered historical research profile; M5/M15 is the newer intraday execution-model layer and must not be conflated.
This is a preparation gate, not strategy-performance evidence. Do not launch a supposedly approved six-strategy backtest using guessed definitions.
