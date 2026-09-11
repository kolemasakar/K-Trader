# CHECKPOINT — v2.2 Parallel Research Batch — 2026-09-11

Status: **COMPLETE FOR CURRENT DATA / WAITING FOR FRESH PROSPECTIVE FAMILIES**

Parent research HEAD before this checkpoint document:

`a741141e0f50ccb32b9b45e2272f108717fc5703`

Branch:

`research-strategy-benchmark-v1`

## Immutable boundaries

Frozen candidate:

`candidate_rule_set_v2_2`

Frozen executable harness SHA256:

`b8471af989090375dec9e25daae184814674a776ab9b46b45e660e35b368be08`

Frozen prospective boundary:

`2026-09-11T20:00:00Z`

Holdout:

`UNTOUCHED / NOT AUTHORIZED`

Production:

- deployed SHA `81b79b281a4cc330b7c11058d202e0d74fb6d70e`;
- health `ok`;
- mode `read_only`;
- data_ready `true`;
- provider `binance_usdm`;
- no deployment/risk/execution/trading-semantics changes made by this batch.

## Completed research tracks

### Level / path diagnostics

Completed before and during this batch:

- Level Context Layer v2;
- Level Context v2.1 strict-break diagnostics;
- broken-level traversal lifecycle;
- MFE/MAE stages 1–3;
- canonical static-level clustering parity.

Strongest post-hoc structural hypothesis remains:

`clean break -> no revisit before entry`

It is **not** a frozen-v2.2 gate.

### P1 Portfolio/correlation

Report SHA256:

`e3840e1314f57195e00682f29a20db6639ff567ca2c1ab3cb06454539a085de9`

Key facts:

- 37 raw trades -> 36 diagnostic correlation families;
- only one multi-trade family under the current definition;
- maximum concurrent positions = 5;
- top-symbol trade share ~16.2%;
- main high-correlation traded-symbol cluster = 1000PEPE/DOGE/TRUMP.

### P2 Execution economics

Report SHA256:

`f9af9afe82eade380ad718f198c7240c7c876f6a13bb0531bc88b4a23840183c`

Key facts:

- median explicit cost ~0.041R;
- median base execution drag ~0.009R;
- median combined explicit+base execution burden ~0.051R;
- stress adds another ~0.015R median full-path drag;
- one zero-slippage path no longer mapped one-to-one to the frozen base path, confirming that execution changes can alter path identity.

No new min-risk threshold is authorized from these diagnostics.

### P3 VSA / volume

Heuristic feature report SHA256:

`9f562913c8c1affaa03b2210f8cd68bbf4a2ca5fe3bef821dd5c080780b06cb2`

Canonical raw-VSA parity SHA256:

`020c6a29dab4d9cdb15b6e6416f360f0fed0dec606df42a0a00166bc014dad70`

Raw canonical VSA does not support a mandatory directional-match gate. VSA remains contextual and strategy-dependent.

### Canonical level parity

Report SHA256:

`82298b60fdfb9983ce2894605e6c02d60a3bb84fb6c7ce96993d9305e789238c`

Canonical static swing clustering saw open-space on 35/37 non-holdout trades. Level Context v2 saw H1 open-space on 22/37. Therefore the richer Level Context research is not a trivial copy of the existing static cluster implementation.

### P4 Prospective infrastructure

Implemented:

- canonical provider-recorded panel export;
- immutable run roots;
- exact harness/protocol hash capture;
- invalid-run fail-closed status;
- invalid snapshot rejection in ledger;
- event/family de-duplication.

Valid snapshots:

1. `2026-09-11T20:30:00Z`: 19/19 symbols, 19 evaluable symbol-bars, 0 events.
2. `2026-09-11T20:45:00Z` retry-2: 19/19 symbols, 38 evaluable symbol-bars, 0 events.

One first-attempt 20:45 run is explicitly `INVALID_INFRASTRUCTURE` due bundle-layout error and is excluded by the ledger.

Valid 20:45 cycle summary SHA256:

`0003e2ebe803da64e641ecd86367474dbb8db1a987056573b03114f06ba7b34b`

Valid 20:45 shadow summary SHA256:

`f99c08fb7d4cda584e3b1a06e8cd9b5161eee200f7b61e77460c6f9fa5352cee`

Current prospective ledger SHA256:

`389c6a4a0c2c0210e49a80c415866260ba9f06e02c8f98aefe4f426a4bf2c2f8`

Independent evidence status:

`NO_ELIGIBLE_FAMILIES_YET`

### P5 Robustness

Report SHA256:

`7edb61d440697c543557f0b7d7f1cb8bb060366b0b901fed9c7ceb66db4d18f1`

Material warning:

Removing IOSTUSDT reduces historical non-holdout expectancy from ~+0.289R to ~+0.046R and PF to ~1.079. This is a material single-symbol contribution and weakens current robustness confidence.

The robustness report is not independent OOS evidence.

### P5 Cross-provider portability

Bybit supports 16/19 fixed-panel symbols. Missing:

- PUMPUSDT;
- RAYSOLUSDT;
- VTHOUSDT.

Synchronized 20:45Z 16-symbol comparison:

- median M15 return correlation ~0.9984;
- median absolute close basis ~4.32 bps;
- Binance frozen events = 0;
- Bybit frozen events = 0.

Report SHA256:

`51a00dacda57602fe981dac5388dbe6127e0530784bb07345f83d183e42bb7e6`

This proves only short-window data/signal portability, not profitability portability.

### P6 Profile research architecture

Created:

`docs/research/PROFILE_RESEARCH_SPECS_FAST_SWING_V0.md`

Research envelopes:

- FAST: H1/M15 -> M5, approximately <=4h;
- SWING: D1/H4 -> H1, approximately 2–4 days;
- POSITION: W1/D1 -> H4, architecture reserved.

These do not alter the existing production FAST TTL contract or earlier lifecycle-profile documentation.

## Promotion status

Frozen v2.2 remains:

`PREHOLDOUT GATE FAIL`

Nothing in this checkpoint overrides:

- non-holdout sample <100;
- validation sample <30;
- non-holdout WR <50%;
- validation WR <50%;
- holdout not authorized.

## What may continue now

Safe ongoing work:

- immutable prospective shadow captures;
- provenance/ledger hardening;
- observation-only logging of Level Context/VSA/volume/execution features;
- separate FAST/SWING architecture and data-readiness work;
- portfolio exposure modelling that does not alter v2.2 decisions.

## What must wait for new evidence

Do not promote or retune from the current seen data:

- clean-break/no-revisit gate;
- early-progress exit/management rule;
- new risk-distance threshold;
- volume/VSA gate;
- IOST inclusion/exclusion rule;
- different 3R/8h parameters.

These require a new preregistered strategy version and fresh OOS/prospective evidence.

## Next hard evidence milestone

First milestone:

`>=30 unique resolved prospective frozen-v2.2 setup families`

Until then prospective v2.2 evidence remains observation-only.
