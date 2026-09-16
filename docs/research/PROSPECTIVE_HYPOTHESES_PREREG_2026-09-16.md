# Prospective Hypotheses Preregistration — 2026-09-16

Status: **PREREGISTERED / FUTURE CONFIRMATION ONLY**

This document freezes several hypotheses discovered during diagnostic-only Phase 11G analysis. It does **not** change frozen candidate `candidate_rule_set_v2_2`, does not authorize retuning, does not open holdout data, and does not authorize production mutation.

## Confirmation boundary

Only primary-family entries with:

`entry_time >= 2026-09-16T13:00:00Z`

may contribute to confirmatory evidence under this preregistration.

All earlier observations — including the four primary families already open before this boundary — are context/discovery data only and must not be counted as confirmation data.

Family semantics remain: earliest eligible entry is the immutable primary representative. Correlated diagnostic observations do not count as independent evidence.

All frozen-v2.2 economics remain unchanged: 3R target, 32 M15 max hold, STOP-first same-bar semantics, 5 bps/side fees, 2 bps/side base slippage, official Binance USD-M funding.

## H1 — SHORT low trend-separation hypothesis

Fixed predictor:

`h1_ema_sep_atr = abs(H1 EMA20 - H1 EMA50) / H1 ATR14`

Fixed threshold derived from the discovery sample and frozen here:

`LOW = h1_ema_sep_atr < 0.9033277894201235`

Hypothesis:

For prospective `SHORT` primary families, the LOW subgroup has higher mean realized-R than `SHORT` families with `h1_ema_sep_atr >= 0.9033277894201235`.

Confirmatory comparison is LOW minus REST. The threshold must not be re-estimated from confirmation data.

Minimum confirmatory reporting requirement:

- at least 20 resolved future primary SHORT families in LOW;
- at least 20 resolved future primary SHORT families in REST;
- report expectancy difference, bootstrap 95% CI and two-sided permutation p-value;
- report symbol and UTC-day concentration;
- leave-one-symbol-out sign consistency must also be reported.

A result may be described as confirmatory-supporting only if all are true:

- mean difference LOW minus REST >= +0.25R;
- bootstrap 95% CI lower bound > 0;
- permutation p < 0.05;
- no single symbol accounts for more than 40% of either comparison group;
- leave-one-symbol-out difference remains positive in at least 80% of eligible exclusions.

Even if these conditions are met, the result authorizes only a versioned future ablation/recalibration proposal under the project governance threshold; it does not modify v2.2 in place.

## H2 — rich obstacle inside 1R

Fixed predictor:

`rich_obstacle_inside_1R = level_v2_h1_next_level_R is not null and level_v2_h1_next_level_R < 1.0`

Hypothesis:

Primary families with an obstacle inside 1R have lower mean realized-R than otherwise comparable primary families without an obstacle inside 1R.

No threshold optimization is permitted. Report overall and by-side results. This remains secondary to H1.

## H3 — rich obstacle inside 3R

Fixed predictor:

`rich_obstacle_inside_3R = level_v2_h1_next_level_R is not null and level_v2_h1_next_level_R < 3.0`

Hypothesis:

Primary families with an obstacle inside 3R have lower mean realized-R than those without such an obstacle.

No threshold optimization is permitted. Report overall and by-side results. This remains secondary to H1.

## H4 — portfolio concentration hypothesis

Fixed concentration event:

At least 3 independent primary families with the same side whose entry times fall within a rolling 60-minute window.

Hypothesis:

Families inside such concentrated cohorts have worse aggregate portfolio behavior than non-concentrated families, measured through mean realized-R, cohort sum-R, and worst cohort sum-R.

This hypothesis concerns portfolio/risk-layer behavior only. It must not be converted into a signal-quality filter without separate validation.

## Multiple comparisons

H1 is the primary preregistered hypothesis. H2–H4 are secondary. Secondary p-values must be reported both raw and with Benjamini-Hochberg adjustment across the secondary family.

## Anti-leakage rules

- No entry before `2026-09-16T13:00:00Z` may enter the confirmation sample.
- No threshold in this document may be re-estimated from future outcomes.
- Unresolved families remain censored until a causal terminal event or the frozen 32-M15 max-hold boundary.
- Holdout remains closed.
- Historical P25/R90/R180/R365 results may be shown as context only; they are not fresh OOS confirmation.
- A future change requires a new version and explicit promotion decision.

## Discovery context (not confirmation evidence)

At the 2026-09-16 12:00Z diagnostic cutoff, the discovery sample contained 39 resolved primary families. The strongest post-hoc interaction was SHORT × LOW `h1_ema_sep_atr`, with LOW expectancy approximately -0.137R versus approximately -1.019R for MID+HIGH, but the LOW group was temporally concentrated and therefore susceptible to regime/time confounding.

This section is preserved only to explain why H1 was preregistered; it must not be mixed with future confirmation statistics.
