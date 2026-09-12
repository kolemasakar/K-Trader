# K-Trader Current State

Updated: 2026-09-12  
Research checkpoint: `docs/checkpoints/2026-09-12_V2_2_FIRST_PROSPECTIVE_FAMILIES_AND_PROFILE_DATASET.md`

## Production state

Production remains unchanged by strategy research.

Accepted production application SHA:

`81b79b281a4cc330b7c11058d202e0d74fb6d70e`

Expected runtime contract:

- health `ok`;
- mode `read_only`;
- provider `binance_usdm`;
- `data_ready=true`;
- Action authentication enabled;
- `scanner_status=DEGRADED` is the known fail-closed/history-readiness condition and does not by itself mean the runtime is unavailable.

No production code, deployment, risk, execution or trading semantics were changed by the strategy-research batch.

## Research isolation

Research branch:

`research-strategy-benchmark-v1`

The research branch does not imply production activation.

Holdout remains:

`UNTOUCHED / NOT AUTHORIZED`

## Frozen INTRADAY candidate

Current strongest frozen research candidate:

`candidate_rule_set_v2_2`

Frozen executable harness SHA256:

`b8471af989090375dec9e25daae184814674a776ab9b46b45e660e35b368be08`

Frozen path:

`H1 direction/context -> M15 pullback -> M15 reclaim/continuation -> structural SL -> H1 structural-space gate -> nominal 3R`

Inherited quality gates:

- `abs(EMA20_H1 - EMA50_H1) / ATR14_H1 >= 0.20`;
- M15 signal body/range <= `0.60`;
- executed structural risk distance >= `1.25%` of entry.

Frozen structural-space layer:

- causal H1 swing radius `2`;
- clustering tolerance `0.20 * ATR14_H1`;
- confirmed cluster requires >=2 pivots;
- no obstacle ahead or nearest confirmed obstacle >=`3R`.

Frozen max hold:

`32 x M15 = 8h`

The 8h rule belongs only to this exact candidate and is not a universal profile limit.

## Historical pre-holdout result

| Segment | Trades | WR | expectancy_R | PF_R |
|---|---:|---:|---:|---:|
| Development | 23 | 47.83% | +0.1003R | 1.1818 |
| Validation | 10 | 30.00% | +0.2507R | 1.3941 |
| Non-holdout | 37 | 45.95% | +0.2888R | 1.5592 |
| Stress non-holdout | 37 | 43.24% | +0.2741R | 1.5235 |

Promotion gate remains **FAIL** because:

- non-holdout sample <100;
- validation sample <30;
- non-holdout WR <50%;
- validation WR <50%.

Therefore `production_approved=false` and `holdout_authorized=false`.

## Post-v2.2 diagnostics

Detailed historical diagnostic report:

`docs/research/PARALLEL_RESEARCH_RESULTS_2026-09-11.md`

Main current conclusions:

- STOP trades generally fail early rather than first producing large favorable excursion;
- TARGET trades usually show strength quickly;
- `clean break -> no revisit before entry` is the strongest current post-hoc structural hypothesis, but is not a v2.2 gate;
- canonical static level clustering does not reproduce the discrimination of the richer Level Context v2 layer;
- historical non-holdout economics are materially supported by IOSTUSDT: removing it leaves expectancy positive at about `+0.046R`, PF about `1.079`, WR about `39.4%`;
- median explicit fee+funding cost is about `0.041R` and median explicit+base execution burden about `0.051R`;
- raw canonical VSA does not support a mandatory directional-match gate.

None of these diagnostics are independent OOS evidence and none automatically changes the frozen rules.

## Prospective frozen-v2.2 evidence

Frozen prospective boundary:

`2026-09-11T20:00:00Z`

The runner is provider-recorded, immutable and fail-closed. It records bundle/protocol/harness hashes and rejects invalid snapshots from the evidence ledger.

Valid snapshots:

- `20:30Z`: 19/19 symbols, 19 entry-evaluable symbol-bars, 0 events;
- `20:45Z` retry-2: 19/19, 38 symbol-bars, 0 events;
- `21:00Z`: 19/19, 57 symbol-bars, 0 events;
- `2026-09-12 00:00Z`: 19/19, 285 symbol-bars, 11 events, 3 eligible observations, 2 unique eligible families.

One first-attempt `20:45Z` capture is explicitly `INVALID_INFRASTRUCTURE` because of the old bundle-layout error and is excluded by ledger v1.1.

Latest evidence status:

`OBSERVATION_ONLY_LT_30_FAMILIES`

Latest ledger SHA256:

`a4f04b85f9568b3f4df02fd11d2744e25176053cfee793054c346700832f5e27`

### First eligible prospective observations

All three are `RAYSOLUSDT LONG` and belong to two setup families.

Family `15fc0ad1...`:

