# CHECKPOINT — v2.2 First Prospective Families + Multi-Profile Dataset — 2026-09-12

Status: **OBSERVATION-ONLY PROSPECTIVE EVIDENCE / HOLDOUT UNTOUCHED / PRODUCTION UNCHANGED**

Branch: `research-strategy-benchmark-v1`

Parent research state before this checkpoint: `c112a680816e06ee55a596e23805dbd3094dd513`

## Immutable boundaries

Frozen strategy: `candidate_rule_set_v2_2`

Frozen executable harness SHA256:

`b8471af989090375dec9e25daae184814674a776ab9b46b45e660e35b368be08`

Frozen prospective boundary:

`2026-09-11T20:00:00Z`

Holdout: **UNTOUCHED / NOT AUTHORIZED**.

Production was not changed by this batch. No deployment, risk, execution or trading-semantics change was made.

## Prospective shadow state

The frozen runner remains provider-recorded, immutable and fail-closed.

Valid snapshots now include:

- `2026-09-11T20:30:00Z`: 19/19 symbols; 19 entry-evaluable symbol-bars; 0 events;
- `2026-09-11T20:45:00Z` retry-2: 19/19; 38 symbol-bars; 0 events;
- `2026-09-11T21:00:00Z`: 19/19; 57 symbol-bars; 0 events;
- `2026-09-12T00:00:00Z`: 19/19; 285 symbol-bars; 11 frozen-v2.2 events; 3 eligible observations; 2 unique eligible setup families.

One earlier first-attempt `20:45Z` capture remains `INVALID_INFRASTRUCTURE` because of the original bundle-layout error. Ledger v1.1 rejects it and it is not evidence.

Latest independent evidence status:

`OBSERVATION_ONLY_LT_30_FAMILIES`

Latest `00:00Z` cycle summary SHA256:

`191ca6fccff63ead30543fc895b750054b96fa9139e9af372a2f40ef36481a46`

Latest shadow summary SHA256:

`bcdf8b5b305d5b1c61de40614c045fccafb16a79f53025af0008375fb10e48d6`

Latest prospective ledger SHA256:

`a4f04b85f9568b3f4df02fd11d2744e25176053cfee793054c346700832f5e27`

## First prospective families

All 3 eligible observations in the first non-empty snapshot are `RAYSOLUSDT LONG`.

Family `15fc0ad1...` contains two consecutive observations from one setup family:

- signal M15 open `2026-09-11T20:45:00Z`, entry `21:00Z`;
- signal M15 open `2026-09-11T21:00:00Z`, entry `21:15Z`.

Family `6aabd4ef...` contains one observation:

- signal M15 open `2026-09-11T23:00:00Z`, entry `23:15Z`.

All three had `clean_break_no_revisit=true` under the already-recorded diagnostic feature layer. This is observation only and does **not** promote that feature into the frozen rules.

## Partial outcomes as of 00:00Z

No eligible observation had reached terminal STOP or 3R TARGET by the frozen `00:00Z` cutoff.

Partial causal path diagnostics:

- first observation: MFE `2.514R`, MAE `0.027R`, still censored;
- second observation: MFE `1.836R`, MAE `0.061R`, still censored;
- third observation: MFE `0.232R`, MAE `0.638R`, still censored.

Do not label these as wins/losses before the frozen terminal rule resolves them. Same-bar terminal priority remains STOP-first; max hold remains 8h for this exact candidate.

Partial-outcome artifact SHA256:

`fab4fca86ecc26f5817318702d716e19c801080235168ee024affcee8c526185`

## Adaptive multi-profile research dataset

A separate research-only dataset was created at exact cutoff `2026-09-11T20:45:00Z`.

Purpose: FAST / future H4-H1 INTRADAY / SWING architecture research. It is explicitly **not** a v2.2 retuning dataset.

Panel: 19/19 `binance_usdm` symbols.

Per-symbol target depths:

- M5: 3000 bars;
- M15: 3000 bars;
- H1: 2000 bars;
- H4: 1000 bars;
- D1: up to 500 bars with listing-age adaptation.

D1 age-limited contracts:

- `AKEUSDT`: 350;
- `METUSDT`: 335;
- `PUMPUSDT`: 428;
- `USELESSUSDT`: 392.

All other listed intervals reached the requested caps.

Dataset summary SHA256:

`4f49f57dcd3d36939bfa56167b13a9af2ea08884fb11be66dd0f957389b3f077`

## Funding history completeness

Funding was exported from the same official Binance Futures source used by the benchmark:

`/fapi/v1/fundingRate`

Funding summary SHA256:

`c987475c7417bb8c34722e0da67ebe71909eb57a99af3be0191d02209122911f`

Completeness audit:

- symbols: 19;
- pass: 19/19;
- timestamps strictly increasing;
- every record remains within query bounds;
- maximum internal funding gap <= `8.01h`;
- tail lag to cutoff <= `8.01h`;
- listing-boundary head lag <=24h.

Status:

`PASS_WITH_LISTING_BOUNDARY_HEAD_GAPS`

The three listing-boundary head-gap symbols are:

- `AKEUSDT`;
- `METUSDT`;
- `USELESSUSDT`.

Funding completeness report SHA256:

`42e48e6452f80a940018859a072705a06dcf2551dabb7d1056b3116f7bb48d88`

This completes the historical OHLCV + funding research-data prerequisite for FAST/SWING economics work on the currently supported canonical intervals. POSITION still requires a separate W1 data contract before executable candidate research.

## Evidence governance

Primary prospective evidence unit remains the **unique resolved setup family**.

Current count: **2 unique eligible families, 0 resolved families**.

Evidence thresholds remain unchanged:

- `<30`: observation only;
- `30–49`: diagnostics;
- `50–99`: hypotheses/ablation proposals only;
- `>=100`: versioned recalibration proposal may be considered, still requiring fresh OOS/prospective evidence and explicit promotion.

Nothing in this checkpoint authorizes:

- opening holdout;
- changing v2.2 rules;
- clean-break/no-revisit hard gate;
- new VSA/volume gate;
- RR or 8h retuning;
- IOST inclusion/exclusion rule;
- production rollout.

## Next evidence action

Continue immutable frozen-v2.2 prospective capture and resolve each eligible family only after the terminal outcome is causally observable.

Hard evidence milestone remains:

`>=30 unique resolved prospective frozen-v2.2 setup families`.
