# Candidate Rule Set v2 — Trend Continuation with Pullback/Reclaim Entry

Date: 2026-09-11
Status: PREREGISTERED RESEARCH CANDIDATE / NO PRODUCTION CHANGE
Branch: `research-strategy-benchmark-v1`

## Purpose

Create the strongest current simple trade-search strategy supported by the combined K-Trader evidence, while preserving a clean mechanism for later improvement from real resolved trades.

This version supersedes neither production Phase 11G nor `candidate_rule_set_v1`; it is a new research candidate after the user changed the strategy-level acceptance objective from `win rate >60%` to allowing `win rate >=50%` when the intended reward:risk is `3:1`.

## Evidence synthesis used before freeze

The rule set combines these observations:

- standalone mean-reversion/re-entry produced the highest observed win rates in Strategy Benchmark v1, but the strongest high-win-rate candidate failed on expectancy, profit factor and validation;
- standalone trend/momentum/breakout variants more often produced positive expectancy / PF>1, but with much lower win rates and weak validation stability;
- earlier K-Trader breakout/retest research supported a deterministic trend-continuation architecture with HTF trend, structural breakout/retest, lower-timeframe confirmation and 3R risk/reward;
- earlier long-window replay showed strong regime dependence and repeated-family dependence, so repeated observations must not be treated as independent setups;
- earlier robustness work did not prove that ATR or volume/momentum should be universal hard gates;
- external literature provides support for moving-average/trend and trading-range-breakout rules in cryptocurrency markets, while also showing that transaction costs can materially change profitability.

## Design principle

Do not trade standalone mean reversion and do not chase raw breakouts.

Use:

`trend / continuation context -> controlled pullback -> reclaim / continuation confirmation -> structural stop -> 3R target`

Mean-reversion information is used only to improve entry timing inside an established directional context.

## Active research profile

Primary profile: `INTRADAY_CONTINUATION_V2`

- direction/context timeframe: `1h`;
- setup/trigger timeframe: `15m`;
- optional execution refinement timeframe: `5m` is recorded but is NOT an active eligibility gate in v2 because current M5 history is materially shorter;
- long and short are symmetric in rules;
- expected holding horizon: intraday;
- maximum holding time: `32 x 15m = 8h`;
- only one open candidate position per symbol/setup family.

## Hard validity gates

A candidate is invalid if any of the following fails:

1. causal closed-bar data only;
2. symbol is in the causal liquidity universe / frozen research panel for historical validation;
3. required 1h and 15m history is contiguous and history-ready;
4. one unambiguous directional H1 trend exists;
5. a valid M15 pullback/reclaim continuation trigger exists;
6. a positive structural stop distance can be defined;
7. target is exactly `3R` from executed entry and no known execution constraint makes that fill impossible;
8. costs, slippage and actual funding are included in evaluation;
9. no duplicate/repeated setup-family entry is opened while the same family is active or in cooldown.

Volume, momentum, D1 alignment and ATR-normalized quality are recorded as quality features, not universal hard gates in v2.

## Direction rule — H1

Use EMA(20), EMA(50), Wilder ATR(14).

LONG context requires all:

- `EMA20_H1 > EMA50_H1`;
- `EMA20_H1(current) > EMA20_H1(3 closed H1 bars ago)`.

SHORT context is symmetric:

- `EMA20_H1 < EMA50_H1`;
- `EMA20_H1(current) < EMA20_H1(3 closed H1 bars ago)`.

The H1 trend state used by an M15 signal must come from the latest fully closed H1 candle available at that M15 decision time.

## Pullback / reclaim trigger — M15

Indicators: EMA(20), EMA(50), Wilder RSI(14), Wilder ATR(14).

A LONG trigger requires:

- H1 LONG context;
- within the previous five fully closed M15 bars including the signal bar, price has made a pullback evidenced by at least one bar with `low <= EMA20_M15` OR `RSI14 < 45`;
- the signal bar closes above `EMA20_M15`;
- `RSI14 >= 50` on the signal bar;
- signal-bar close is greater than the previous M15 bar high;
- signal bar is bullish (`close > open`).

SHORT is symmetric:

- H1 SHORT context;
- within the previous five bars at least one bar has `high >= EMA20_M15` OR `RSI14 > 55`;
- signal bar closes below `EMA20_M15`;
- `RSI14 <= 50`;
- signal-bar close is below previous M15 bar low;
- signal bar is bearish (`close < open`).

