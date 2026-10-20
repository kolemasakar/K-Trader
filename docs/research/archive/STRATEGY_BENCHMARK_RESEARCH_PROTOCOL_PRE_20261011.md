# K-Trader Strategy Benchmark Research Protocol

Date: 2026-09-11
Status: PLANNED RESEARCH / SEPARATE CHAT / NO PRODUCTION SEMANTICS CHANGE

## Purpose

Run a clean research program outside the current Phase 11G rule-design thread to identify simple, robust trading strategies that perform well on K-Trader's existing historical datasets.

The requested research sequence is:

1. research the strongest well-documented but simple trading strategies;
2. formalize each strategy into deterministic, testable rules;
3. backtest them on the available K-Trader historical market data under one common protocol;
4. select strategies with observed win rate strictly above 60%;
5. reject apparent high-win-rate strategies that are not economically viable or are statistically too weak;
6. extract the strongest recurring rules/components from the surviving strategies;
7. build a new candidate K-Trader rule set from those components;
8. re-test that combined rule set on historical data not used to construct it;
9. decide whether the new rule set deserves consideration as a future foundation.

This work is research-only. It does not modify the currently accepted production strategy, hard gates, Phase 11G catalogue, runtime configuration, or Phase 12 status.

## Canonical project boundaries

Repository:

`kolemasakar/K-Trader`

Production application SHA at handoff:

`81b79b281a4cc330b7c11058d202e0d74fb6d70e`

Repository `main` at research-handoff start:

`35cdbdd81882064ebd59c6b49fe7f2ff95aa2b21`

Production mode:

- read-only;
- provider: `binance_usdm`;
- continuous universe capture remains active;
- Phase 11G remains active;
- Phase 12 remains inactive.

Do not deploy, change production scanner configuration, relax the current production gates, or mutate the canonical catalogue as part of this benchmark research unless a later explicit approval is given.

## Existing research data

Primary research root:

`/data/research/phase11g`

Known useful sources include:

- provider-recorded universe snapshots;
- coherent MTF bundles;
- historical replay datasets;
- prospective-control shards/reports;
- catalogue entries for `SUIUSDT` and `XRPUSDT`;
- recent top-universe symbols and exported MTF bundles;
- available intervals include `5m`, `15m`, `1h`, `4h`, `1d` where the corresponding bundle is history-ready.

Before any benchmark, inventory the exact available date ranges, symbols, intervals, missing history, and content hashes. Do not assume equal coverage across symbols.

## Research principle

The goal is not to prove that a preferred strategy works. The goal is to compare simple strategies fairly under the same data, cost, execution, and validation rules.

A strategy must be specified before testing its holdout segment. No manual chart interpretation or discretionary post-hoc adjustment is allowed.

## Strategy discovery stage

Use current web research plus established trading literature to identify simple strategies with a credible public rationale and reproducible rule set. Prefer simple strategies with few parameters and avoid black-box machine learning for this study.

Initial families to investigate include, but are not limited to:

- moving-average trend following / crossover;
- trend pullback to a moving average;
- Donchian / highest-high lowest-low breakout;
- simple volatility or range breakout;
- Bollinger-band mean reversion;
- RSI mean reversion, with and without a trend filter;
- momentum continuation;
- channel breakout / channel mean reversion;
- simple MACD trend confirmation if it adds information beyond moving averages;
- simple price/volume confirmation rules when fully deterministic.

Do not accept internet claims such as "80% win rate" without an independently reproducible rule definition and backtest.

## Strategy formalization contract

For every candidate strategy record, before testing:

- strategy id and version;
- market type;
- timeframe(s);
- exact indicator formulas;
- exact parameter values;
- entry condition;
- entry timing and execution price convention;
- stop-loss rule;
- take-profit / exit rule;
- time exit if any;
- opposite-signal exit if any;
- re-entry / cooldown rule;
- long/short eligibility;
- position sizing assumption;
- transaction-cost assumptions;
- whether funding is relevant;
- data requirements;
- any market-regime filter.

The rules must be executable without human judgment.

## Anti-look-ahead requirements

Mandatory:

- closed bars only;
- no future candle information;
- no target/stop derived from future pivots;
- indicator values use only data available at the decision timestamp;
- fills occur only at a price available after the signal is known;
- no retroactive universe ranking fabrication;
- where provider-recorded universe snapshots are used, select the newest causal snapshot at or before the cutoff;
- missing symbol history is explicit and does not cause retrospective replacement unless the benchmark protocol explicitly defines a causal replacement policy in advance.

## Common backtest execution model

A single common execution model must be used across candidate strategies wherever possible.

At minimum include:

- entry on next executable bar/tick convention after signal confirmation;
- exchange fee assumption appropriate to Binance USD-M;
- slippage assumption;
- stop/target collision policy defined deterministically when both are touched in one bar;
- conservative intrabar ambiguity handling;
- no impossible fills outside candle ranges;
- no leverage-dependent artificial improvement of win rate;
- funding costs for strategies that hold positions across funding windows, or explicitly justify why funding is immaterial.

Run cost sensitivity at more than one plausible cost/slippage level.

## Data splitting

Do not optimize and judge on the same period.

Preferred sequence:

- development / exploratory segment;
- validation segment;
- untouched out-of-sample holdout;
- where data length allows, rolling or walk-forward validation.

Keep the exact split boundaries in the research artifacts.

Do not use the planned clean observation window `2026-09-12T06:00:00Z <= t < 2026-09-13T06:00:00Z` for parameter tuning. It may later be used only as additional untouched prospective evidence if appropriate.

