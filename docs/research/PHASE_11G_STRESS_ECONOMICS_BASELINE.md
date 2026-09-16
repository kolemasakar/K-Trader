# Phase 11G Stress Economics Baseline

Status: **DOCUMENTED / DIAGNOSTIC / NON-AUTHORIZING**

Purpose: package the already-accepted causal historical BASE vs STRESS execution-cost evidence so the Phase 11G closure report has an explicit stress-economics reference.

Source root:

`/data/research/phase11g/historical_robustness_v1_20260905T144500Z/results_rolling_context_v1`

Methodology guard:

- corrected causal rolling-context replay;
- frozen v2.2 strategy;
- historical evidence only;
- historical trades do not count toward prospective family thresholds;
- do not use this document to retune v2.2 in place.

## BASE vs STRESS results

| Window | BASE trades | BASE expectancy | BASE PF_R | STRESS trades | STRESS expectancy | STRESS PF_R |
|---|---:|---:|---:|---:|---:|---:|
| P25 | 214 | +0.259415R | 1.51934 | 218 | +0.224861R | 1.44589 |
| R90 | 531 | +0.031637R | 1.05736 | 545 | -0.009676R | 0.98289 |
| R180 | 1073 | -0.013131R | 0.97609 | 1104 | -0.042896R | 0.92315 |
| R365 | 2099 | -0.051000R | 0.90956 | 2170 | -0.074531R | 0.87036 |

## Interpretation

- recent P25 remains positive under the accepted stress-cost scenario;
- R90 is approximately neutral in BASE but becomes slightly negative under stress;
- R180 and R365 are negative in both BASE and STRESS;
- execution-cost stress worsens results but does not explain the main long-horizon weakness;
- this is consistent with the prospective finding that current negative expectancy is primarily a signal/regime problem rather than a pure fee/slippage problem.

## Prospective execution economics context

At accepted cutoff `2026-09-16T16:30:00Z`, prospective resolver economics include persisted funding, fees and base slippage. The latest resolved prospective expectancy is `-0.5539825538R` on `43` resolved primary families.

Prospective stress replay is not required to reinterpret the historical windows; if a future closure report needs a dedicated prospective stress transformation, it must be versioned and diagnostic-only rather than modifying accepted outcomes.

## Closure use

This document satisfies the Phase 11G requirement to explicitly package available stress economics before closure.

It does not authorize:

- production risk caps;
- strategy retuning;
- holdout access;
- Phase 12;
- production trading.