Entry occurs at the next executable M15 open with adverse slippage applied.

## Stop

Use the structural extreme of the five-bar pullback window plus a small volatility buffer:

- LONG: `SL = min(low[-5:]) - 0.15 * ATR14_M15`;
- SHORT: `SL = max(high[-5:]) + 0.15 * ATR14_M15`.

If the executed next-bar entry no longer leaves a positive stop distance, the signal is invalid.

ATR is used here to normalize the structural buffer, not as an independent profitability gate.

## Target and exits

Initial target:

- `TP = entry + 3 * risk_distance` for LONG;
- `TP = entry - 3 * risk_distance` for SHORT.

Intrabar ambiguity is conservative: if stop and target are both reachable inside one unresolved candle, count STOP first.

Other exits:

- hard stop;
- hard 3R target;
- time exit at the next executable open after 32 completed M15 bars if neither stop nor target has resolved;
- no discretionary early profit taking in v2.

## Duplicate-family / cooldown rule

A setup family is identified by at least:

`(symbol, direction, H1 trend episode, M15 pullback episode)`.

Only one active entry is allowed per family. After resolution, no re-entry from the same pullback episode is allowed. A new entry requires a new pullback/reclaim sequence.

This prevents repeated-bar observations from inflating effective sample size.

## Quality features recorded but not hard-gated

For every eligible and near-miss setup record:

- D1 EMA20/EMA50 direction and EMA20 slope alignment;
- H1 EMA separation / H1 ATR;
- M15 pullback depth / ATR;
- M15 signal candle body/range;
- relative quote volume versus previous 20-bar mean/median;
- RSI depth and reclaim strength;
- distance to recent structural highs/lows;
- expected fee/slippage/funding burden in R;
- long/short side;
- symbol and liquidity rank;
- UTC hour/session;
- setup-family identity.

These become candidates for later evidence-driven ranking, not silent live-rule changes.

## Economics and acceptance objective

Nominal payoff is `1R loss / 3R target`.

Gross break-even win rate for exact 3:1 outcomes is 25% before costs. At 50% wins and 50% full-stop losses the gross expectancy is `+1.0R/trade` and gross profit factor is `3.0`.

User-requested strategy target:

- observed OOS win rate `>=50%` where sample is sufficient;
- positive net expectancy after fees/slippage/funding;
- profit factor `>1` mandatory, target `>=1.5`;
- no single-symbol or single-regime domination;
- acceptable drawdown relative to expectancy;
- stability under stress slippage.

A lower win rate is not automatically unprofitable mathematically, but v2 should not be promoted as meeting the requested objective unless OOS win rate reaches 50% with the other economic tests satisfied.

## Research validation sequence

1. freeze this exact rule set and hash it;
2. run only development + validation / walk-forward first;
3. do not alter rules after seeing those results and still call the same version v2;
4. only if the preregistered promotion gate is passed, open the untouched holdout once;
5. otherwise keep holdout untouched and create a separately versioned v2.1 only from documented new evidence.

## Continuous improvement from real trades

The production-learning design is evidence accumulation, not uncontrolled online self-modification.

For every real/demo signal, store the full causal feature vector, execution data and final outcome including:

- intended and realized entry/SL/TP;
- actual fees, slippage and funding;
- realized R;
- maximum favorable excursion (MFE);
- maximum adverse excursion (MAE);
- holding time;
- setup-family id;
- all quality features above;
- exact strategy version and source-data/config hashes.

Evidence gates:

- `<30` resolved unique families: observation only;
- `30-49`: preliminary diagnostics, no rule change;
- `50-99`: component/ablation analysis may propose changes, but no automatic promotion;
- `>=100` resolved unique families with reasonable symbol/regime spread: allow a versioned recalibration proposal;
- every proposed change becomes a new preregistered version and must survive walk-forward/OOS before production consideration.

Preferred statistical tracking:

- Wilson interval for win rate;
- bootstrap/confidence interval for expectancy;
- profit factor and drawdown;
- calibration by score bucket;
- long/short and regime decomposition;
- unique-family rather than raw-record counts;
- sensitivity to fees/slippage/funding.

## Production boundary

This document is research-only. It does not change production Phase 11G, scanner configuration, risk controls, deployment SHA, or Phase 12 state.
