# Phase 11G Horizon Profile Lifecycle Study

Date: 2026-09-09

Status: RESEARCH COMPLETE / FAST CANONICAL / INTRADAY + MEDIUM PROVISIONAL

## Objective

Test whether the existing 60-minute setup TTL should remain universal when K-Trader is used for different trading horizons.

Owner direction:

- fast trades up to roughly four hours may retain the current short lifecycle;
- same-day trading should use a less local setup timeframe around M15-M30 and a longer lifecycle;
- medium-duration trading should use a setup timeframe around H1 and a still longer lifecycle.

## Implementation corrections required before research

The pre-study runtime had three FAST-specific assumptions:

1. `RuntimeScannerConfig.setup_interval` accepted only `5m`.
2. Analyzer converted setup age bars to seconds with a hard-coded `bars * 5 * 60` formula.
3. ATR-used daily range was built from `setup_candles`, which is valid only while setup interval is M5; the canonical day-range builder correctly requires M5.

The research branch corrects these without changing the FAST default:

- supported research setup intervals: `5m`, `15m`, `1h`;
- derived TTL: `setup_max_age_bars * setup_interval_seconds`;
- `setup_max_age_seconds` is exposed as a config property;
- ATR-used UTC-day range remains canonical M5 regardless of setup/evidence timeframe;
- replay CLI can explicitly select setup interval and setup max-age bars;
- a dedicated lifecycle sensitivity script instruments candidate geometry age while leaving all other hard gates unchanged.

M30 was not introduced because it is not currently part of the canonical MTF history plan/bundle. M15 is the first INTRADAY research timeframe.

## Research provenance

Production research data was used read-only; deployed source was not mutated.

Universe context:

- provider: `binance_usdm`;
- window source: immutable Phase 11F captures from 2026-09-08 and 2026-09-09;
- selected archive range: `2026-09-08T15:00:46.200766Z` through `2026-09-09T14:55:37.490972Z`;
- snapshots: `289`;
- archive SHA-256: `c1a9b3bf0dcded79ff22beef6c7795ed7172b6dd3484730db7a561f743274ef4`;
- cohort SHA-256: `01fc835c63f555a578eaa9c9554df0fd7152336d35a8cd6297b3f8d204bed2f1`;
- context max age: `300 seconds`.

Study panel: three symbols present in all 289 snapshots and among the strongest average liquidity ranks:

- `XRPUSDT`;
- `DOGEUSDT`;
- `SUIUSDT`.

Deep replay bundles as-of `2026-09-09T15:00:00Z`:

- XRPUSDT bundle SHA-256: `3b61a36682075031dead1e7603cbc696827edac1ec0d65efb31d4fd66697f053`;
- DOGEUSDT bundle SHA-256: `af67ab91d5be2e00bf534e8fefa56e16722453115f1ae9e81a630d12a8cbc48b`;
- SUIUSDT bundle SHA-256: `36d714ab636f69b360cf35cb2c4fc1987a0e610957b5aa142b1d32cf60162aa8`.

Bundle depths:

- `1d=300`;
- `4h=300`;
- `1h=300`;
- `15m=400`;
- `5m=700`.

Instrumented sensitivity evaluation window:

- `2026-09-09T12:00:00Z` through `2026-09-09T15:00:00Z`;
- same canonical full analyzer;
- all RR/ATR/structure/context/scoring gates unchanged;
- profile expiry was evaluated post hoc from actual `SetupGeometry.confirmation_time` so multiple TTL thresholds could be compared from one analyzer run per symbol/timeframe.

## INTRADAY / M15 results

Across the three symbols:

- candidate records: `994`;
- geometry records: `359`;
- observed median setup age by symbol: `180m`, `195m`, `210m`;
- observed p90 setup age by symbol: `525m` to `600m`;
- observed maximum setup age: `690m`.

Aggregate lifecycle sensitivity:

| TTL | Geometry survivors | Expired | Survivor share |
| --- | ---: | ---: | ---: |
| 60m | 83 | 276 | 23.1% |
| 120m | 110 | 249 | 30.6% |
| 240m | 227 | 132 | 63.2% |
| 360m | 279 | 80 | 77.7% |
| 480m | 290 | 69 | 80.8% |

Base hard-reject population included:

- `HTF_CONTEXT_MISMATCH`: 916;
- `INVALID_GEOMETRY`: 635;
- `PRIMARY_LEVEL_NOT_STRONG`: 633;
- `RR_BELOW_3`: 359.

No M15 configuration produced a tradable signal in this sample.

Interpretation:

- 60-120m remains too short for the observed M15 setup lifecycle;
- the largest transition occurs by 4h;
- 4h retains about 63% of geometries;
- 6h retains about 78%;
- extending to 8h adds relatively little versus 6h in this sample.

Research conclusion: provisional INTRADAY lifecycle band `4–6h`, with M15 as the initial setup/evidence interval.

## MEDIUM / H1 results

Across the three symbols:

- candidate records: `339`;
- geometry records: `36`;
- observed symbol medians: `60m`, `300m`, `330m`;
- maximum observed age: `840m`.

Aggregate lifecycle sensitivity:

| TTL | Geometry survivors | Expired | Survivor share |
| --- | ---: | ---: | ---: |
| 60m | 17 | 19 | 47.2% |
| 120m | 21 | 15 | 58.3% |
| 240m | 21 | 15 | 58.3% |
| 480m | 24 | 12 | 66.7% |
| 720m | 32 | 4 | 88.9% |
| 1440m | 36 | 0 | 100% |

Base hard-reject population included:

- `HTF_CONTEXT_MISMATCH`: 315;
- `INVALID_GEOMETRY`: 303;
- `PRIMARY_LEVEL_NOT_STRONG`: 215;
- `RR_BELOW_3`: 36.

No H1 configuration produced a tradable signal in this sample.

Interpretation:

- a 60m universal TTL is not suitable for H1 lifecycle research;
- 8h retains about two thirds of observed geometries;
- 12h retains nearly 89%;
- 24h eliminates expiry in this sample and is therefore too permissive to justify as a first research default without stronger outcome evidence.

Research conclusion: provisional MEDIUM lifecycle band `8–12h`, with H1 as the initial setup/evidence interval.

## What this study does not prove

The sample produced zero tradable signals under unchanged canonical hard gates. Therefore it does not provide WIN/LOSS or expectancy evidence from which a profitability-optimal TTL can be selected.

The terms `4–6h` and `8–12h` are lifecycle research bands, not profitability optima and not production defaults.

Further selection requires larger time-separated samples with naturally valid trades and real resolved outcomes. No threshold may be loosened to manufacture such a sample.

## Profile state after study

### FAST

- production/canonical profile;
- setup interval: M5;
- TTL: 60m / 12 bars;
- unchanged.

### INTRADAY

- research profile;
- setup interval: M15;
- provisional TTL band: 4–6h / 16–24 bars;
- not production-active.

### MEDIUM

- research profile;
- setup interval: H1;
- provisional TTL band: 8–12h / 8–12 bars;
- not production-active.

## Guardrails

Unchanged:

- `RR >= 3`;
- structural SL/TP;
- no synthetic 3R target;
- ATR-used semantics;
- context freshness `300s` for this research chain;
- no synthetic outcomes;
- no probability calibration;
- FAST remains the only production profile until separately approved and deployed.
