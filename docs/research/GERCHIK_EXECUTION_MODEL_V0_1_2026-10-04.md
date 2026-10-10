# Gerchik common research execution model v0.1 — 2026-10-04

Status: implemented and synthetic-tested; experiment assumptions, not a frozen S1–S6 market backtest.

Implementation: `scripts/research/gerchik_execution_v0_1.py`. Pure function, immutable setup/config/bar inputs; no production imports, orders, strategy classification or level construction.

## Contract

- Externally confirmed S1–S6 setup includes specification ID and level provenance; level known_at cannot exceed signal known_at.
- Integer UTC epoch milliseconds, exclusive bar end; first bar starts exactly at signal known_at, subsequent bars contiguous at explicitly supplied interval. Caller must supply fully observed historical bars and correctly timestamped signal availability. Delayed signals require a separate entry policy.
- Entry is next bar open. Technical stop is supplied; target is 1R or 3R from actual entry-open risk. These are experimental research targets, not a change to production structural targets. Invalid entry/target geometry is explicit.
- Stop gap fills at open, permitting losses below -1R. Target gap fills conservatively at target. Open is resolved before intrabar high/low.
- Both SL and TP touched in one bar: primary AMBIGUOUS with no realized R; explicitly configured STOP_FIRST is a separate sensitivity.
- Explicit bar-count horizon: unresolved trade exits at final horizon close. Incomplete history returns CENSORED; missing entry returns PENDING_ENTRY. Neither receives a realized return.
- Gross R uses initial raw-open risk. Net R subtracts entry+exit notional fee rate, two adverse spread/slippage fill costs in price units, and signed funding cost per unit, divided by that risk. Fill costs are modeled as P&L costs, not shifts of target geometry.
- All costs and their provenance are mandatory, including deliberately zero synthetic costs. Funding is a declared horizon estimate; this version does not reconstruct payment schedules or prorate early exits. Historical fee/funding adequacy must be resolved before interpreting market net returns.
- Result carries strategy/specification/level/cost provenance and collision policy. Caller remains responsible for cohort hash, full experiment config, symbol, setup deduplication, non-overlapping position policy, structural-target sensitivity and scheduling 1R before 3R.

## Validation and remaining work

13 focused execution tests plus 22 ATR5/cohort cases: 35 passed locally on Python 3.12. Coverage includes long/short targets, net-cost normalization, adverse and favorable gaps, collision sensitivity, censorship/time exits, causal timestamps, malformed OHLC, invalid geometry and invariance of completed results under future extension.

Previous branch CI dad96b42 completed successfully (run 37195397280). CI for this implementation must be checked after publication.

Next: connect externally confirmed setups to the current Gerchik level/ATR5 contract. S1–S3 confirmation predicates, coefficient migration, S5/S6 variants and execution profile remain unresolved; this simulator deliberately does not guess them. Year cohort remains exploratory, M5 is absent, independent untouched holdout is unverified. No market results, merge, deployment or trading are claimed.
