# K-Trader Strategy Research — v2.2 Preholdout Checkpoint

Date: 2026-09-11
Branch: `research-strategy-benchmark-v1`
Scope: research only
Production changes: none
Holdout: untouched

## Canonical repository state

Canonical main at checkpoint start:

`f3ddbfddb37847f63234960855afa287ec9eb9ce`

Research branch before documentation sync:

`0aba55432dc084181651b5f254c25800f309a754`

At that point the research branch was 14 commits ahead of main and 0 behind.

Production runtime remains the accepted read-only deployment based on application image/SHA:

`81b79b281a4cc330b7c11058d202e0d74fb6d70e`

No production trading semantics, deployment, risk configuration or execution behavior were changed by the strategy-research work recorded here.

## Frozen candidate

Candidate: `candidate_rule_set_v2_2`

Executable harness:

`research/strategy_benchmark_v1/candidate_v2_2_backtest.py`

Harness commit:

`9abb05d88912293cee3c254dd427a7127ce5bcc7`

Runtime harness SHA256:

`b8471af989090375dec9e25daae184814674a776ab9b46b45e660e35b368be08`

Prospective shadow protocol commit:

`0aba55432dc084181651b5f254c25800f309a754`

## v2.2 strategy construction

Frozen current INTRADAY candidate:

`H1 directional context -> M15 pullback -> reclaim/continuation -> structural stop -> H1 structural-space gate -> 3R target`

Inherited v2.1 quality gates:
- H1 EMA separation / ATR >= 0.20;
- M15 signal body fraction <= 0.60;
- minimum structural stop distance >=1.25% of executed entry.

v2.2 structural-space gate:
- causal H1 pivot detector, radius 2;
- level cluster tolerance 0.20 H1 ATR14;
- confirmed level >=2 clustered pivots;
- next confirmed obstacle must be absent or >=3R from entry.

Frozen INTRADAY max hold remains 32 M15 bars = 8h.

## Preholdout result

Report SHA256:

`577debe6e6a8a4f1954ffd5b27e872ce971d2de2074783a0abe2e69e79747f8a`

Candidate artifact SHA256:

`85e96f699e54d08a4795d50034fc40b2f69aea535ecf4b22b56ddfbb9417179b`

| Segment | Trades | WR | expectancy_R | PF_R |
|---|---:|---:|---:|---:|
| Development | 23 | 47.83% | +0.1003R | 1.1818 |
| Validation | 10 | 30.00% | +0.2507R | 1.3941 |
| Non-holdout | 37 | 45.95% | +0.2888R | 1.5592 |
| Stress non-holdout | 37 | 43.24% | +0.2741R | 1.5235 |

Promotion gate: **FAIL**.

Fail reasons:
- NON_HOLDOUT_SAMPLE_LT_100;
- VALIDATION_SAMPLE_LT_30;
- NON_HOLDOUT_WIN_RATE_LT_50;
- VALIDATION_WIN_RATE_LT_50.

`holdout_authorized=false`.

## Key diagnostics

Non-holdout exits:
- STOP 18;
- TARGET 8;
- TIME_EXIT 11.

TIME_EXIT:
- 9/11 positive;
- average approximately +0.55R.

No current evidence supports extending the frozen 8h v2.2 max-hold merely to improve backtest performance.

Direction concentration:
- LONG 34;
- SHORT 3.

This is recorded as a concentration diagnostic only.

Structural detector:
- 35/37 non-holdout trades classified as `open_space`.

Interpretation: `h1_pivot_cluster_v1` is too sparse to represent the complete level environment. This motivates a richer Level Context Layer v2, but does not authorize retroactive v2.2 modification.

## Methodological safeguard

Simple post-filtering of an already generated v2.1 trade list is not equivalent to a full executable v2.2 path because rejecting an earlier trade may make a later signal executable.

All strategy evaluations must therefore use the complete causal executable path rather than only filtering existing completed trades.

## Knowledge audit state

Uploaded legacy files were audited and retained as `HISTORICAL / RESEARCH REFERENCE`:
- `01_levels_rules.pdf`;
- `02_ATR_and_range.pdf`;
- `03_money_management.pdf`;
- `04_position_sizing.pdf`;
- `K_Trader_KB_VSA_ATR_SysInstrAddition1.md`.

Useful concepts are hypotheses/features only unless revalidated.

Universal legacy hard gates are not imported automatically.

## Prospective boundary

Frozen executable timestamp derives from commit `9abb05d...`.

First fully prospective M15 signal-bar boundary:

`2026-09-11T20:00:00Z`

The prospective v2.2 rules remain frozen while new evidence accumulates.

## Next approved work

Proceed in parallel with:

### A. Level Context Layer v2
Feature-only research on richer deterministic structural context.

### B. MFE/MAE diagnostics
Diagnostic study of excursion and duration behavior using existing frozen trades and causal market history.

Constraints:
- do not modify frozen v2.2;
- do not open holdout;
- do not reuse validation as fresh OOS evidence;
- do not change production;
- any proposed strategy rule resulting from diagnostics becomes a new version.

## Control conclusion

Project strategy-research state is coherent and ready for Level Context Layer v2 + MFE/MAE diagnostics in parallel.

Current strongest frozen candidate remains v2.2, but it is **not production-approved** and has **not passed promotion**.