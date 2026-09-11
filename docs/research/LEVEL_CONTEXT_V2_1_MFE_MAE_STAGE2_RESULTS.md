# Level Context v2.1 + MFE/MAE Stage 2 — Results

Date: 2026-09-11
Status: DIAGNOSTIC COMPLETE / NO STRATEGY CHANGE / HOLDOUT UNTOUCHED

## Boundary

The frozen `candidate_rule_set_v2_2` was not modified. No production trading semantics, risk, SL, TP, RR, max-hold or deployment settings changed. The locked holdout was not opened.

Execution used the already approved SentinelX privileged boundary: exact `sudo /usr/bin/docker exec` into `k-trader-ktrader-1`. No filesystem permission or SentinelX policy broadening was performed.

## Artifacts

- Level Context v2.1 report:
  `/data/research/phase11g/strategy_benchmark_v1/combined_rules/level_context_v2_1_diag/report.json`
- SHA256: `ffb066036b45a3f433535db2249f7ed460d8405d298a5f8dbf9b81a9ef5cab60`

- MFE/MAE Stage 2 report:
  `/data/research/phase11g/strategy_benchmark_v1/combined_rules/mfe_mae_v2_2_stage2/report.json`
- SHA256: `36f09c7bb8b99198729eddbb9f1ffb45c889897a925f687921135f72977a5bb3`

## 1. Level Context v2.1

### Strict break definition still does not discriminate

Requiring a causal close-through of a level that already had at least two same-side confirmed pivots was still present in every frozen v2.2 trade:

- development: `23/23`;
- validation: `10/10`;
- non-holdout: `37/37`.

Therefore `strict_break_present` is not useful as a binary eligibility feature for this candidate family. Do not promote it.

A recency band (`<=8 H1 bars`) did discriminate numerically but remains a diagnostic only:

- development: n=4, WR 75.0%, expectancy +0.071R;
- validation: n=8, WR 37.5%, expectancy +0.570R;
- non-holdout: n=13, WR 53.85%, expectancy +0.373R.

The samples are too small and the WR behavior is not stable enough for promotion.

### H1 open-space remains the strongest structural hypothesis

Development:

- H1 open-space: n=13, WR 69.23%, expectancy `+0.759R`, PF_R `3.329`;
- obstacle ahead: n=10, WR 20.0%, expectancy `-0.756R`, PF_R `0.106`.

Non-holdout:

- H1 open-space: n=22, WR 59.09%, expectancy `+0.796R`, PF_R `3.072`;
- obstacle ahead: n=15, WR 26.67%, expectancy `-0.456R`, PF_R `0.358`.

Validation remains unresolved because the sample is tiny and does not reproduce the split:

- open-space: n=7, expectancy `+0.248R`;
- obstacle ahead: n=3, expectancy `+0.257R`.

Conclusion: keep H1 open-space / obstacle geometry as a high-priority feature, not a hard gate.

### Obstacle evidence count

Development obstacles with evidence count 3-4 were negative. Non-holdout count 4 was also strongly negative (`n=9`, expectancy `-0.638R`). Validation is too sparse and does not provide an independent confirmation.

The evidence count must remain diagnostic; no threshold is authorized.

### Break revisit / mirror-retest observation

The dynamic broken-level revisit feature showed a directionally consistent association:

- development, no revisit: n=10, WR 70.0%, expectancy `+0.558R`, PF_R `2.731`;
- development, revisit: n=13, WR 30.77%, expectancy `-0.252R`;
- validation, no revisit: n=3, WR 66.67%, expectancy `+1.952R`;
- validation, revisit: n=7, WR 14.29%, expectancy `-0.478R`;
- non-holdout, no revisit: n=14, WR 71.43%, expectancy `+0.817R`, PF_R `4.504`;
- non-holdout, revisit: n=23, WR 30.43%, expectancy `-0.033R`.

A post-hoc mechanism check did NOT show that the effect is simply caused by a subsequent level invalidation. Among non-holdout revisit cases:

- invalidated after break: n=12, expectancy `+0.423R`;
- not invalidated after break: n=11, expectancy `-0.530R`.