- signal `20:45Z`, entry `21:00Z`;
- signal `21:00Z`, entry `21:15Z`.

Family `6aabd4ef...`:

- signal `23:00Z`, entry `23:15Z`.

All three carried `clean_break_no_revisit=true`; this remains observation-only.

At the exact `00:00Z` cutoff no observation had a terminal STOP or 3R TARGET:

- first: MFE `2.514R`, MAE `0.027R`;
- second: MFE `1.836R`, MAE `0.061R`;
- third: MFE `0.232R`, MAE `0.638R`.

All remain censored until a frozen terminal outcome becomes causally observable. They must not be counted as wins/losses yet.

Partial-outcome artifact SHA256:

`fab4fca86ecc26f5817318702d716e19c801080235168ee024affcee8c526185`

## Multi-profile research dataset

A separate research-only adaptive dataset was captured at:

`2026-09-11T20:45:00Z`

It is explicitly not a v2.2 retuning source.

Panel: 19/19 `binance_usdm` symbols.

Depths:

- M5 = 3000 bars;
- M15 = 3000;
- H1 = 2000;
- H4 = 1000;
- D1 = up to 500, listing-age aware.

Age-limited D1 histories:

- AKEUSDT 350;
- METUSDT 335;
- PUMPUSDT 428;
- USELESSUSDT 392.

Dataset summary SHA256:

`4f49f57dcd3d36939bfa56167b13a9af2ea08884fb11be66dd0f957389b3f077`

### Funding layer

Official Binance Futures funding source:

`/fapi/v1/fundingRate`

Funding was captured for 19/19 symbols.

Completeness status:

`PASS_WITH_LISTING_BOUNDARY_HEAD_GAPS`

Audit facts:

- 19/19 pass;
- strictly increasing timestamps;
- all records inside query bounds;
- maximum internal gap <=`8.01h`;
- tail lag <=`8.01h`;
- head lag <=24h for listing-day boundaries.

Listing-boundary head-gap symbols:

`AKEUSDT`, `METUSDT`, `USELESSUSDT`.

Funding summary SHA256:

`c987475c7417bb8c34722e0da67ebe71909eb57a99af3be0191d02209122911f`

Funding completeness report SHA256:

`42e48e6452f80a940018859a072705a06dcf2551dabb7d1056b3116f7bb48d88`

This removes the historical OHLCV+funding prerequisite for FAST/SWING research on currently supported canonical intervals. POSITION still requires a separate W1 data contract.

## Cross-provider portability

`bybit_linear` supports 16/19 fixed-panel symbols. Missing:

`PUMPUSDT`, `RAYSOLUSDT`, `VTHOUSDT`.

At synchronized `20:45Z` on the common 16-symbol set:

- median M15 return correlation ~`0.9984`;
- median absolute close basis ~`4.32 bps`;
- Binance events 0;
- Bybit events 0.

This is data/signal portability only, not profitability validation.

## Profile architecture

Research spec:

`docs/research/PROFILE_RESEARCH_SPECS_FAST_SWING_V0.md`

Current research envelopes:

| Profile | Context | Setup/trigger | Research envelope |
|---|---|---|---|
| FAST | H1/M15 | M15 -> M5 | up to ~4h |
| INTRADAY | H4/H1 conceptual; frozen v2.2 currently H1 | M15 | ~8–12h architecture; frozen v2.2 uses 8h |
| SWING | D1/H4 | H1 | ~2–4 days |
| POSITION | W1/D1 | H4 | ~7–21 days, architecture reserved |

TTL before entry and max-hold after entry remain separate concepts.

## Evidence governance

Primary evidence unit = **unique resolved setup family**.

Current prospective state:

- 2 unique eligible families;
- 0 resolved families.

Evidence bands remain:

- `<30`: observation only;
- `30–49`: diagnostics;
- `50–99`: hypotheses/ablation proposals only;
- `>=100`: versioned recalibration proposal may be considered, still requiring fresh OOS/prospective evidence and explicit promotion.

Every rule change requires a new strategy version, preregistration, causal full-path testing, fresh OOS/prospective evidence and explicit promotion. Validation/holdout must not be repeatedly mined to tune the same version.

## Current safe work boundary

Continue:

- exact frozen-v2.2 prospective shadow capture;
- causal outcome resolution of prospective families;
- provenance/ledger hardening;
- feature observation without changing eligibility;
- separate FAST/SWING research using the new dataset;
- portfolio/correlation research.

Do not change frozen v2.2 from currently seen data:

- no clean-break/no-revisit hard gate;
- no early-progress exit rule;
- no new min-risk threshold;
- no volume/VSA hard gate;
- no IOST inclusion/exclusion rule;
- no RR or 8h retuning;
- no holdout opening.

## Next hard evidence milestone

`>=30 unique resolved prospective frozen-v2.2 setup families`

Until then prospective evidence remains observation-only.
