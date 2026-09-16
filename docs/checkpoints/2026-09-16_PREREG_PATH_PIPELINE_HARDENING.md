# 2026-09-16 — Preregistration, Path Quality and Pipeline Hardening

Status: **ACCEPTED DIAGNOSTIC / HARDENING CHECKPOINT**

This checkpoint records work performed in Phase 11G without changing frozen `candidate_rule_set_v2_2`, opening holdout data, or mutating production behavior.

## Accepted prospective state used

Diagnostic source cutoff: `2026-09-16T12:00:00Z`.

- eligible observations: `56`;
- unique primary families: `43`;
- resolved primary families: `39`;
- unresolved primary families: `4`;
- wins/losses: `9/30`;
- expectancy: `-0.6482720085510278R`;
- evidence tier: `DIAGNOSTIC_30_49_RESOLVED_FAMILIES`.

The four currently open primary families remain governed by the frozen 32-M15 causal max hold. No outcome was forced during this work.

## Prospective hypothesis preregistration

Canonical document:

`docs/research/PROSPECTIVE_HYPOTHESES_PREREG_2026-09-16.md`

Confirmation boundary:

`entry_time >= 2026-09-16T13:00:00Z`

Anything earlier is discovery/context only, including the four families that were already open before this boundary.

Primary preregistered hypothesis H1 freezes:

`SHORT && h1_ema_sep_atr < 0.9033277894201235`

as the LOW-trend subgroup. The threshold may not be re-estimated from future outcomes.

H1 requires a future confirmation sample with at least `20` resolved future primary SHORT families in LOW and `20` in REST, plus fixed effect, bootstrap, permutation, concentration, and leave-one-symbol-out criteria. Meeting the preregistered criteria would still authorize only a future versioned proposal, never an in-place v2.2 change.

Secondary preregistered hypotheses cover rich obstacle inside 1R, rich obstacle inside 3R, and same-side 60-minute portfolio concentration.

## Path / MFE / MAE quality diagnostics

Runtime report:

`/data/research/phase11g/strategy_benchmark_v1/combined_rules/prospective_path_quality/20260916T120000Z/report.json`

SHA256:

`4cf1085bbcd35bb381f1f2981136f6f66f97c734b5efa10fedf9a8a9d7e41030`

Reproducible implementation:

`research/strategy_benchmark_v1/prospective_path_quality_diagnostics.py`

Key findings on 39 resolved primary families:

- mean MFE: `0.8013R`;
- mean MAE: `1.0491R`;
- median realized R: `-1.0247R`;
- median hold: `20` M15 bars.

STOP outcomes:

- `26` families;
- expectancy `-1.0669R`;
- mean MFE `0.7015R`;
- mean MAE `1.3103R`;
- `17/26` reached at least `+0.5R`;
- `7/26` reached at least `+1R` and nevertheless finished non-positive;
- none reached `+2R` before STOP in this sample.

TIME_EXIT outcomes:

- `13` families;
- expectancy `+0.1890R`;
- wins `9/13`;
- mean MFE `1.0010R`;
- mean MAE `0.5265R`;
- median hold `33` bars under existing resolver counting semantics.

TIME_EXIT by achieved MFE:

- `<0.5R`: n=3, expectancy `-0.5869R`;
- `0.5–1R`: n=5, expectancy `+0.1439R`;
- `1–2R`: n=3, expectancy `+0.4769R`;
- `2–3R`: n=2, expectancy `+1.0336R`.

These observations generate future exit-management hypotheses only. They do not authorize moving stop, adding break-even behavior, partial exits, trailing stops, or changing the 32-M15 max hold in frozen v2.2.

## Execution-cost decomposition

- post-cost expectancy: `-0.6483R`;
- estimated mean pre-cost expectancy: `-0.5811R`;
- mean total execution drag: about `0.0671R` per resolved family;
- only `1` resolved family was pre-cost positive but post-cost non-positive.

Therefore execution costs are material but do not explain the current negative prospective expectancy by themselves.

## Symbol and temporal concentration

Leave-one-symbol-out overall expectancy remained negative after every single-symbol exclusion, approximately between `-0.576R` and `-0.740R`. The weak prospective result is therefore not explained by one symbol alone.

Temporal behavior is much less stable:

- 2026-09-12: `-1.005R`;
- 2026-09-13: `-1.133R`;
- 2026-09-14: `-0.798R`;
- 2026-09-15: `-0.146R`;
- 2026-09-16 currently has only one resolved pre-existing family and is not interpretable alone.

This supports retaining regime/time confounding as a central research explanation.

## Fail-closed research orchestration

New runner:

`research/strategy_benchmark_v1/run_prospective_research_pipeline_v1.py`

Behavior:

- plan-only by default;
- explicit `--execute` required to run stages;
- stages: capture -> funding snapshot -> resolver v1.2 -> post-30 diagnostics -> statistical diagnostics;
- each stage records status and command in a hashed manifest;
- any non-zero stage terminates later stages;
- existing run-root is rejected in execute mode;
- missing scripts and missing prior outcomes fail closed;
- no holdout access or production action is part of the runner.

Plan-mode validation for future `13:00Z` produced:

`PLAN_ONLY`, five `PLANNED` stages, no research stage execution.

Plan manifest SHA256:

`f684f38bf8793c1cbc0cfc0f0a01fc58ca07466b31a94ec83d05db62faafba73`

Synthetic failure-path validation intentionally failed the funding stage with return code `7`:

- capture: PASS;
- funding: FAILED;
- resolver and all later stages: not executed;
- wrapper return code: `1`;
- `LATER_STAGES_BLOCKED=PASS`.

Failure manifest SHA256:

`e2c1ecb3f2fb92fcbf9e1f67317d4d16282b474f3eaff633f3196bf203eba51b`

Regression tests:

`research/strategy_benchmark_v1/tests/test_prospective_research_pipeline_v1.py`

Result: `4/4 PASS`.

Covered behaviors:

- deterministic UTC stamping;
- plan mode does not invoke subprocess;
- failed stage records FAILED and raises;
- successful stage records PASS.

## Governance conclusion

No frozen-v2.2 parameter changed.

No SHORT/LONG filter changed.

No exit-management rule changed.

No risk gate changed.

Holdout remains closed.

Production remains untouched.

The new LOW-trend SHORT signal is now preregistered for genuinely future confirmation rather than further post-hoc reuse of the discovery sample.

Phase 11G remains **ACTIVE**. Phase 12 remains **FUTURE / NOT ACTIVE**.
