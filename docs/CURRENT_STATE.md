# K-Trader Current State

Updated: 2026-09-11

## Canonical references

Latest production/runtime continuity is governed by the Phase 11G deployment/checkpoint chain in `docs/checkpoints/`.

Latest independent strategy-research checkpoint:

`docs/checkpoints/2026-09-11_STRATEGY_V2_2_PREHOLDOUT_CHECKPOINT.md`

Current strategy-research handoff:

`docs/handoffs/BOOTSTRAP_PACKAGE_2026-09-11_K_TRADER_V2_2_LEVEL_CONTEXT_V2_HANDOFF.md`

Current parallel research plan:

`docs/research/LEVEL_CONTEXT_V2_MFE_MAE_RESEARCH_PLAN.md`

## Current phase boundary

- Phase 10: COMPLETE / read-only product accepted;
- Phase 11A-11F: VERIFIED;
- Phase 11G production capture / prospective-control tooling: ACTIVE and accepted;
- production provider: `binance_usdm`;
- FAST/M5 production lifecycle remains governed by the canonical deployed rules;
- INTRADAY/M15 strategy redesign remains RESEARCH ONLY;
- independent strategy benchmark/research branch: ACTIVE;
- frozen INTRADAY research candidate: `candidate_rule_set_v2_2`;
- v2.2 promotion: FAILED PREHOLDOUT GATE;
- v2.2 holdout: UNTOUCHED / NOT AUTHORIZED;
- prospective v2.2 shadow observation: ACTIVE under frozen rules;
- Level Context Layer v2 + MFE/MAE diagnostics: APPROVED NEXT RESEARCH;
- Phase 12 multi-provider expansion: not activated by this strategy work.

## Repository identities

Canonical main at the beginning of this strategy-research checkpoint:

`f3ddbfddb37847f63234960855afa287ec9eb9ce`

Research branch:

`research-strategy-benchmark-v1`

Frozen executable v2.2 harness commit:

`9abb05d88912293cee3c254dd427a7127ce5bcc7`

Prospective shadow protocol commit:

`0aba55432dc084181651b5f254c25800f309a754`

The research branch is intentionally separate from production activation. Research commits do not imply deployment.

## Production identity — verified 2026-09-11

Direct host audit confirms:

- deployed SHA: `81b79b281a4cc330b7c11058d202e0d74fb6d70e`;
- image: `k-trader:81b79b281a4cc330b7c11058d202e0d74fb6d70e`;
- container: healthy;
- `/health`: `status=ok`;
- mode: `read_only`;
- `data_ready=true`;
- `scanner_status=DEGRADED`;
- provider: `binance_usdm`;
- Action authentication enabled.

`DEGRADED` does not by itself mean the whole runtime is unusable; current health remains OK and data-ready. Young/insufficient-history contracts continue to fail closed rather than being substituted to manufacture eligibility.

No production deployment, risk, execution or trading-semantics change was made by the independent strategy-research work below.

## Production research/control policy

Production and the existing Phase 11G canonical analyzer remain distinct from the independent candidate-strategy benchmark.

Production safeguards remain:
- read-only application behavior;
- provider-recorded data;
- causal/as-of replay requirements;
- no fabricated historical context;
- no synthetic outcomes;
- no probability calibration without evidence;
- explicit fail-closed handling of insufficient history/data errors;
- canonical deployment through GitHub PR/CI/deploy, not direct host code mutation.

The independent strategy research must not silently redefine current production behavior.

## Independent strategy benchmark — current result

The benchmark programme compared multiple simple trend, breakout, momentum and mean-reversion families under realistic costs.

Benchmark v1 found no strategy meeting the full promotion gate.

Subsequent combined-rule development produced:
- v2: failed preholdout economics;
- v2.1: improved quality gating but validation remained weak;
- v2.2: current strongest frozen research candidate, adding structural-space filtering.

### Frozen v2.2 construction

Current INTRADAY research path:

`H1 directional context -> M15 pullback -> M15 reclaim/continuation -> structural SL -> H1 structural-space gate -> 3R target`

Inherited v2.1 quality gates:
- `abs(EMA20_H1 - EMA50_H1) / ATR14_H1 >= 0.20`;
- M15 signal candle body/range <= `0.60`;
- executed structural risk distance >= `1.25%` of entry.

v2.2 structural-space layer:
- causal H1 swing radius `2`;
- level clustering tolerance `0.20 * ATR14_H1`;
- confirmed cluster requires >=2 pivots;
- entry requires no confirmed obstacle ahead or nearest confirmed obstacle >=`3R`.

Frozen max hold for this exact INTRADAY candidate:

`32 x M15 = 8h`

This is not a universal max-hold rule for other profiles.

## v2.2 reproducibility

Executable harness:

`research/strategy_benchmark_v1/candidate_v2_2_backtest.py`

Harness SHA256:

`b8471af989090375dec9e25daae184814674a776ab9b46b45e660e35b368be08`

Preholdout report:

`/data/research/phase11g/strategy_benchmark_v1/combined_rules/v2_2_preholdout_report.json`

Report SHA256:

`577debe6e6a8a4f1954ffd5b27e872ce971d2de2074783a0abe2e69e79747f8a`

