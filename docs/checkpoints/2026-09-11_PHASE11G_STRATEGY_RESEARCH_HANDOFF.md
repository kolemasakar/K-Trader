# Phase 11G — Strategy Research Handoff Checkpoint

Date: 2026-09-11
Status: CURRENT PROJECT FROZEN FOR SEPARATE STRATEGY BENCHMARK RESEARCH

## Decision

The current Phase 11G gate-audit thread is intentionally paused before changing any production trading rule.

A separate research chat will investigate simple, strong trading strategies from first principles, backtest them on the existing K-Trader historical datasets, retain strategies with observed win rate strictly above 60% subject to economic/statistical quality checks, synthesize a new candidate rule set from the strongest recurring components, and re-test that combined rule set on untouched historical/holdout data.

No current production rule is changed by this decision.

## Canonical repository state

Repository:

`kolemasakar/K-Trader`

Canonical `main` at handoff start:

`35cdbdd81882064ebd59c6b49fe7f2ff95aa2b21`

This SHA is documentation-only ahead of the deployed application SHA.

## Production application state

Accepted deployed application SHA:

`81b79b281a4cc330b7c11058d202e0d74fb6d70e`

Accepted runtime state:

- production healthy;
- mode `read_only`;
- `data_ready=true`;
- provider `binance_usdm`;
- provider-recorded universe capture active;
- single-writer prospective-control hardening deployed and accepted;
- unique-primary-level survivorship diagnostic deployed and accepted;
- no causal capture gap >300s observed across the last deployment;
- Phase 11G active;
- Phase 12 inactive.

## Accepted Phase 11G evidence at handoff

Cumulative non-overlap prospective evidence:

```text
logical cutoffs          438
symbol slots            8760
history pass            7352
history fail            1391
analysis errors            17
decision records       90621
tradable records            0
```

Cumulative sequential funnel:

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

Recent two-window survivorship diagnostic:

```text
record funnel:       852 -> 309 -> 216 -> 40 -> 10 -> 0 -> 0 -> 0
unique-level funnel:  28 ->  12 ->   8 ->  4 ->  3 -> 0 -> 0 -> 0
```

Interpretation accepted before the research pivot:

- per-cutoff counts materially overstate effective independent structural evidence;
- 10 recent TTL-pass records represented only 3 distinct primary structural levels;
- natural RR>=3 geometry existed, but recent examples failed the ATR gate by a very large margin;
- current `grade C` after hard rejection is not independent evidence because the scoring code caps rejected decisions at grade C / score <=69;
- no hard gate was changed before this handoff.

## Gate audit findings retained for later comparison

The following items are hypotheses/questions, not approved production changes:

- HTF blanket directional alignment may be appropriate for continuation setups but potentially too blunt for reversal/trap setups;
- primary-level `STRONG` currently derives mainly from touch count and may be too simple as a universal quality gate;
- geometry target selection may conflate nearest obstacle with primary structural target;
- grade A/A+ currently overlaps with factors already used as hard rejects, creating possible double counting;
- ATR-used <=80% may need methodology review, although recent RR>=3 cases were far beyond any modest threshold adjustment;
- FAST/M5 TTL60 remains accepted, while setup re-arm semantics may deserve study;
- RR>=3 is not being relaxed based on current evidence.

These questions are deliberately deferred while the new benchmark study establishes an independent evidence base from simpler strategies.

## Research handoff protocol

Canonical research instructions:

`docs/research/STRATEGY_BENCHMARK_RESEARCH_PROTOCOL.md`

The separate research chat must use that protocol as the operating contract.

## Existing research data

Primary root:

`/data/research/phase11g`

Important available artifact classes include:

- recorded universe snapshots;
- coherent MTF bundles;
- prospective-control shards and reports;
- historical replay studies;
- two-entry dataset catalogue (`SUIUSDT`, `XRPUSDT`);
- recent research diagnostics and survivorship artifacts.

The new research must inventory exact symbol/timeframe/date coverage before backtesting rather than assume uniform data availability.

## New research goal

The new study should answer:

> Which simple, reproducible trading strategies produce the strongest robust performance on the K-Trader historical datasets under realistic costs and causal execution, and can their strongest recurring components be combined into a simpler and better candidate foundation than the current rule stack?

User-requested primary screen:

`observed win rate > 60%`

Required additional quality checks:

- positive expectancy after costs;
- profit factor >1 after costs;
- sufficient trade count or explicit `INSUFFICIENT SAMPLE` label;
- acceptable drawdown relative to return;
- symbol/time-period robustness;
- out-of-sample/holdout survival;
- realistic fees, slippage and fills;
- no catastrophic-tail structure hidden behind a high win rate.

## Planned technical observation pause remains unchanged

Development freeze:

`2026-09-12 09:00 Kyiv -> 2026-09-13 09:00 Kyiv`

UTC observation window:

`2026-09-12T06:00:00Z <= t < 2026-09-13T06:00:00Z`

During that window:

- production read-only capture continues;
- health/freshness monitoring continues;
- code/config/deploy changes remain frozen except emergency recovery;
- heavy production-host replay remains frozen;
- the clean observation window must not be used for tuning the new strategy rules.

## Project invariants during separate research

Until an explicit later decision:

- current production semantics remain unchanged;
- current production application remains pinned to the accepted deployed SHA unless emergency recovery is required;
- no research strategy is production-approved merely because it backtests well;
- Phase 12 remains inactive;
- no synthetic outcomes or fabricated probabilities are permitted;
- research outputs belong under dedicated research/documentation subdirectories, not repository or storage roots.

## Resume condition for this chat/thread

Resume the current Phase 11G architecture/gate discussion only after the separate strategy benchmark produces:

- comparable simple-strategy backtests;
- the >60% survivor set;
- robust quality metrics;
- component/ablation evidence;
- a pre-registered combined candidate rule set;
- a fresh holdout result.

At that point compare the independent benchmark evidence against the current Phase 11G rules and decide whether to retain, redesign, or replace the existing strategic foundation.
