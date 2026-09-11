# Level Context Layer v2 + MFE/MAE — Initial Diagnostic Results

Date: 2026-09-11
Status: INITIAL DIAGNOSTIC PASS / FROZEN v2.2 UNCHANGED / HOLDOUT UNTOUCHED / NO PRODUCTION CHANGE

## Scope

This report records the first parallel execution of:

A. `Level Context Layer v2` feature extraction;
B. actual-path `MFE/MAE` diagnostics for frozen `candidate_rule_set_v2_2` trades.

The work is diagnostic only. It does not change v2.2 eligibility, entry, stop, target, max-hold, risk or production behavior.

## Code

Level Context feature module:

`research/strategy_benchmark_v1/level_context_v2_features.py`

Level Context runner:

`research/strategy_benchmark_v1/run_level_context_v2.py`

MFE/MAE diagnostics:

`research/strategy_benchmark_v1/mfe_mae_diagnostics.py`

Because the benchmark source manifest contains merged `5m/15m/1h` histories but not merged `4h`, the runner constructs H4 causally from complete UTC-aligned groups of four closed H1 bars. Incomplete H4 buckets are discarded.

## Artifacts

Level Context summary:

`/data/research/phase11g/strategy_benchmark_v1/combined_rules/level_context_v2/summary.json`

SHA256:

`c1cc84f1d2f04f12c419ae1e658cc9bdc7f6a8f1a6b55052f8f524f21f679167`

MFE/MAE report:

`/data/research/phase11g/strategy_benchmark_v1/combined_rules/mfe_mae_v2_2/report.json`

SHA256:

`c71944cc28cc514b11453769b026ca8159aec04a5a0532183ea5080c84336385`

Holdout opened: **false**.

## A. Level Context Layer v2 — first result

Feature availability was complete for all frozen v2.2 completed trades in development, validation and non-holdout.

### Open-space classification

| Segment | n | H1 open-space | H4 open-space |
|---|---:|---:|---:|
| Development | 23 | 13 | 22 |
| Validation | 10 | 7 | 8 |
| Non-holdout | 37 | 22 | 32 |

The original minimal v2.2 detector classified 35/37 non-holdout trades as open-space. The richer H1 feature layer reduces that to 22/37, meaning it recognizes a materially larger set of nearby structural obstacles without changing any executed trade.

This is evidence that the previous `h1_pivot_cluster_v1` was too sparse as a market-description layer.

### Other first-pass structural features

Non-holdout:
- H1 trend-break present: 37/37;
- H4 trend-break present: 37/37;
- H1 floating-zone flag: 1/37;
- H4 floating-zone flag: 0/37;
- next-level mirror flag: 0/37 on both H1/H4.

Interpretation:
- current trend-break detector is broad and therefore not yet discriminative;
- floating-zone threshold is highly selective in this sample;
- mirror classification is too sparse under the current deterministic definition;
- these features need calibration/review as descriptors before any future rule proposal.

None becomes a hard gate from this diagnostic pass.

## B. MFE/MAE — non-holdout actual-path result

Frozen v2.2 non-holdout completed trades: `37`.

Overall:
- mean realized R: `+0.2888R`;
- median MFE: `1.066R`;
- mean MFE: `1.288R`;
- median MAE: `0.882R`;
- mean MAE: `0.704R`;
- median time-to-MFE: `3 M15 bars`;
- median explicit fee+funding cost: approximately `0.041R`.

### STOP trades

STOP count: `18`.

- mean MFE before stop: `0.438R`;
- median MFE before stop: `0.355R`;
- reached +0.5R before stop: `5/18`;
- reached +1R before stop: `3/18`;
- reached +2R before stop: `0/18`.

Interpretation: most losing trades failed relatively early and did not first produce large favorable excursion. The initial evidence does **not** support a simple claim that most stops are merely winners being stopped after +1R/+2R.

A small subset did reach +1R before later stopping; this is diagnostic only and insufficient for a management-rule change.

### TARGET trades

TARGET count: `8`.

- median MAE before target: `0.227R`;
- mean MAE before target: `0.255R`;
- median time to 3R: `13.5 M15 bars` (~3h22m).

