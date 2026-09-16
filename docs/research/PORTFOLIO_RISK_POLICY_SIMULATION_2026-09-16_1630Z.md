# Portfolio Risk Policy Simulation — 2026-09-16 16:30Z

Status: **DIAGNOSTIC ONLY / NO PRODUCTION POLICY SELECTED**

Source script:

`research/strategy_benchmark_v1/portfolio_risk_policy_simulation.py`

Runtime report SHA256:

`a336d786b7c9f061c23ddae2490f8aa96951a28f7436bd80b2d7aacb8ef5e38c`

## Objective

Quantify how simple pre-trade portfolio caps would have changed concentration in the already-observed prospective family stream.

This is not a profitability optimizer and must not be used to choose production caps by maximizing historical expectancy.

## Observed uncapped concentration

At the 16:30Z diagnostic state:

- maximum concurrent families observed: `8`;
- maximum concurrent SHORT families: `8`;
- largest correlated cohort: `4`;
- current unresolved open families: `4`.

## Simulated policy scenarios

| Policy | Risk/family | Max positions | Max portfolio risk | Max same-side risk | Max cluster risk | Accepted / 47 | Resolved accepted expectancy |
|---|---:|---:|---:|---:|---:|---:|---:|
| P025_3_CONSERVATIVE | 0.25% | 3 | 0.75% | 0.75% | 0.50% | 30 | -0.60386R |
| P050_3_BALANCED | 0.50% | 3 | 1.50% | 1.50% | 1.00% | 30 | -0.60386R |
| P050_4_BALANCED | 0.50% | 4 | 2.00% | 2.00% | 1.00% | 33 | -0.60421R |
| P050_5_WIDE | 0.50% | 5 | 2.50% | 2.50% | 1.50% | 40 | -0.60030R |

## Interpretation

The scenarios materially reduce concurrency and correlated exposure, but none changes the fundamental sign of the observed strategy expectancy.

Therefore:

- portfolio caps are necessary as a future **risk-control layer**;
- they are not a substitute for positive strategy alpha;
- no cap set is promoted from this diagnostic sample;
- production cap selection requires an independent risk-design decision and validation, not post-hoc selection on this sample.

## Control contract retained

Any future production authorization layer should support at minimum:

- `risk_per_trade_pct`;
- `max_portfolio_open_risk_pct`;
- `max_same_side_open_risk_pct`;
- `max_correlated_cluster_open_risk_pct`;
- `max_open_positions`.

Pre-trade authorization must fail closed when any configured cap would be exceeded.
