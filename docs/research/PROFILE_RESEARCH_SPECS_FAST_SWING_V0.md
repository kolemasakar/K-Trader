# K-Trader — FAST / SWING Profile Research Specs v0

Status: **RESEARCH ARCHITECTURE ONLY**  
Production impact: **NONE**  
Holdout authorization: **NONE**

## Purpose

Define separate preregistration envelopes for future profile research without copying INTRADAY v2.2 thresholds into other horizons and without changing the frozen v2.2 candidate.

These are architecture/specification boundaries, not trading rules.

## Common governance

For every profile:

- one profile = one strategy version and evidence chain;
- TTL-before-entry and max-hold-after-entry are separate parameters;
- signals/indicators use closed bars only;
- MTF context must be causally aligned to the decision time;
- structural invalidation precedes position sizing;
- costs include fees, execution slippage and funding when applicable;
- planned RR target begins at `>=3`, but realized payoff distribution must be measured separately;
- historical VSA/ATR/level thresholds remain features/hypotheses unless separately validated;
- no automatic production promotion;
- no cross-profile pooling of WR/expectancy/PF for a promotion decision.

Evidence gates remain:

- `<30` unique resolved setup families: observation only;
- `30–49`: diagnostics;
- `50–99`: hypotheses/ablation proposals only;
- `>=100` diverse families: versioned recalibration proposal may be considered, still requiring OOS/prospective evidence and explicit promotion.

## FAST profile — research envelope

### Intended use

Short-horizon continuation/reversal research where the trade is expected to resolve within several hours.

### Initial MTF architecture

- context: `H1 / M15`;
- setup: `M15`;
- trigger/execution timing: `M5`;
- research holding envelope: up to approximately `4h`.

The `4h` figure is an initial research envelope, not a live hard exit.

### Required research data

Minimum coherent closed-bar series:

- M5 sufficient for trigger and path reconstruction;
- M15 sufficient for setup/structure;
- H1 sufficient for regime/context;
- funding history for perpetual instruments;
- executable fee/slippage model.

### Questions to answer before candidate construction

1. Does M5 improve entry timing enough to offset greater noise and execution costs?
2. What setup TTL is appropriate in M5 bars after an M15 setup forms?
3. What fraction of successful trades reaches `0.5R/1R/2R/3R` by 15/30/60/120/240 minutes?
4. Which structural obstacle distance is relevant at M15/H1?
5. Does a lower-TF confirmation increase expectancy after costs rather than only increasing WR?
6. How much correlated risk appears when many crypto symbols trigger within the same short window?

### Explicit non-inheritance

Do **not** automatically inherit from INTRADAY v2.2:

- H1 EMA separation `0.20`;
- M15 body fraction `0.60`;
- min risk distance `1.25%`;
- 8h max hold;
- current structural-space detector thresholds.

These may be benchmark features only until separately preregistered and tested for FAST.

## SWING profile — research envelope

### Intended use

Multi-day continuation/reversal research where structural context is expected to mature more slowly than INTRADAY.

### Initial MTF architecture

- context: `D1 / H4`;
- setup/trigger: `H1`;
- optional execution refinement may later use M15 only if evidence justifies it;
- research holding envelope: approximately `2–4 days`.

The `2–4 days` figure is an initial research envelope, not a live hard exit.

### Required research data

Minimum coherent series:

- H1 deep enough for setup/path analysis;
- H4 for structural context;
- D1 for higher-timeframe regime;
- materially longer history than INTRADAY to produce adequate independent families;
- funding history covering multi-day holds;
- delisting/listing-age controls and provider continuity.

### Questions to answer before candidate construction

1. How should D1/H4 regime be represented without overfitting EMA thresholds?
2. What is the causal Level Context representation for H4/D1 obstacles?
3. What setup TTL in H1 bars preserves relevance while avoiding stale entries?
4. What max-hold envelope allows a nominal 3R target to mature without converting the strategy into POSITION trading?
5. How material is cumulative funding relative to initial `R`?
6. Are overnight/weekend and regime-transition risks materially different?
7. How should correlated multi-day exposure be capped across highly correlated symbols?

### Explicit non-inheritance

Do **not** automatically inherit:

- INTRADAY v2.2 entry thresholds;
- 8h max hold;
- M15 trigger rules;
- old ATR-used 60/80% thresholds;
- legacy fixed SL percentages;
- mandatory VSA rules.

## POSITION profile

Architecture reservation only:

- context: `W1 / D1`;
- setup/trigger: `H4`;
- indicative research horizon: approximately `7–21 days`.

No candidate construction is authorized yet. Data depth, regime count and funding/execution assumptions must be audited first.

## Relationship to frozen INTRADAY v2.2

Frozen INTRADAY v2.2 remains unchanged:

`H1 context -> M15 pullback/reclaim -> structural SL -> H1 structural-space gate -> nominal 3R -> frozen 8h max hold`

FAST/SWING/POSITION research must not be used to reinterpret its historical results or alter its prospective shadow protocol.

## Promotion boundary

A future FAST or SWING candidate requires, in order:

1. separate preregistered rule specification;
2. deterministic executable harness;
3. causal full-path development test;
4. validation not reused for repeated tuning;
5. fresh OOS/prospective evidence;
6. locked holdout only after predefined gates;
7. explicit human promotion decision.