## Required metrics

For every strategy, symbol, timeframe, split, and aggregate result report at least:

- number of trades;
- wins;
- losses;
- win rate;
- average win in R;
- average loss in R;
- expectancy in R/trade;
- profit factor;
- net return after costs;
- maximum drawdown;
- longest losing streak;
- median holding time;
- long vs short statistics;
- symbol-level concentration;
- timeframe-level concentration;
- sensitivity to fees/slippage;
- in-sample vs out-of-sample degradation.

When enough observations exist, add uncertainty/confidence intervals for win rate and expectancy.

## User-requested primary selection rule

Primary screen:

`observed win rate > 60%`

A candidate that does not exceed 60% does not enter the requested survivor set.

However, win rate alone is not sufficient. A >60% candidate must also be rejected or marked insufficient if any of the following applies:

- non-positive expectancy after costs;
- profit factor <= 1 after costs;
- result is driven by a tiny number of trades;
- result is dominated by one symbol or one isolated period without generalization;
- excessive drawdown relative to return;
- severe collapse on validation/holdout;
- result depends on unrealistic fills or ignored fees/slippage;
- high win rate is produced by very small wins and occasional catastrophic losses.

The >60% threshold is therefore a necessary requested filter, not proof of superiority.

## Minimum evidence policy

Do not present a strategy as validated merely because it crossed 60% on a small sample.

Preferred target:

- at least 100 completed trades for a headline strategy-level estimate when available;
- otherwise label the result `INSUFFICIENT SAMPLE` and show the exact count.

For unique market episodes / symbols, also report concentration so repeated correlated signals are not mistaken for independent evidence.

## Parameter policy

Keep parameter search intentionally small.

Examples:

- use a few standard moving-average pairs rather than dozens;
- use a few standard RSI thresholds rather than scanning every integer;
- use a few breakout lookbacks rather than exhaustive optimization.

If a parameter sweep is used:

- define the grid before the holdout;
- report all tested variants, not only the winner;
- prefer broad stable plateaus over a single sharp optimum;
- penalize complexity and fragile parameter sensitivity.

## Benchmark outputs

Create a dedicated research root, not the project root. Suggested host/container research location:

`/data/research/phase11g/strategy_benchmark_v1/`

Suggested artifact structure:

- `inventory.json`
- `strategy_catalogue.json`
- `protocol.json`
- `runs/<strategy_id>/...`
- `summary/leaderboard.json`
- `summary/leaderboard.csv`
- `summary/survivors_gt60.json`
- `summary/component_analysis.json`
- `combined_rules/candidate_rule_set_v1.json`
- `combined_rules/backtest_report.json`
- `combined_rules/holdout_report.json`

Every artifact should contain source-data identity and relevant hashes where feasible.

## Stage A — simple-strategy benchmark

Research and test a broad but manageable set of simple strategies under the common protocol.

Do not combine strategies during this stage.

Output one comparable leaderboard.

## Stage B — >60% survivor analysis

Take only strategies whose observed win rate is strictly above 60% and then evaluate the quality filters above.

For surviving candidates, identify which rule components recur:

- trend filter;
- entry timing;
- volatility condition;
- pullback/breakout condition;
- stop placement;
- profit-taking structure;
- session/time filters;
- volume confirmation;
- long/short asymmetry;
- market-regime dependency.

Do not infer that a component is useful merely because it appears in multiple similar strategies; measure its contribution with ablation or controlled comparison where possible.

## Stage C — candidate K-Trader rule synthesis

Build a deliberately simple candidate rule set from the strongest evidence.

Goals:

- fewer rules rather than more;
- no duplicate filters measuring the same thing twice;
- separate validity/safety checks from ranking/quality rules;
- retain deterministic structural risk management;
- avoid synthetic targets introduced only to force a desired RR;
- keep the rule set explainable.

Pre-register this rule set before the final historical holdout test.

## Stage D — re-test combined rules

Test the synthesized rule set from scratch on historical data.

Required comparison:

- combined candidate rule set;
- best individual simple strategies;
- current K-Trader Phase 11G strategy as a reference where comparable;
- buy-and-hold or no-trade baseline only where meaningful for the metric being compared.

The final decision must consider more than win rate:

- >60% requested threshold;
- positive expectancy;
- profit factor;
- drawdown;
- stability across symbols/time periods;
- out-of-sample performance;
- implementation complexity.

## Decision states

Use explicit final labels:

- `PROMISING_FOR_FURTHER_VALIDATION`
- `INSUFFICIENT_EVIDENCE`
- `REJECTED`

Do not label the new rules production-approved during this study.

## No-go actions during this research

Do not:

- deploy research code to production unless separately approved;
- alter the production scanner or trading gates;
- activate Phase 12;
- write synthetic outcomes into the Phase 11G catalogue;
- fabricate probability estimates;
- cherry-pick only profitable symbols or periods after seeing results;
- optimize on the final holdout;
- claim a strategy is good solely because win rate exceeds 60%.

## Final deliverable

The research chat should finish with:

1. evidence-backed shortlist of simple strategies studied;
2. exact deterministic definitions;
3. data inventory and backtest protocol;
4. full benchmark leaderboard;
5. strategies with win rate >60%;
6. quality/risk review of those survivors;
7. common-rule/component analysis;
8. proposed simple K-Trader candidate rule set;
9. fresh historical/holdout backtest of the combined rule set;
10. recommendation whether it is worth considering as a future foundation, with explicit uncertainties and no production change without approval.
