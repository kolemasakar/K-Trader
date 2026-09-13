# Frozen v2.2 Historical Robustness Windows v1 — Preregistered Protocol

Date: 2026-09-13
Status: PREREGISTERED SECONDARY ROBUSTNESS / HOLDOUT UNTOUCHED / PRODUCTION UNCHANGED

## Purpose

Extend the already accepted 25-day Historical Expansion v1 with fixed longer windows while preserving the exact frozen `candidate_rule_set_v2_2` rules.

These windows are secondary robustness evidence. They do not replace the accepted 25-day primary confirmatory block and do not count toward prospective family thresholds.

## Frozen identity

- strategy: `candidate_rule_set_v2_2`
- frozen harness SHA256: `b8471af989090375dec9e25daae184814674a776ab9b46b45e660e35b368be08`
- hard historical cutoff: `2026-09-05T14:45:00Z`
- target: `3R`
- max hold: `32 x M15`
- fee: frozen harness value
- base/stress execution slippage: frozen harness values
- funding: official Binance USD-M funding history
- same-bar ambiguity: STOP first

No strategy parameter, symbol-selection rule or direction filter may be changed based on the results.

## Windows fixed before outcome inspection

All windows end at the same hard cutoff and are intentionally nested robustness views:

- `R90`: final `8640` M15 bars = 90 days;
- `R180`: final `17280` M15 bars = 180 days;
- `R365`: final `35040` M15 bars = 365 days.

The accepted 25-day Historical Expansion v1 remains the primary historical confirmatory result.

## Data and warm-up requirements

Start from the same frozen 19-symbol panel. No substitution is permitted.

For each window, a symbol is included before outcomes are evaluated only if it has at least:

- M15: evaluation bars + `600` causal warm-up bars;
- H1: window duration in hours + `300` causal warm-up bars;
- contiguous provider-recorded closed candles;
- funding history covering the scored evaluation interval.

Therefore required depths are:

- R90: M15 `9240`, H1 `2460`;
- R180: M15 `17880`, H1 `4620`;
- R365: M15 `35640`, H1 `9060`.

A 1D history is collected only to establish funding-query coverage and provenance; lack of 500 full D1 bars does not by itself exclude a symbol if the M15/H1/funding criteria pass.

Symbols that fail a window's objective readiness criteria are labelled `AGE_LIMITED` / `DATA_INCOMPLETE` for that window. They are not replaced and the window is not shifted.

## Isolation

No candle closing at or after `2026-09-05T14:45:00Z` may be scored.

The existing benchmark development/validation/holdout dataset is not used as an outcome source. The existing holdout remains unopened.

## Metrics

For each window report:

- eligible symbol cohort before outcomes;
- completed trades and censored positions;
- wins/losses and win rate;
- expectancy_R after costs;
- profit_factor_R;
- max drawdown in chronological trade stream;
- STOP/TARGET/TIME_EXIT composition;
- LONG/SHORT counts and expectancy;
- per-symbol trade count / expectancy;
- top-symbol share;
- base and stress-slippage results;
- time-block stability diagnostics;
- concentration / coverage warnings.

## Interpretation

R90/R180/R365 are nested secondary robustness views, not independent prospective tests. Their purpose is to detect time/regime dependence, sample concentration and failure of the historical edge over longer horizons.

They may motivate hypotheses for a future preregistered strategy version, but they do not authorize modifying frozen v2.2 in place.

Historical trades must never be added to the prospective unique-family counts.

## Fail closed

Abort or mark a window invalid if:

- frozen harness SHA differs;
- hard cutoff isolation is violated;
- outcome-based symbol inclusion occurs;
- provider sequence is non-contiguous;
- required funding coverage is missing;
- existing holdout outcomes are accessed;
- the fixed window length is changed after results are seen.
