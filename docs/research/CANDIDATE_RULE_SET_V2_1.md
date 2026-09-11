# Candidate Rule Set v2.1 — Quality-Gated Trend Pullback Continuation

Date: 2026-09-11
Status: PREREGISTERED RESEARCH REFINEMENT / HOLDOUT STILL UNTOUCHED / NO PRODUCTION CHANGE

## Why v2.1 exists

`candidate_rule_set_v2` improved trade construction but failed the pre-holdout target: its equal-risk expectancy in R was negative and observed win rate was below the user-requested 50% target.

A bounded non-holdout ablation was then performed using only v2 development/validation trades. The final 20% holdout remained unopened.

The only refinement retained for v2.1 is a simple three-part quality gate that was directionally consistent with both current development/validation evidence and earlier K-Trader replay observations:

1. avoid weak H1 trends;
2. avoid chasing an already impulsive M15 confirmation candle;
3. avoid entries where the structural stop is so close that costs/noise dominate the risk unit.

Volume is NOT promoted to a hard gate. D1 alignment is NOT promoted to a hard gate. Long/short asymmetry is NOT promoted to a hard gate because earlier and current samples disagree about which side is stronger.

## Base setup inherited from v2

The strategy remains:

`H1 directional trend -> M15 pullback -> M15 reclaim/continuation confirmation -> structural SL -> 3R target`

H1 direction:

- LONG: EMA20 > EMA50 and EMA20 > EMA20 from 3 closed H1 bars earlier;
- SHORT: symmetric.

M15 pullback/reclaim:

- pullback must occur within the previous 5 closed M15 bars;
- LONG pullback: low touches/breaches EMA20 or RSI14 <45;
- LONG reclaim trigger: close > EMA20, RSI14 >=50, close > prior M15 high, bullish candle;
- SHORT symmetric using high/EMA20, RSI14 >55, reclaim below EMA20, RSI14 <=50, close below prior M15 low, bearish candle.

Entry: next executable M15 open with adverse slippage.

SL:

- LONG: minimum low of the 5-bar pullback window minus `0.15 * ATR14_M15`;
- SHORT: maximum high plus `0.15 * ATR14_M15`.

TP: exactly `3R` from executed entry.

Maximum holding time: `32 x 15m = 8h`.

Stop/target same-bar ambiguity: STOP first.

## New hard quality gates in v2.1

### 1. H1 trend separation

Require:

`abs(EMA20_H1 - EMA50_H1) / ATR14_H1 >= 0.20`

Purpose: reject nearly flat/indeterminate H1 trends without requiring extreme trend strength.

### 2. Do not chase an impulse candle

Require M15 signal candle:

`abs(close - open) / (high - low) <= 0.60`

Purpose: continuation confirmation is required, but already-expanded impulse candles are rejected. This is consistent with earlier replay evidence in which `momentum impulse = false` was the only preliminary stable-positive momentum subgroup; that earlier result remains supportive rather than independently conclusive.

### 3. Minimum structural risk distance

After next-open execution and slippage, require:

`abs(entry - structural_SL) / entry >= 0.0125`

That is a minimum stop distance of `1.25%` of entry price.

Purpose: avoid defining an R-unit so narrow that round-trip fees/slippage and ordinary intrabar noise consume too much of 1R. This is an execution-quality constraint, not an ATR profitability gate.

No maximum stop-distance profitability gate is introduced in v2.1. Position sizing is expected to normalize account risk per trade.

## Features deliberately NOT hard-gated

Still recorded for later evidence:

- D1 alignment;
- relative volume;
- pullback depth;
- H1 trend strength above the minimum;
- funding sign/magnitude;
- UTC time/session;
- symbol/liquidity rank;
- long/short side.

## Evaluation metric correction

Because K-Trader sizes positions from stop distance, the primary economics must be measured in **R**, not only in unscaled percentage return.

Primary metrics for v2.1:

- `expectancy_R`;
- `profit_factor_R` calculated from positive/negative realized R;
- win rate;
- drawdown in R;
- realized fees/slippage/funding;
- unique setup-family count.

Raw percentage-return PF may still be reported, but it is secondary.

## Promotion objective

User-requested target for a 3R strategy:

- OOS win rate `>=50%`;
- positive `expectancy_R` after all costs;
- `profit_factor_R >1`, target `>=1.5`;
- adequate sample and symbol/regime spread;
- stress-slippage survival.

A strategy with win rate below 50% can be mathematically profitable at 3R, but it does not satisfy the requested performance target and therefore is not promoted as meeting the objective.

## Holdout gate

The untouched holdout may be opened exactly once only if development + validation provide enough evidence under these frozen v2.1 rules.

If v2.1 fails pre-holdout, do not tune v2.1 and then reuse the same name. Create a new version and preserve the holdout.

## Continuous learning

Carry forward the v2 evidence loop:

- log every eligible, rejected-near-miss, and executed setup with exact strategy version and causal features;
- record actual entry/SL/TP, fees, slippage, funding, MFE, MAE, hold time and realized R;
- use unique setup-family counts, not repeated bar observations;
- <30 resolved families: observation only;
- 30-49: diagnostics only;
- 50-99: component/ablation proposals allowed, no automatic rule promotion;
- >=100 diverse resolved families: versioned recalibration proposal allowed;
- every change requires a new preregistered version and fresh walk-forward/OOS validation.

Production rules must never mutate automatically from one or a few trades.
