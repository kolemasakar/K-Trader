# K-Trader — Post-30 Prospective Diagnostic Baseline

Date: 2026-09-16  
Status: **ACCEPTED DIAGNOSTIC BASELINE / NO RETUNING / HOLDOUT UNTOUCHED**

## Governance boundary

Source prospective outcome state at `2026-09-16T09:45:00Z`:

- unique primary families `43`;
- resolved primary families `39`;
- unresolved primary families `4`;
- evidence tier `DIAGNOSTIC_30_49_RESOLVED_FAMILIES`;
- frozen candidate `candidate_rule_set_v2_2` unchanged;
- holdout opened `false`;
- production action `false`.

This checkpoint is descriptive only. None of the subgroup results below authorizes an in-place filter, threshold change, direction change, RR/max-hold change, symbol exclusion, holdout access or production mutation.

## Reproducible diagnostic artifacts

Prospective diagnostic runner:

`research/strategy_benchmark_v1/prospective_v2_2_post30_diagnostics.py`

Initial runner commit:

`7c1dd999ea23ed31c1280ab5a7cc30aec1d4bb65`

Statistical diagnostic runner:

`research/strategy_benchmark_v1/prospective_post30_statistical_diagnostics.py`

Initial runner commit:

`810fdb958f719a94c62c4bc15dab14e1b8a1b726`

Artifact directory:

`/data/research/phase11g/strategy_benchmark_v1/combined_rules/prospective_post30_diagnostics/20260916T094500Z`

Hashes:

- descriptive report `8a09a4e2130ce53925621373f774b2dc4ba7a655bcf64c8694fbf5b2e8d2b226`;
- canonical statistical report `9dfd9d01c874e61f38732dec4b0349df397e3fc163c1a90ae0b020a9a5004373`.

The statistical report uses deterministic `200,000`-iteration two-sided permutation tests, `100,000` bootstrap resamples for mean-difference intervals, Fisher exact tests for win-rate contrasts, and Benjamini-Hochberg adjustment across the listed exploratory contrasts.

## Overall prospective state

Resolved primary families `39`:

- wins `9`;
- losses `30`;
- win rate `23.076923%`;
- expectancy `-0.6482720083734612R`;
- median `-1.0246807651677718R`;
- R-based profit factor `0.15009942512951674`.

## Direction diagnostic

LONG:

- `13` resolved;
- wins/losses `3 / 10`;
- win rate `23.076923%`;
- expectancy `-0.585215R`.

SHORT:

- `26` resolved plus `4` currently unresolved;
- wins/losses among resolved `6 / 20`;
- win rate `23.076923%`;
- expectancy `-0.679800R`.

Exploratory contrast SHORT minus LONG:

- expectancy difference `-0.094585R`;
- bootstrap 95% interval `[-0.656248R, +0.376365R]`;
- permutation `p=0.71679`;
- BH-adjusted `q=0.71679`;
- Fisher win-rate `p=1.0`.

Interpretation: the current prospective sample does **not** support a directional LONG-only/SHORT-exclusion conclusion.

## Level Context diagnostics

### Rich obstacle inside 3R

Obstacle `<3R = true`:

- `18` resolved;
- wins `2`;
- expectancy `-0.874479R`.

Obstacle `<3R = false`:

- `21` resolved;
- wins `7`;
- expectancy `-0.454380R`.

Exploratory difference true minus false:

- `-0.420099R`;
- bootstrap 95% interval `[-0.850803R, -0.009225R]`;
- raw permutation `p=0.06868`;
- BH-adjusted `q=0.22956`;
- Fisher win-rate raw `p=0.13873`, adjusted `q=0.41618`.

### Rich obstacle inside 1R

Obstacle `<1R = true`:

- `14` resolved;
- wins `1`;
- expectancy `-0.923283R`.

Obstacle `<1R = false`:

- `25` resolved;
- wins `8`;
- expectancy `-0.494266R`.

Exploratory difference true minus false:

