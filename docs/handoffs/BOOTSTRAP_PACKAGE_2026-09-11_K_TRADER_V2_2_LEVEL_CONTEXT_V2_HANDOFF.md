# BOOTSTRAP PACKAGE — K-Trader v2.2 -> Level Context Layer v2 + MFE/MAE

Date: 2026-09-11
Repository: `kolemasakar/K-Trader`
Branch: `research-strategy-benchmark-v1`
Purpose: exact continuation point after v2.2 preholdout evaluation and before Level Context Layer v2 + MFE/MAE diagnostics.

## 1. Production boundary

Production remains read-only and unchanged by this research.

Accepted production application/image SHA:

`81b79b281a4cc330b7c11058d202e0d74fb6d70e`

Do not change deployment, execution, Risk Manager or trading semantics as part of this research stage.

## 2. Canonical/main boundary

Canonical main at the strategy-research checkpoint base:

`f3ddbfddb37847f63234960855afa287ec9eb9ce`

Research branch diverges only for research/docs work and was 14 commits ahead / 0 behind before the current documentation-sync commits.

## 3. Frozen candidate v2.2

Frozen executable strategy:

`candidate_rule_set_v2_2`

Harness:

`research/strategy_benchmark_v1/candidate_v2_2_backtest.py`

Harness commit:

`9abb05d88912293cee3c254dd427a7127ce5bcc7`

Runtime harness SHA256:

`b8471af989090375dec9e25daae184814674a776ab9b46b45e660e35b368be08`

Prospective protocol commit:

`0aba55432dc084181651b5f254c25800f309a754`

v2.2 is frozen. Do not tune it in place.

## 4. Preholdout result

Report:

`/data/research/phase11g/strategy_benchmark_v1/combined_rules/v2_2_preholdout_report.json`

SHA256:

`577debe6e6a8a4f1954ffd5b27e872ce971d2de2074783a0abe2e69e79747f8a`

Candidate artifact:

`/data/research/phase11g/strategy_benchmark_v1/combined_rules/candidate_rule_set_v2_2.json`

SHA256:

`85e96f699e54d08a4795d50034fc40b2f69aea535ecf4b22b56ddfbb9417179b`

Results:
- Development: n=23, WR 47.83%, expectancy +0.1003R, PF_R 1.1818;
- Validation: n=10, WR 30.00%, expectancy +0.2507R, PF_R 1.3941;
- Non-holdout: n=37, WR 45.95%, expectancy +0.2888R, PF_R 1.5592;
- Stress non-holdout: n=37, WR 43.24%, expectancy +0.2741R, PF_R 1.5235.

Promotion gate failed because:
- non-holdout n <100;
- validation n <30;
- non-holdout WR <50%;
- validation WR <50%.

Holdout remains untouched and unauthorized.

## 5. Diagnostics already known

Non-holdout exits:
- STOP 18;
- TARGET 8;
- TIME_EXIT 11.

9/11 TIME_EXIT trades were positive; average TIME_EXIT about +0.55R.

Direction concentration:
- LONG 34;
- SHORT 3.

Structural detector:
- 35/37 non-holdout trades = `open_space`.

This is the main reason to research Level Context Layer v2.

## 6. Prospective boundary

First fully prospective M15 signal-bar boundary after the frozen executable v2.2 commit:

`2026-09-11T20:00:00Z`

Prospective evidence must be accumulated under unchanged frozen v2.2 rules.

Do not reinterpret later rule changes as if they had existed at this boundary.

## 7. Knowledge governance

Legacy Knowledge files were audited and must remain historical references:
- `01_levels_rules.pdf`;
- `02_ATR_and_range.pdf`;
- `03_money_management.pdf`;
- `04_position_sizing.pdf`;
- `K_Trader_KB_VSA_ATR_SysInstrAddition1.md`.

Do not automatically import their old thresholds as canonical rules.

Useful hypotheses include:
- fixed vs floating levels;
- trend-break/first-pullback levels;
- mirror levels;
- repeated-touch/limit levels;
- consolidation boundaries;
- false breaks;
- rejection tails;
- structural stop placement;
- technical room to target.

## 8. Current research task

Proceed with two parallel tracks.

### Track A — Level Context Layer v2

Build richer deterministic causal structural features for:
- trend-break levels;
- mirror levels;
- repeated-touch/limit levels;
- consolidation boundaries;
- false-break behavior;
- rejection-tail behavior;
- level age/strength;
- floating/forming zones;
- next-obstacle distance in ATR/R.

This layer starts as features only. Do not use it to modify v2.2 eligibility.

### Track B — MFE/MAE diagnostics

For frozen v2.2 completed trades calculate:
- MFE_R / MAE_R;
- time-to-MFE / time-to-MAE;
- time-to-0.5R/1R/2R/3R;
- favorable excursion before stop;
- adverse excursion before target;
- TIME_EXIT path state;
- costs in R;
- diagnostic cuts by exit reason, side, symbol, structural context and duration.

Actual-path metrics and post-exit counterfactuals must be kept separate.

## 9. Research plan document

Read first:

`docs/research/LEVEL_CONTEXT_V2_MFE_MAE_RESEARCH_PLAN.md`

Also read:

`docs/checkpoints/2026-09-11_STRATEGY_V2_2_PREHOLDOUT_CHECKPOINT.md`

and updated:

`docs/research/CANDIDATE_RULE_SET_V2_2_RESEARCH_SPEC.md`

## 10. Methodological constraints

- closed bars only;
- no look-ahead;
- MTF alignment causal at decision time;
- full executable path for strategy evaluation;
- primary evidence unit = unique resolved setup family;
- validation is not fresh OOS after inspection;
- holdout remains closed;
- no production changes;
- no automatic rule promotion;
- any strategy change becomes a new preregistered version.

## 11. Evidence gates

- <30 resolved unique families: observation only;
- 30-49: diagnostics only;
- 50-99: ablation/component proposals, no production promotion;
- >=100 diverse families: versioned recalibration proposal may be considered.

## 12. User performance objective

For nominal RR 1:3:
- OOS WR target >=50%;
- expectancy_R >0 after all costs;
- PF_R >1 mandatory, target >=1.5;
- stress survival;
- diversified symbols/regimes;
- acceptable drawdown.

Do not represent v2.2 as having met this objective.

## 13. Immediate next action

Implement Track A Level Context Layer v2 feature extractor and Track B MFE/MAE diagnostic extractor in parallel, test causality/reproducibility, then run diagnostics without changing frozen v2.2.