Interpretation: successful 3R trades generally did not require deep adverse excursion and usually resolved well inside the frozen 8h max-hold.

### TIME_EXIT trades

TIME_EXIT count: `11`.

- positive realized R: `9/11`;
- mean realized R: `+0.550R`;
- median MFE: `1.546R`;
- mean MFE: `1.432R`;
- median MAE: `0.462R`;
- median terminal 4-bar directional slope: approximately `+0.035R`.

Interpretation:
- many time exits had meaningful favorable excursion but retraced before the 8h exit;
- terminal short-window slope is near flat/slightly positive in aggregate, not a strong signal that simply extending max-hold would improve outcomes;
- because targets that succeed typically reach 3R much earlier (~3.4h median), current evidence still does not justify extending v2.2 max-hold.

A future version may investigate profit-management/time-exit behavior, but not by modifying frozen v2.2 in place.

## Structural context joined with outcomes

Using Level Context Layer v2 H1 classification on the same frozen trades:

### Development
- H1 open-space: n=13, mean realized `+0.759R`;
- H1 obstacle-ahead: n=10, mean realized `-0.756R`.

### Non-holdout
- H1 open-space: n=22, mean realized `+0.796R`;
- H1 obstacle-ahead: n=15, mean realized `-0.456R`.

### Validation
- H1 open-space: n=7, mean realized `+0.248R`;
- H1 obstacle-ahead: n=3, mean realized `+0.257R`.

This is a potentially important structural hypothesis because development and combined non-holdout show a large separation. However validation is tiny and does not reproduce a comparable separation.

Therefore **do not promote H1 open-space v2 as a hard gate from this result**.

Correct next use:
- retain as a candidate causal feature;
- collect prospective values under frozen execution;
- test a separately preregistered future version if independent evidence accumulates.

## Risk-distance diagnostic

Non-holdout mean realized R by initial risk-distance bucket:
- 1.25-1.5%: n=4, `+0.911R`;
- 1.5-2.0%: n=8, `-0.898R`;
- 2.0-3.0%: n=7, `-0.433R`;
- >=3.0%: n=18, `+0.959R`.

This is non-monotonic and the small buckets are unstable. It does not justify changing the frozen 1.25% minimum risk-distance gate.

## Direction diagnostic

Non-holdout:
- LONG: n=34, mean realized `+0.173R`;
- SHORT: n=3, mean realized `+1.597R`.

SHORT sample is far too small for a side-specific rule. No side is disabled or promoted.

## Methodology notes

MFE/MAE report is `actual_path_only=true`.

For the exit-event bar, diagnostics use only the known terminal execution event rather than the full bar high/low, avoiding unknown intrabar ordering after the exit.

This makes exit-bar excursion estimates conservative and prevents hidden look-ahead.

No post-exit counterfactual bars are mixed into actual-path MFE/MAE.

## Initial conclusions

1. `Level Context Layer v2` materially improves structural description compared with the sparse v2.2 detector, but its subfeatures are not yet validated trading gates.
2. Most STOP trades fail before achieving +0.5R/+1R; entry/context quality remains a primary research target.
3. Successful TARGET trades typically reach 3R well inside 8h, weakening the case for extending current INTRADAY max-hold.
4. TIME_EXIT trades frequently had >1R MFE but finished around +0.55R on average; this supports future management diagnostics, not an immediate rule change.
5. H1 open-space v2 shows a strong development/non-holdout association with outcome, but validation is too small to authorize promotion.
6. Current risk-distance and side subgroups are too small/non-monotonic for rule changes.

## Next steps

Continue Track A by improving descriptive coverage for:
- mirror levels;
- false-break context;
- rejection tails;
- consolidation boundaries;
- level age/strength;
- floating-zone score;
- obstacle quality/confidence.

Continue Track B by adding:
- distribution/quantile tables for time-to-1R/2R/3R;
- STOP path categories (immediate failure vs favorable-then-reversal);
- TIME_EXIT path categories;
- prospective joining of Level Context v2 features.

Hard boundaries remain:
- v2.2 frozen;
- holdout untouched;
- production unchanged;
- validation not reused as fresh OOS;
- any future trading-rule change requires a new preregistered strategy version.