Machine-readable candidate:

`/data/research/phase11g/strategy_benchmark_v1/combined_rules/candidate_rule_set_v2_2.json`

Candidate SHA256:

`85e96f699e54d08a4795d50034fc40b2f69aea535ecf4b22b56ddfbb9417179b`

## v2.2 preholdout metrics

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

Therefore:
- `production_approved=false`;
- `holdout_authorized=false`;
- holdout remains untouched.

Positive expectancy/PF is encouraging but does not override the preregistered sample/WR gates.

## v2.2 diagnostic state

Non-holdout exit composition:
- STOP: 18;
- TARGET: 8;
- TIME_EXIT: 11.

TIME_EXIT:
- 9/11 positive;
- average approximately +0.55R.

Current evidence does not justify changing the frozen 8h INTRADAY time exit merely to improve historical performance.

Direction concentration:
- LONG: 34;
- SHORT: 3.

This is a diagnostic concentration warning only; it is not evidence to disable SHORT or promote LONG-only logic.

Structural context:
- 35/37 non-holdout v2.2 trades were classified `open_space` by `h1_pivot_cluster_v1`.

Interpretation: the current detector is too sparse to represent the complete structural environment. This motivates **Level Context Layer v2** as a new feature-research track, not an in-place v2.2 change.

## Prospective v2.2 boundary

First fully prospective M15 signal-bar boundary after the executable freeze:

`2026-09-11T20:00:00Z`

All prospective observations must preserve the exact frozen v2.2 rules.

Later research ideas must not be projected backwards as if they existed at this boundary.

## Knowledge governance

Legacy strategy Knowledge files are intentionally retained as:

`HISTORICAL / RESEARCH REFERENCE`

Files:
- `01_levels_rules.pdf`;
- `02_ATR_and_range.pdf`;
- `03_money_management.pdf`;
- `04_position_sizing.pdf`;
- `K_Trader_KB_VSA_ATR_SysInstrAddition1.md`.

They may generate hypotheses/features but do not automatically override canonical or current research evidence.

Do not automatically import as hard gates:
- historical ATR-used 60/80% thresholds;
- fixed stop percentages/pips/cents;
- old risk percentages;
- mandatory VSA/volume conditions;
- old timeframe/holding assumptions.

Useful retained concepts:
- fixed vs floating/forming levels;
- trend-break / first-pullback levels;
- mirror levels;
- repeated-touch/limit levels;
- consolidation boundaries;
- false breaks;
- rejection tails;
- structural invalidation stops;
- technical room to target.

## Horizon/profile research architecture

Provisional research envelopes:

| Profile | Context | Trigger | Research horizon |
|---|---|---|---|
| FAST | H1/M15 | M5 | up to ~4h |
| INTRADAY | H4/H1 | M15 | ~8-12h envelope; frozen v2.2 uses 8h |
| SWING | D1/H4 | H1 | ~2-4 days |
| POSITION | W1/D1 | H4 | ~7-21 days |

These are research envelopes, not universal production limits.

TTL before entry and max-hold after entry are separate parameters.

## Evidence governance

Primary evidence unit = unique resolved setup family.

- <30 families: observation only;
- 30-49: diagnostics only;
- 50-99: hypotheses/ablation proposals, no automatic promotion;
- >=100 diverse families: versioned recalibration proposal may be considered.

Every strategy rule change requires:
- a new strategy version;
- preregistration;
- causal full-path backtest/walk-forward;
- fresh OOS/prospective evidence;
- holdout only after a predefined gate;
- explicit promotion decision.

Validation/holdout must not be repeatedly mined to tune the same version.

## Next approved work — parallel tracks

### A. Level Context Layer v2

Develop deterministic causal feature extraction for:
- trend-break/first-pullback levels;
- mirror levels;
- repeated-touch/limit levels;
- consolidation boundaries;
- false breaks;
- rejection tails;
- level age/strength/role changes;
- floating/forming-zone score;
- nearest obstacle distance in ATR/R.

This starts as a feature layer only and must not change frozen v2.2 eligibility.

### B. MFE/MAE diagnostics

For frozen v2.2 completed trades compute:
- MFE_R;
- MAE_R;
- time-to-MFE/MAE;
- time-to-0.5R/1R/2R/3R;
- positive excursion before STOP;
- adverse excursion before TARGET;
- TIME_EXIT path state;
- costs in R;
- cuts by exit reason, side, symbol, structural context and duration.

Actual in-trade path metrics must be separated from any post-exit counterfactual study.

Detailed plan:

`docs/research/LEVEL_CONTEXT_V2_MFE_MAE_RESEARCH_PLAN.md`

## Performance objective

For nominal `RR=1:3`:
- OOS WR target >=50%;
- expectancy_R >0 after all costs;
- PF_R >1 mandatory, target >=1.5;
- stress-slippage survival;
- adequate diverse unique-family sample;
- no single-symbol/single-regime domination;
- acceptable drawdown.

v2.2 has not yet met this complete target.

## Immediate next action

Implement and test **Level Context Layer v2** and **MFE/MAE diagnostics** in parallel while:
- v2.2 remains frozen;
- holdout remains closed;
- production remains unchanged.