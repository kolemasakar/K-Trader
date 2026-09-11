# Candidate Rule Set v2.2 — Research Specification

Date: 2026-09-11
Status: FROZEN EXECUTABLE RESEARCH CANDIDATE / PREHOLDOUT EVALUATED / HOLDOUT UNTOUCHED / PRODUCTION UNCHANGED

## Objective

Extend the current v2.1 trend-pullback-continuation foundation with deterministic structural-space context derived from the legacy Knowledge Base, without importing unvalidated legacy constants as production rules.

Core:

`trend context -> pullback -> reclaim/continuation -> structural invalidation stop -> structural-space gate -> target 3R`

## Frozen executable v2.2

Executable harness:

`research/strategy_benchmark_v1/candidate_v2_2_backtest.py`

Frozen harness commit:

`9abb05d88912293cee3c254dd427a7127ce5bcc7`

Runtime harness SHA256:

`b8471af989090375dec9e25daae184814674a776ab9b46b45e660e35b368be08`

Prospective shadow protocol commit:

`0aba55432dc084181651b5f254c25800f309a754`

Holdout status: **UNTOUCHED**.

Production status: **NO CHANGE**.

## 1. Active INTRADAY v2.2 profile

v2.2 is the current frozen INTRADAY research candidate.

Base inherited from v2.1:
- H1 trend context;
- M15 pullback/reclaim trigger;
- structural SL;
- next executable M15 open;
- target `3R`;
- current frozen maximum hold `32 x M15 = 8h`;
- same-bar ambiguity: STOP first;
- fees, slippage and actual funding included.

v2.1 quality gates retained:
- H1 EMA20/EMA50 separation / ATR14 >= `0.20`;
- M15 signal body fraction <= `0.60`;
- structural risk distance >= `1.25%` of executed entry.

v2.2 adds deterministic H1 structural-space detection:
- causal pivot radius: `2` H1 bars;
- level clustering tolerance: `0.20 * ATR14_H1`;
- confirmed level requires >= `2` clustered pivots;
- trade allowed only if no confirmed obstacle is ahead (`open_space`) or nearest confirmed obstacle is >= `3R` away.

The current level detector is versioned:

`h1_pivot_cluster_v1`

It is intentionally simple and is not considered a final universal level model.

## 2. Preholdout v2.2 result

Report:

`/data/research/phase11g/strategy_benchmark_v1/combined_rules/v2_2_preholdout_report.json`

Report SHA256:

`577debe6e6a8a4f1954ffd5b27e872ce971d2de2074783a0abe2e69e79747f8a`

Candidate artifact:

`/data/research/phase11g/strategy_benchmark_v1/combined_rules/candidate_rule_set_v2_2.json`

Candidate SHA256:

`85e96f699e54d08a4795d50034fc40b2f69aea535ecf4b22b56ddfbb9417179b`

Results:

| Segment | Trades | WR | expectancy_R | PF_R |
|---|---:|---:|---:|---:|
| Development | 23 | 47.83% | +0.1003R | 1.1818 |
| Validation | 10 | 30.00% | +0.2507R | 1.3941 |
| Non-holdout | 37 | 45.95% | +0.2888R | 1.5592 |
| Stress non-holdout | 37 | 43.24% | +0.2741R | 1.5235 |

Promotion gate: **FAIL**.

Reasons:
- non-holdout sample <100;
- validation sample <30;
- non-holdout WR <50%;
- validation WR <50%.

Important: positive expectancy/PF does not authorize holdout because the preregistered user target and minimum sample gates were not met.

## 3. Current diagnostics

Non-holdout exit composition:
- 18 STOP;
- 8 TARGET;
- 11 TIME_EXIT.

TIME_EXIT behavior:
- 9 of 11 time exits positive;
- average TIME_EXIT approximately `+0.55R`.

Therefore current evidence does **not** justify lengthening the frozen v2.2 8h INTRADAY max-hold solely to improve results.

Directional concentration:
- LONG 34;
- SHORT 3.

This is a concentration warning, not evidence to disable SHORT or promote LONG-only behavior.

Structural detector observation:
- 35 of 37 non-holdout trades classified `open_space`.

This indicates `h1_pivot_cluster_v1` is too sparse to represent the full structural environment and motivates a separate **Level Context Layer v2** research track. It does not authorize retroactive modification of frozen v2.2.

## 4. Historical Knowledge interpretation

Historical files remain `HISTORICAL / RESEARCH REFERENCE`.

Do not automatically promote:
- ATR-used 60%/80% thresholds;
- fixed percentage/pip stops;
- mandatory VSA/volume gates;
- historical risk percentages;
- legacy timeframe/holding assumptions.

The useful retained concepts are:
- fixed vs floating/forming levels;
- trend-break / first-pullback levels;
- mirror levels;
- repeated-touch/limit levels;
- consolidation/protorgovka zones;
- false breaks and rejection tails;
- structural stop beyond thesis invalidation;
- technical room to target.

## 5. Multi-horizon architecture

Research envelopes remain provisional:
- FAST: H1/M15 -> M5, up to ~4h;
- INTRADAY: H4/H1 -> M15, ~8-12h envelope; current frozen v2.2 specifically uses 8h;
- SWING: D1/H4 -> H1, ~2-4 days;
- POSITION: W1/D1 -> H4, ~7-21 days.

TTL and max-hold are separate parameters. No universal time rule applies across profiles.

## 6. Evidence policy

Primary evidence unit = unique resolved setup family.

- <30 families: observation only;
- 30-49: diagnostics only;
- 50-99: hypotheses/ablation proposals allowed, no production change;
- >=100 diverse families: versioned recalibration proposal allowed.

Every strategy change requires a new version and fresh causal walk-forward/OOS evidence.

Validation and holdout must not be reused for iterative tuning of the same version.

No automatic live-rule mutation.

## 7. Prospective freeze

Frozen executable candidate timestamp is tied to commit `9abb05d...` on 2026-09-11.

First fully prospective M15 signal-bar boundary after the freeze:

`2026-09-11T20:00:00Z`

Frozen v2.2 rules must remain unchanged while prospective evidence accumulates.

## 8. Next research tracks

Proceed in parallel without modifying v2.2:

### A. Level Context Layer v2
Develop richer causal structural features for:
- trend-break levels;
- mirror levels;
- repeated-touch/limit levels;
- consolidation boundaries;
- false breaks;
- rejection tails;
- level age/strength/role change;
- floating-zone detection;
- next obstacle distance in R.

This track is **feature research**, not a v2.2 rule change.

### B. MFE/MAE diagnostics
Measure for frozen v2.2 and prior comparable setups:
- MFE_R;
- MAE_R;
- time-to-1R/2R/3R;
- time-to-MFE;
- whether STOP trades first achieved positive excursion;
- whether TIME_EXIT trades were still expanding or already decaying;
- outcome by exit reason, side, symbol, regime and structural context.

Diagnostics must not be used to retune v2.2 in place. Any resulting rule proposal becomes a new version.

## 9. Promotion objective remains unchanged

For nominal target RR 1:3:
- OOS WR target >=50%;
- expectancy_R >0 after costs;
- PF_R >1 mandatory, target >=1.5;
- stress-slippage survival;
- adequate unique-family sample;
- no single-symbol or single-regime domination;
- acceptable drawdown.

Until these gates pass, v2.2 remains a research candidate only.