Therefore this feature should not be interpreted as a simple failed-mirror rule. It may be a proxy for lifecycle maturity, repeated traversal/chop, or late continuation entry. Rename the research concept mentally as `broken_level_revisit` until its mechanism is resolved.

No gate is promoted from this post-hoc result.

## 2. MFE/MAE Stage 2

### STOP paths strongly favor an entry/context diagnosis

Non-holdout STOPs: `18`.

- `IMMEDIATE_FAILURE_LT_0_5R`: `13/18` = 72.22%; median MFE `0.155R`;
- `PARTIAL_FAVORABLE_0_5_TO_1R`: `2/18` = 11.11%; median MFE `0.772R`;
- `FAVORABLE_THEN_REVERSAL_GE_1R`: `3/18` = 16.67%; median MFE `1.170R`.

Thus almost three quarters of stopped trades never achieved even +0.5R before failing. The main improvement opportunity remains setup/context selection, not merely wider stops or a different profit target.

### Successful 3R trades progress early

For the eight non-holdout TARGET trades:

- median time to +0.5R: `0` M15 bars;
- median time to +1R: `1.5` bars;
- median time to +2R: `7` bars;
- median time to +3R: `13.5` bars (~3h22m);
- median MAE before target: `0.227R`.

This is a strong descriptive signature: the best trades tend to move favorably early and reach 3R well inside the current 8h maximum hold.

It does not yet authorize an early-progress exit rule.

### TIME_EXIT trades lose material open profit

Non-holdout TIME_EXIT: `11`, of which `9` finish positive.

- median MFE: about `1.55R` from Stage 1;
- median giveback: `0.719R`;
- median capture ratio: `0.262` of MFE.

Stage-2 terminal-state split:

- EXPANDING: n=3, mean realized `+0.856R`, median giveback `0.563R`;
- STALLING: n=6, mean realized `+0.493R`, median giveback `0.667R`;
- RETRACING: n=2, mean realized `+0.262R`, median MFE `2.203R`, median giveback `1.926R`.

The RETRACING subgroup is small but economically interesting: it reached substantial favorable excursion and surrendered most of it before the fixed time exit.

This motivates a separately preregistered future trade-management study; it does not change the frozen v2.2 exit behavior.

### Threshold reach rates, non-holdout

Across all 37 trades:

- reached +0.5R: `22/37` = 59.46%; median time 1 bar;
- reached +1R: `19/37` = 51.35%; median time 3 bars;
- reached +2R: `11/37` = 29.73%; median time 13 bars;
- reached +3R: `8/37` = 21.62%; median time 13.5 bars.

For TIME_EXIT trades only:

- +0.5R: 9/11;
- +1R: 8/11;
- +2R: 3/11;
- +3R: 0/11.

## 3. Research interpretation

Current evidence separates two research problems:

1. **Entry/context quality** — dominant loss source. Immediate failures are common, and H1 structural obstruction / repeated broken-level revisit are high-priority explanatory features.
2. **Profit retention** — secondary but material. TIME_EXIT trades are often profitable but surrender meaningful MFE before exit.

Do not mix these into one optimized rule set yet.

## 4. Next research tasks

### Level Context v2.2 measurement layer

Without changing the candidate:

- replace binary `mirror/retest` naming with explicit broken-level revisit lifecycle features;
- record revisit count, most-recent revisit age, time from break to first revisit, number of crossings of the level zone, hold-side ratio after each revisit, and distance from current entry to the broken level in R;
- distinguish clean breakout continuation from repeated level traversal/congestion;
- keep H1 obstacle strength components separately rather than promoting a composite threshold.

### MFE/MAE Stage 3

Build a diagnostic-only post-entry state model:

- early progress timing without changing execution;
- MFE giveback curve over time;
- distinguish `never-progressed` from `progressed-then-reversed`;
- for TIME_EXIT, quantify when peak MFE occurred and how much was surrendered during the final 4/8/12 M15 bars;
- formulate any later trade-management candidate as a NEW version for fresh prospective validation.

## Promotion status

Unchanged:

- v2.2 remains frozen;
- pre-holdout promotion gate remains FAILED;
- holdout remains unopened;
- production remains unchanged/read-only.
