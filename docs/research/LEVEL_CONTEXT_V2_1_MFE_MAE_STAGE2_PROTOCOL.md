# Level Context v2.1 + MFE/MAE Stage 2 — Diagnostic Protocol

Date: 2026-09-11
Status: PREREGISTERED DIAGNOSTIC / NO STRATEGY CHANGE / HOLDOUT UNTOUCHED

## Boundary

This work does not modify frozen `candidate_rule_set_v2_2`, its promotion gate, production trading semantics, risk, SL, TP, RR, max hold, or the locked holdout.

Only development, validation and combined non-holdout artifacts may be read. Results are diagnostic and may motivate a future separately versioned candidate; they cannot retroactively change v2.2.

## A. Level Context v2.1 diagnostics

The first Level Context v2 detector showed that the old `trend_break_present` definition was too broad (`37/37` non-holdout) and that pivot-type-only mirror classification was too sparse.

### Strict confirmed-level break

A diagnostic break is counted only when all of the following were causal at the decision time:

- H1 pivot candidates use radius 2 and therefore require the confirming future-with-respect-to-pivot bars to already be closed before the trade decision;
- the broken structure has at least two same-side confirmed pivots before the break event;
- LONG requires an actual close crossing from at/below the level zone to above it; SHORT is symmetric;
- the break event and all retest observations occur no later than the trade decision.

Recorded continuous/features:

- `strict_break_present`;
- `strict_break_age_bars`;
- `strict_break_displacement_atr`;
- `strict_prebreak_pivot_count`;
- `strict_held_close_fraction`;
- `strict_invalidated_after_break`;
- `strict_level_distance_R_now`.

`strict_break_fresh` uses `<=8 H1 bars` only as a diagnostic recency band corresponding to the current INTRADAY 8h envelope. It is not a hard gate.

### Dynamic mirror/retest

`strict_mirror_retest_present` means that after a confirmed-level break, a later closed H1 bar revisited the broken level zone and closed on the breakout side before the decision timestamp.

This is intended to detect resistance→support / support→resistance behavior even when the later retest does not itself become an exact opposite-type pivot.

### Obstacle evidence

For an H1 obstacle ahead, a non-promotional evidence count records whether the obstacle has:

- at least two touch episodes;
- at least one false break;
- rejection-tail score `>=0.50`;
- age `<=24 H1 bars`;
- mirror classification.

The count is diagnostic only. No threshold is authorized as an eligibility gate.

## B. MFE/MAE Stage 2 diagnostics

Stage 2 uses only the actual frozen v2.2 execution path and retains the Stage 1 causal rule that the exit-event bar contributes only the known execution event, not unknown intrabar extremes.

### STOP path classes

- `IMMEDIATE_FAILURE_LT_0_5R`: MFE < 0.5R;
- `PARTIAL_FAVORABLE_0_5_TO_1R`: 0.5R <= MFE < 1R;
- `FAVORABLE_THEN_REVERSAL_GE_1R`: MFE >= 1R.

These labels diagnose whether losses are primarily entry/context failures or trade-management reversals. They are not stop-management rules.

### TIME_EXIT state

Using the causal terminal four-bar directional slope:

- `EXPANDING`: slope >= +0.25R;
- `STALLING`: -0.25R < slope < +0.25R;
- `RETRACING`: slope <= -0.25R.

The ±0.25R band is frozen before Stage 2 output is inspected and is diagnostic only.

Additional metrics:

- gross terminal R = realized R + explicit fee/funding R;
- giveback R = MFE R - gross terminal R;
- capture ratio = gross terminal R / MFE R when MFE > 0;
- reach fractions and median time-to-0.5R/1R/2R/3R;
- cross-tabs with H1 open-space, obstacle evidence and strict break/retest context.

## Interpretation policy

- Development patterns may generate hypotheses.
- Validation is a check, not a tuning surface.
- Small subgroups remain descriptive regardless of apparent effect size.
- No result in this diagnostic can authorize the v2.2 holdout.
- Any promoted rule must be a new version with fresh prospective/OOS evidence.

## Implementation

Repository scripts:

- `research/strategy_benchmark_v1/level_context_v2_1_diagnostics.py`
- `research/strategy_benchmark_v1/mfe_mae_stage2_diagnostics.py`

Both scripts passed Python syntax compilation on the research host shell.

## Current execution gate

At protocol freeze time the SentinelX policy lists `/opt/k-trader/data` as read-only, but the host Unix directory mode prevents the `sentinelx` account from traversing the production data tree. No filesystem permissions were changed automatically.

The scripts remain preregistered before output inspection. Once a read-only execution path to the existing research artifacts is restored, run Stage 2 without changing the frozen definitions above.
