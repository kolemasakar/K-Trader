# BOOTSTRAP PACKAGE — K-Trader Strategy Benchmark Research

Date: 2026-09-11
Target: NEW CHAT
Purpose: independent research into simple, strong trading strategies and comparative backtesting on existing K-Trader data.

## Mission

Pause the current Phase 11G gate-redesign discussion. Start a separate evidence-first research program.

Research the strongest but simple trading strategies, formalize them into deterministic rules, backtest them under a common causal execution model using the existing K-Trader historical datasets, select strategies with observed win rate strictly above 60% subject to robustness/economic checks, extract their strongest recurring components, synthesize a new simple candidate K-Trader rule set, then re-test that combined rule set on untouched historical/holdout data.

The research must answer whether that new evidence-based rule set is strong enough to justify later consideration as a replacement or redesign foundation for the current strategy stack.

## Canonical sources to read first

Repository:

`kolemasakar/K-Trader`

Read these files before doing research:

1. `docs/research/STRATEGY_BENCHMARK_RESEARCH_PROTOCOL.md`
2. `docs/checkpoints/2026-09-11_PHASE11G_STRATEGY_RESEARCH_HANDOFF.md`
3. `docs/checkpoints/2026-09-11_PHASE11G_SURVIVORSHIP_AND_PRE_FREEZE_ACCEPTANCE.md`
4. `docs/PROSPECTIVE_SURVIVORSHIP_DIAGNOSTIC.md`
5. `docs/PROSPECTIVE_CONTROL_SPEC.md`
6. `docs/PHASE_11G_CHECKPOINT.md`

Do not substitute memory for these canonical documents when a current repo fact is available.

## Canonical state at handoff

Repository `main` before adding this handoff documentation:

`35cdbdd81882064ebd59c6b49fe7f2ff95aa2b21`

Accepted deployed application SHA:

`81b79b281a4cc330b7c11058d202e0d74fb6d70e`

Production:

- healthy;
- read-only;
- provider `binance_usdm`;
- continuous provider-recorded universe capture active;
- Phase 11G active;
- Phase 12 inactive.

Do not deploy or change production semantics during the benchmark research without explicit approval.

## Existing data root

Primary research root:

`/data/research/phase11g`

The first operational step is a read-only inventory of the available datasets:

- symbols;
- intervals;
- date/time coverage;
- bar counts;
- coherent MTF bundles;
- universe archives/snapshots;
- missing history;
- current content hashes / provenance.

Do not assume every symbol has the same coverage.

## Important existing Phase 11G evidence

Cumulative prospective evidence before the research pivot:

```text
logical cutoffs          438
symbol slots            8760
history pass            7352
history fail            1391
analysis errors            17
decision records       90621
tradable records            0
```

Current sequential funnel:

```text
HTF aligned             2374
-> strong level          740
-> valid geometry         527
-> ATR <= 80              229
-> TTL60                   20
-> RR >= 3                  0
-> Grade A/A+               0
-> tradable                 0
```

Recent effective survivorship:

```text
record funnel:       852 -> 309 -> 216 -> 40 -> 10 -> 0 -> 0 -> 0
unique-level funnel:  28 ->  12 ->   8 ->  4 ->  3 -> 0 -> 0 -> 0
```

Do not use these current gates as assumptions for the new benchmark. They are a reference system to compare against later.

## Research questions

The research must establish:

- which simple strategy families have credible reproducible definitions;
- which actually work on the available K-Trader historical data;
- which exceed 60% observed win rate;
- whether those >60% results retain positive expectancy after realistic costs;
- whether results survive validation/holdout;
- which rules/components repeatedly improve performance;
- whether a small combined rule set outperforms the individual components without overfitting;
- whether that combined rule set is strong enough to justify later redesign of K-Trader.

## Web research requirement

Use current web research and established literature to build the candidate strategy catalogue.

Prefer:

- academic or institutional research;
- established technical-analysis literature with precise rules;
- public strategies with deterministic definitions;
- simple strategies with few parameters.

Treat influencer/blog claims of extreme win rate as unverified until independently reproduced.

## Candidate strategy families

Do not limit the study to this list, but investigate these families first because they are simple and reproducible:

- moving-average trend following/crossover;
- moving-average trend pullback;
- Donchian/highest-high lowest-low breakout;
- simple range/volatility breakout;
- Bollinger-band mean reversion;
- RSI mean reversion, optionally with a trend filter;
- simple momentum continuation;
- channel breakout / channel mean reversion;
- simple MACD confirmation if it adds distinct information;
- simple volume-confirmed price patterns if rules can be made deterministic.

Avoid black-box ML in this benchmark.

## Formalization rule

Before any holdout test, every strategy must have a written versioned rule definition containing:

- timeframe;
- indicators and formulas;
- exact parameters;
- entry condition;
- execution timing convention;
- stop-loss;
- target/exit;
- time exit if used;
- re-entry/cooldown;
- long/short logic;
- cost model;
- required data;
- any regime filter.

No discretionary chart reading.

## Backtest validity requirements

Mandatory:

- closed bars only;
- no look-ahead;
- causal indicators;
- deterministic fills;
- conservative resolution of stop/target ambiguity inside one candle;
- realistic Binance USD-M fees;
- slippage;
- funding where relevant;
- no impossible fills;
- no retroactive universe reconstruction when causal universe snapshots are required;
- identical execution assumptions across strategies wherever possible.