- `-0.429018R`;
- bootstrap 95% interval `[-0.826609R, -0.042069R]`;
- raw permutation `p=0.07652`;
- BH-adjusted `q=0.22956`;
- Fisher win-rate raw `p=0.11891`, adjusted `q=0.41618`.

Interpretation: obstacle distance is the strongest current **hypothesis-generating** diagnostic, but neither contrast survives the exploratory multiple-comparison adjustment. It must not be converted into a frozen-v2.2 eligibility filter at this tier.

Other Level Context contrasts are weaker in the current sample:

- clean-break true vs false: permutation `p=0.26918`, adjusted `q=0.53836`;
- floating-zone true vs false: permutation `p=0.64793`, adjusted `q=0.71679`;
- frozen-vs-rich open-space disagreement exists in `12` of `43` families, but no rule change is authorized.

The `consolidation_present=false` subgroup contains only one resolved family and is not inferentially useful.

## Raw VSA diagnostic

Within current bundle coverage:

- `7` primary families have a raw VSA event on the signal bar;
- those `7` classify as `OPPOSING` to trade direction;
- `32` classify as `NONE`;
- `4` older signal bars are unavailable in the current rolling bundle and are explicitly marked unavailable rather than imputed.

OPPOSING vs NONE among resolved/source-available observations:

- expectancy `-0.791671R` vs `-0.603962R`;
- permutation `p=0.62275`;
- BH-adjusted `q=0.71679`;
- Fisher win-rate `p=1.0`.

Interpretation: the sample does not currently support a VSA-based eligibility change.

## Execution economics diagnostic

Across the `39` resolved primary families:

- mean fee burden `0.034430R`;
- median fee burden `0.034254R`;
- mean signed funding cost `0.018887R`;
- median signed funding cost `0R`;
- mean fee + funding burden `0.053316R`;
- mean measured exit-slippage drag `0.013811R`;
- median measured exit-slippage drag `0.013528R`.

The slippage value is retained as execution-path sensitivity and is not treated as a simple interchangeable algebraic fee term.

## Outcome decomposition

Resolved terminal states:

- `26 STOP` — all losses, expectancy `-1.066884R`;
- `13 TIME_EXIT` — `9` wins / `4` losses, expectancy `+0.188953R`.

This is an **ex-post outcome decomposition**, not a pre-entry predictor. Terminal state must not be used as if it were an available entry-time filter.

## Portfolio/concentration diagnostic

Across all `43` prospective families:

- symbol HHI `0.102217`;
- largest single-symbol family share `16.2791%`;
- maximum concurrent families `6`;
- maximum concurrent LONG `4`;
- maximum concurrent SHORT `6`.

At absolute 15m-return correlation threshold `0.70`, the current captured-window cluster contains:

`ADAUSDT, DOGEUSDT, ENAUSDT, SUIUSDT, TRUMPUSDT, WLDUSDT, XRPUSDT`.

Same-side / within-60-minute / correlated grouping is diagnostic only:

- diagnostic cohorts `36`;
- multi-family correlated cohorts `4`;
- largest correlated cohort size `4`;
- correlation graph edges `11`.

Interpretation: single-symbol concentration is not dominant, but concurrent correlated exposure exists and remains relevant for future portfolio/risk research. No production risk rule is changed by this observation.

## Accepted conclusions at the 30–49 tier

1. No current prospective evidence supports a LONG-only or SHORT-exclusion modification.
2. Rich obstacle distance (`<1R` / `<3R`) is the clearest hypothesis-generating feature, but does not survive the current exploratory multiplicity adjustment.
3. Raw signal-bar VSA does not currently show a reliable prospective separation.
4. Explicit fees/funding and execution drag are material enough to remain mandatory in every future evaluation.
5. Correlated simultaneous exposure is observable and should remain a portfolio diagnostic dimension.
6. Frozen v2.2 remains unchanged; holdout remains closed.

## Next evidence boundary

Continue prospective collection/resolution without retuning.

The next governance boundary is:

`>=50 unique resolved prospective frozen-v2.2 setup families`

At `50–99`, hypotheses/ablation proposals may be formalized, but still may not be promoted without fresh out-of-sample/prospective evidence and explicit authorization.
