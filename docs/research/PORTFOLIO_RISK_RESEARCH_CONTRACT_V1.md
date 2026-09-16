# Portfolio Risk Research Contract v1

Status: **DIAGNOSTIC / NON-PRODUCTION**

## Purpose

Prospective v2.2 evidence shows that independently valid setup families can cluster in time, direction and correlated symbols. Per-trade risk alone is therefore insufficient for a future production authorization layer.

This contract defines the quantities that a future portfolio-risk gate must control. It does **not** set or authorize production values.

## Current motivating evidence

At accepted cutoff `2026-09-16T14:15:00Z`:

- open primary families: `7`;
- all seven are `SHORT`;
- max observed concurrent families: `7`;
- max observed concurrent SHORT families: `7`;
- largest correlated cohort: `4`;
- current unresolved symbols: ADAUSDT x2, DOGEUSDT x2, SUIUSDT, TRUMPUSDT, XRPUSDT.

Parametric gross-stop exposure if every family carried equal independent risk:

| Risk/family | 7 concurrent | 4-family correlated cohort |
|---:|---:|---:|
| 0.25% | 1.75% | 1.00% |
| 0.50% | 3.50% | 2.00% |
| 1.00% | 7.00% | 4.00% |
| 2.00% | 14.00% | 8.00% |

These are exposure calculations, not recommendations.

## Required future control parameters

A future production risk manager must accept explicit configured values for:

- `risk_per_trade_pct`;
- `max_portfolio_open_risk_pct`;
- `max_same_side_open_risk_pct`;
- `max_correlated_cluster_open_risk_pct`;
- `max_open_positions`.

Optional later extensions may include:

- per-symbol risk cap;
- sector/factor risk cap;
- leverage-adjusted notional cap;
- volatility-adjusted portfolio cap;
- exchange/margin utilization cap.

## Required behavior

Before any future order authorization, the risk layer must calculate the post-trade state and **fail closed** if any configured cap would be exceeded.

The calculation must use accepted open-position risk, not merely order count.

A setup may remain analytically valid while being rejected for portfolio concentration.

## Correlation handling

Correlation grouping is a portfolio-risk diagnostic, not canonical setup-family semantics.

Current research convention:

- same-side entries close in time are examined together;
- cross-symbol correlation is measured from causal historical returns;
- current diagnostic cluster threshold is `|rho| >= 0.70` where sufficient common history exists.

The production cluster model and thresholds require a separate versioned acceptance before enforcement.

## Governance

- frozen v2.2 is unchanged;
- no risk cap is selected here;
- no production enforcement is enabled;
- holdout remains closed;
- this contract defines an interface for future risk authorization only.

Canonical diagnostic implementation:

`research/strategy_benchmark_v1/prospective_portfolio_risk_layer.py`