## Timeframes

Inventory first, then benchmark across the timeframes for which reliable coherent data exists.

Priority candidates:

- 5m;
- 15m;
- 1h.

4h/1d may be used as trend/context inputs where a strategy definition requires them, or as standalone strategy timeframes if there is enough historical sample.

Do not force every strategy onto every timeframe if its premise is incompatible.

## Dataset split

Do not optimize and score on the same data.

Use, where coverage permits:

- exploratory/development segment;
- validation segment;
- untouched holdout;
- walk-forward/rolling validation.

Pre-register split boundaries and strategy parameters before holdout evaluation.

Do not tune on the clean technical-pause observation window:

`2026-09-12T06:00:00Z <= t < 2026-09-13T06:00:00Z`

## Primary selection rule requested by user

A strategy can enter the survivor set only when:

`observed win rate > 60%`

But >60% win rate is not by itself acceptance.

Also require review of:

- number of trades;
- expectancy after costs;
- profit factor;
- net return;
- maximum drawdown;
- average win/loss in R;
- losing streak;
- symbol/timeframe concentration;
- fee/slippage sensitivity;
- out-of-sample degradation.

Reject or mark insufficient evidence if >60% is generated by tiny samples, catastrophic rare losses, unrealistic execution, one-symbol concentration, or holdout collapse.

Preferred headline sample size: at least 100 completed trades where available. Otherwise label `INSUFFICIENT SAMPLE` with the exact count.

## Research output root

Use a dedicated research directory:

`/data/research/phase11g/strategy_benchmark_v1/`

Do not write new files into storage or repository roots.

Recommended structure:

```text
strategy_benchmark_v1/
  inventory.json
  protocol.json
  strategy_catalogue.json
  runs/
  summary/
    leaderboard.json
    leaderboard.csv
    survivors_gt60.json
    component_analysis.json
  combined_rules/
    candidate_rule_set_v1.json
    backtest_report.json
    holdout_report.json
```

## Work phases

### A. Research and catalogue simple strategies

- web/literature research;
- exact deterministic definitions;
- shortlist simple candidates;
- avoid excessive parameter variants.

### B. Build/verify common benchmark harness

- data inventory;
- cost/execution model;
- no-look-ahead tests;
- deterministic reproducibility;
- test fixtures for stop/target ambiguity;
- common metrics.

### C. Backtest every strategy fairly

- same data splits where applicable;
- same cost model;
- per-symbol/per-timeframe results;
- aggregate leaderboard;
- all variants reported, not just winners.

### D. Select >60% survivor set

- apply strict `win rate > 60%` filter;
- then apply economic/robustness checks;
- distinguish `PROMISING`, `INSUFFICIENT`, `REJECTED`.

### E. Component analysis

Identify which components recur among robust survivors:

- trend alignment;
- pullback/breakout structure;
- volatility conditions;
- entry timing;
- stop placement;
- exit design;
- volume confirmation;
- session/time filters;
- long/short asymmetry.

Use controlled comparisons/ablation where possible. Do not infer causality from simple co-occurrence.

### F. Synthesize candidate K-Trader rule set

Create the simplest rule set supported by evidence.

Separate:

- hard validity/safety requirements;
- strategy conditions;
- ranking/quality score.

Avoid duplicated filters and rules that measure the same phenomenon twice.

### G. Re-test combined rules

Pre-register `candidate_rule_set_v1` before final holdout.

Compare:

- combined candidate rule set;
- best individual simple strategies;
- current K-Trader Phase 11G logic where comparable.

Use untouched holdout/walk-forward evidence.

## Required final report

The final research result must contain:

1. strategy catalogue and research sources;
2. exact deterministic rule definitions;
3. data inventory;
4. backtest methodology;
5. cost/execution assumptions;
6. complete leaderboard;
7. all strategies with win rate >60%;
8. sample-size and robustness review;
9. expectancy/profit factor/drawdown for survivors;
10. component/ablation analysis;
11. proposed candidate K-Trader rules;
12. combined-rule historical test;
13. untouched holdout/walk-forward result;
14. comparison with current K-Trader approach;
15. recommendation: `PROMISING_FOR_FURTHER_VALIDATION`, `INSUFFICIENT_EVIDENCE`, or `REJECTED`.

## Hard prohibitions

Do not:

- change production strategy or config;
- deploy benchmark code to production without explicit approval;
- activate Phase 12;
- tune on the final holdout;
- cherry-pick symbols after seeing performance;
- report only the best parameter combination while hiding failed variants;
- ignore fees/slippage/funding where material;
- claim >60% win rate means profitability without expectancy;
- fabricate probabilities or synthetic outcomes.

## First actions in the new chat

1. Restore state from this bootstrap and the canonical repo docs.
2. Verify current repo/runtime identities read-only.
3. Inventory `/data/research/phase11g` data coverage.
4. Research and propose a concise strategy candidate catalogue with sources.
5. Freeze the common backtest protocol and strategy definitions.
6. Only then implement/run backtests.
7. Report progress incrementally with exact artifact paths and hashes.

Do not ask the user to repeat project facts already contained in the canonical handoff documents.
