# Phase 11G - Horizon Time-Split Validation

Date: 2026-09-09

Status: **FAST CANONICAL / INTRADAY M15 UNIVERSAL TTL UNRESOLVED / MEDIUM H1 8-12H TIME-SPLIT VALIDATED / RESEARCH ONLY**

## Objective

Validate the provisional non-FAST setup-lifecycle bands on a new provider-recorded time segment without changing any trading hard gate, and test whether observed M15 lifecycle heterogeneity is explained by setup evidence type or primary-level timeframe.

This study does not select a profitability-optimal TTL. No synthetic outcomes, targets, ranks, context or probabilities are introduced.

## Shared invariants

Unchanged throughout the study:

- provider: `binance_usdm`;
- context freshness: `max_context_age_seconds=300`;
- newest recorded universe snapshot at/before the replay cutoff;
- canonical analyzer path;
- structural stop and nearest structural target only;
- `RR >= 3` hard gate;
- canonical ATR-used semantics;
- no synthetic 3R target;
- no probability calibration;
- FAST/M5 remains the only production-active profile.

## New time-separated sample

Provider-recorded universe interval:

- start: `2026-09-09T15:05:36.607853Z`;
- end: `2026-09-09T18:45:35.095933Z`;
- snapshots: `46`;
- strict symbol intersection: `42`;
- archive SHA-256: `8cf2a38529dec1ef949641feb9ccc7885b133ff50240e66b354ce0efa33894af`.

Eight-symbol liquidity panel:

- `XRPUSDT`;
- `DOGEUSDT`;
- `USELESSUSDT`;
- `IOSTUSDT`;
- `SUIUSDT`;
- `NEARUSDT`;
- `1000PEPEUSDT`;
- `ENAUSDT`.

Cohort SHA-256:

`5c23efe9f9749a48857e0fcd89521b923e2da6f780d29ae141b45db010b002bb`

Every symbol passed the deep-history target as-of `2026-09-09T18:45:00Z`:

- `1d=300`;
- `4h=300`;
- `1h=300`;
- `15m=400`;
- `5m=700`.

Bundle SHA-256 identities:

- XRPUSDT: `4335535469acaabbb202668d976b054ebc8b58be5ac7b3a8ab3e14370c137225`;
- DOGEUSDT: `f8ee05f4626d7e308759bd194cf399d8db51b5e75be8b5e61126c0dbc9dc990e`;
- USELESSUSDT: `6ee98ab18559b597768f2e7c4893eace5cfdbf0d3b214d9a2539b176757d01a1`;
- IOSTUSDT: `db40f971e1f2dc93ec8bab82beff7db0807c571c576242b9086a5556247945ee`;
- SUIUSDT: `7246ae1a5af31af1ad3b7481b377acc02563edaf89413138f9117e09e7a51b6e`;
- NEARUSDT: `a3c73e83529a98b6a1491544f07b1eba6ca1b9ed5f4c5ced97e1be4cb7296a9e`;
- 1000PEPEUSDT: `615088e31b9306791baaa26d6d79f0cf8ad496cb32f36bb8d31afbbb1654b4f9`;
- ENAUSDT: `ee32b52d64cc3cadd9d0500a1668a2403edb850c37fbe856e6958e885fef5d41`.

## INTRADAY / M15 time-split result

Evaluation window: `2026-09-09T15:15:00Z` through `2026-09-09T18:45:00Z`.

Aggregate:

- analyzed cutoffs: `112`;
- candidate records: `2754`;
- geometry records: `1415`;
- unique/tradable signals: `0`.

Lifecycle sensitivity:

| TTL | Geometry survivors | Share | RR-only survivors | Tradable |
| --- | ---: | ---: | ---: | ---: |
| 4h | 524 | 37.0% | 0 | 0 |
| 6h | 643 | 45.4% | 0 | 0 |
| 8h | 826 | 58.4% | 0 | 0 |
| 10h | 957 | 67.6% | 6 | 0 |
| 12h | 1130 | 79.9% | 31 | 0 |
| 15h | 1358 | 96.0% | 56 | 0 |
| 18h | 1415 | 100% | 56 | 0 |

All RR-only survivors in this sample belong to `NEARUSDT`. Therefore a longer global M15 TTL must not be selected merely because one symbol contributes the surviving RR-only population.

### Evidence-type stratification

Geometry records:

- `TRAP_LEVEL_CONFIRMATION`: `1400`;
- `TRAP_VSA_CONFIRMATION`: `15`, all on NEARUSDT;
- `VSA_LEVEL_CONFIRMATION`: `0` valid geometry records.

Evidence type does not explain the broad M15 lifecycle heterogeneity because almost the entire geometry population is the same setup family: `TRAP_LEVEL_CONFIRMATION`.

### Primary-level-timeframe stratification

For STRONG primary-level geometry in the new sample:

| Primary level TF | Geometry | Median setup age |
| --- | ---: | ---: |
| 15m | 364 | 382.5m |
| 1h | 199 | 420m |
| 4h | 68 | 420m |
| 1d | 28 | 637.5m |

Older structural timeframes explain part of the observed persistence, but this relation is not stable enough across time samples to justify a TTL lookup table.

## Exact first-study reconstruction

The original first horizon-study population was reconstructed from immutable recorded inputs and reproduced the checkpoint identities exactly:

- archive SHA-256: `c1a9b3bf0dcded79ff22beef6c7795ed7172b6dd3484730db7a561f743274ef4`;
- cohort SHA-256: `01fc835c63f555a578eaa9c9554df0fd7152336d35a8cd6297b3f8d204bed2f1`;
- XRPUSDT bundle: `3b61a36682075031dead1e7603cbc696827edac1ec0d65efb31d4fd66697f053`;
- DOGEUSDT bundle: `af67ab91d5be2e00bf534e8fefa56e16722453115f1ae9e81a630d12a8cbc48b`;
- SUIUSDT bundle: `36d714ab636f69b360cf35cb2c4fc1987a0e610957b5aa142b1d32cf60162aa8`.

This confirms that comparison against the first study is reproducible rather than an approximate reconstruction.

For STRONG primary-level geometry in that exact population:

- 15m level median age: `180m`;
- 1h level median age: `210m`;
- 4h level median age: `247.5m`;
- no STRONG 1d geometry existed in that sample.

The large shift in median ages between the exact first sample and the new sample means primary-level timeframe alone does not produce a stable universal M15 TTL rule.

## INTRADAY conclusion

The earlier `4-6h` M15 band remains a useful initial design hypothesis but is **not validated as a universal lifecycle rule**.

Current state:

- M15 is still the preferred first INTRADAY research setup timeframe because it is already canonical MTF data;
- no single M15 production TTL is approved;
- no symbol-specific, evidence-specific or level-timeframe-specific TTL table is approved;
- geometry-survival share alone is insufficient for further TTL optimization;
- further selection requires additional time-separated samples and, critically, naturally tradable setups with real resolved outcomes.

## MEDIUM / H1 time-split validation

Exact first-study H1 population:

- candidate records: `339`;
- geometry records: `36`;
- 8h survivors: `24/36 = 66.7%`;
- 12h survivors: `32/36 = 88.9%`;
- 16h survivors: `36/36 = 100%`;
- 24h survivors: `36/36 = 100%`;
- tradable signals: `0`.

New eight-symbol time-split population:

- analyzed cutoffs: `24`;
- candidate records: `863`;
- geometry records: `170`;
- 8h survivors: `95/170 = 55.9%`;
- 12h survivors: `144/170 = 84.7%`;
- 16h survivors: `167/170 = 98.2%`;
- 24h survivors: `170/170 = 100%`;
- RR-only survivors: `0` at 8h, `9` at 12h and longer, all from `NEARUSDT`;
- tradable signals: `0`.

The H1 distribution is materially more stable across the two time-separated samples than M15. The provisional `8-12h` MEDIUM lifecycle band is therefore **time-split validated as a design band**, but it remains research-only and is not a profitability optimum or production default.

## Research boundary after this validation

### FAST

- setup interval: M5;
- TTL: 60m / 12 bars;
- production-active and target-host validated.

### INTRADAY

- setup interval: M15;
- lifecycle: unresolved/provisional;
- earlier 4-6h hypothesis not validated as universal on the broader time-split panel;
- research-only.

### MEDIUM

- setup interval: H1;
- lifecycle design band: 8-12h / 8-12 bars;
- time-split validated for lifecycle persistence;
- research-only; no profitability or production activation claim.

## Next research rule

Do not continue adding TTL dimensions merely to fit current geometry ages. Continue provider-recorded accumulation and revisit INTRADAY/MEDIUM selection when additional time-separated evidence and naturally valid tradable setups/outcomes exist. No hard gate is to be weakened to create such evidence.
