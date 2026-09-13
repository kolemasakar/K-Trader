# Frozen v2.2 Historical Expansion v1 — Preregistered Protocol

Date: 2026-09-13
Status: PREREGISTERED / RESEARCH ONLY / HOLDOUT UNTOUCHED / PRODUCTION UNCHANGED

## Purpose

Run a large historical confirmatory evaluation of the already frozen `candidate_rule_set_v2_2` without changing its trading rules and without using the existing strategy-benchmark holdout.

This track supplements, but does not replace, the independent prospective evidence stream that begins at `2026-09-11T20:00:00Z`.

## Frozen candidate identity

- strategy: `candidate_rule_set_v2_2`
- frozen harness SHA256: `b8471af989090375dec9e25daae184814674a776ab9b46b45e660e35b368be08`
- target: `3R`
- max hold: `32 x M15 = 8h`
- H1 EMA20/EMA50 separation / ATR14 >= `0.20`
- M15 signal body/range <= `0.60`
- executed structural risk distance >= `1.25%`
- H1 structural-space gate: open space OR next confirmed obstacle >= `3R`
- same-bar ambiguity: STOP first
- fees/slippage/funding retained

No parameter above may be changed after historical outcomes are inspected.

## Existing benchmark isolation

The currently prepared benchmark data begins on approximately `2026-09-05` and contains development, validation and an untouched holdout. Historical Expansion v1 must not evaluate any interval at or after the existing benchmark start.

Hard external cutoff:

`2026-09-05T14:45:00Z`

All evaluated M15 bars must close strictly before that cutoff.

The existing benchmark holdout remains unopened and is not counted in Historical Expansion v1.

## Dataset source

Provider: `binance_usdm` only.

Canonical K-Trader deep-history pagination is used. Provider pages must remain single-provider, closed, chronological, deduplicated and contiguous.

Funding must be obtained from Binance official USD-M funding history. No zero-funding substitute is permitted for final confirmatory metrics.

## Panel

Start from the frozen 19-symbol primary panel. No symbol substitution is allowed.

A symbol may enter the primary confirmatory cohort only by objective data-readiness rules, not by performance:

- instrument exists at the historical cutoff;
- at least `3000` closed M15 bars are available before the cutoff;
- at least `1000` closed H1 bars are available before the cutoff;
- required sequences are contiguous;
- funding history covers the evaluated interval sufficiently for the frozen cost model.

Symbols failing these conditions remain in the coverage report as `AGE_LIMITED` or `DATA_INCOMPLETE` and are excluded from primary aggregate metrics. Their outcomes must not be inspected and then used to decide inclusion.

## Confirmatory evaluation window

For every primary-cohort symbol, evaluate the final `2400` M15 bars immediately preceding the hard cutoff, equivalent to 25 days of 24/7 market time.

Additional earlier H1/M15 bars are retained only as causal warm-up/context and are not scored as entries outside the fixed evaluation window.

The evaluation end is fixed before outcomes are seen. The window must not be shifted based on results.

## Secondary coverage blocks

After the primary 25-day block is completed, longer historical windows may be added only as separately labelled robustness blocks. They may not redefine the primary confirmatory result.

Any later 90-day / 180-day / 1-year study requires its own immutable window specification and must preserve the same rule freeze.

## Metrics to report

Primary:

- completed trades;
- wins / losses;
- win rate;
- expectancy_R after costs;
- profit_factor_R;
- max drawdown in R;
- STOP / TARGET / TIME_EXIT composition;
- LONG / SHORT counts;
- per-symbol trade counts and expectancy;
- top-symbol share;
- cumulative fees, funding and slippage contribution where available.

Robustness diagnostics:

- base slippage versus frozen stress slippage;
- result by symbol;
- result by direction;
- result by calendar sub-window;
- concentration warnings.

## Interpretation rules

Historical Expansion v1 is confirmatory historical evidence, not prospective evidence.

It must never be merged numerically with the prospective family count used for the `<30 / 30–49 / 50–99 / >=100` prospective governance thresholds.

Historical results may strengthen or weaken confidence in v2.2, identify regime dependence, and motivate hypotheses for a future preregistered version. They do not authorize in-place tuning of v2.2.

If historical results suggest a rule change, that change must become a new version with fresh OOS/prospective validation.

## Fail-closed conditions

Abort primary evaluation if:

- frozen harness SHA differs;
- existing benchmark holdout is accessed for outcomes;
- provider data cannot be made contiguous;
- funding/cost treatment materially differs from the frozen economics;
- evaluation window or symbol inclusion is changed after outcome inspection.

## Relationship to current work

Track A: continue frozen-v2.2 prospective collection unchanged.

Track B: execute this preregistered historical expansion in parallel.

Production remains unchanged and read-only.