# Strategy Synthesis Checkpoint — v2.1

Date: 2026-09-11
Status: RESEARCH ONLY / PROVISIONAL BEST CURRENT CANDIDATE / HOLDOUT UNTOUCHED

## Scope

This checkpoint combines the current Strategy Benchmark v1 evidence with research conclusions imported from the previous K-Trader strategy-research chat. Production is unchanged.

The imported prior-chat metrics are retained as prior evidence and should be artifact-level revalidated if the original historical replay artifacts are later re-opened. They are not treated as new holdout evidence.

## Prior-chat evidence incorporated

Earlier Breakout / Retest Trend-Continuation MVP used:

- D1 EMA20/EMA50 plus EMA20 slope for directional context;
- H1 breakout -> retest -> continuation structure;
- lower-timeframe execution confirmation;
- structural SL plus buffer;
- nominal 3R target;
- long and short;
- volume/momentum as evidence features rather than universally proven hard gates.

Reported earlier replay observations:

- 90D: 24 H1 structures / 10 families; 12 full setups / 9 families; 8 ATR-compatible / 6 families; 3 TP / 5 SL; 37.5% win rate; +0.50R expectancy in that sample;
- 180D production-depth: 69 structures / 28 families; 34 full setups; 15 candidate-like / 11 families; 4 TP / 11 SL; 26.67% win rate; +0.067R expectancy; family-first approximately +0.091R;
- early 90D approximately -0.429R versus late 90D approximately +0.500R, indicating strong regime dependence;
- repeated-family exposure was material;
- side asymmetry was not stable enough to justify disabling one side;
- ATR-rejected resolved examples did not prove the ATR gate improved expectancy;
- `momentum impulse = false` was the only preliminary stable-positive momentum subgroup, but was explicitly considered post-hoc and insufficient as a standalone hard gate.

## Current Strategy Benchmark v1 evidence

Nine simple strategies x 3 timeframes produced 27 combinations under one cost/execution protocol.

No combination passed the original `win rate >60%` survivor gate.

Main pattern:

- mean-reversion/re-entry produced the highest win rates but failed expectancy / PF / validation robustness;
- trend/momentum/breakout variants more often produced positive expectancy or PF>1 but with lower win rates and unstable validation;
- therefore standalone mean reversion is not selected as the foundation;
- mean-reversion information is instead used as pullback/entry timing inside a directional continuation setup.

## User objective update

The user explicitly relaxed the strategy-level win-rate objective:

- nominal RR remains `1:3`;
- 50% successful trades is acceptable.

At exact 3:1 before costs, break-even win rate is 25%. A 50/50 TP/SL distribution would imply gross +1R expectancy per trade and gross PF 3.0. Actual evaluation remains after fees, slippage and funding.

## Candidate v2 result

Preregistered architecture:

`H1 trend -> M15 pullback -> M15 reclaim/continuation -> structural stop -> 3R target`

Pre-holdout result:

- development: 125 trades, WR 34.4%, expectancy -0.148R;
- validation: 44 trades, WR 31.8%, expectancy -0.122R;
- non-holdout: 170 trades, WR 35.3%, expectancy -0.118R;
- holdout remained closed.

v2 therefore failed.

## v2 ablation findings

The most useful robust direction was not a stronger momentum filter. Instead the evidence favored rejecting already-expanded continuation candles and rejecting very narrow structural R-units.

The retained v2.1 refinements are:

1. H1 trend quality: `abs(EMA20-EMA50)/ATR14 >= 0.20`;
2. non-impulsive M15 signal candle: `body/range <= 0.60`;
3. minimum structural stop distance after next-open execution: `risk_distance/entry >= 1.25%`.

No hard volume gate, D1-alignment gate, universal ATR-profitability gate or long/short gate is introduced.

## Candidate v2.1

Canonical research document:

`docs/research/CANDIDATE_RULE_SET_V2_1.md`

Machine-readable artifact:

`/data/research/phase11g/strategy_benchmark_v1/combined_rules/candidate_rule_set_v2_1.json`

SHA-256:

`95d730f4a5273d692f4a6877413b9a6eb725cde1db95afb99858ee52ddfd661f`

Pre-holdout report:

`/data/research/phase11g/strategy_benchmark_v1/combined_rules/v2_1_preholdout_report.json`

SHA-256:

`5fb7fdbf8f890c6eb1ae7b1cf03ceea56e9bd58fbc5d0e4210cdd14f042d3f8c`

## v2.1 pre-holdout result

Development:

- completed trades: 55;
- WR: 45.45%;
- expectancy: +0.103R;
- PF_R: 1.192;
- max drawdown trade stream: 4.90R.

Validation:

- completed trades: 25;
- WR: 36.0%;
- expectancy: -0.014R;
- PF_R: 0.977;
- max drawdown trade stream: 8.24R.

Combined non-holdout:

- completed trades: 85;
- WR: 43.53%;
- expectancy: +0.086R;
- PF_R: 1.157;
- top-symbol trade share: 9.4%.

Stress slippage:

- completed trades: 86;
- WR: 40.70%;
- expectancy: +0.054R;
- PF_R: 1.097.

The result is economically better than v2 overall but does not satisfy the requested 50% OOS target and does not yet have sufficient validation sample.

## Current decision

`candidate_rule_set_v2_1` is the strongest current simple evidence-based research foundation, but it is NOT validated and NOT production-approved.

Holdout remains unopened because the preregistered promotion gate failed.

The next evidence source should be genuinely new resolved trades / prospective signals, not further mining of the same validation sample.

## Learning architecture

For each prospective/demo/real setup capture:

- complete causal feature vector;
- strategy version and config/data hashes;
- intended and executed entry/SL/TP;
- actual fees/slippage/funding;
- MFE / MAE;
- holding time;
- realized R;
- unique setup-family identity;
- rejected near-miss records as well as accepted trades.

Evidence stages:

- <30 unique resolved families: observation only;
- 30-49: diagnostics only;
- 50-99: component/ablation proposals allowed, no live rule mutation;
- >=100 diverse resolved families: versioned recalibration proposal allowed;
- every revision must be preregistered and must survive fresh walk-forward/OOS evidence before production consideration.

No automatic live self-modification is permitted.
