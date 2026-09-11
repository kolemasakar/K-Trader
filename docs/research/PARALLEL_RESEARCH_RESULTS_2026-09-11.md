# K-Trader — Parallel Research Results — 2026-09-11

Status: **DIAGNOSTIC / RESEARCH ONLY**  
Frozen strategy: `candidate_rule_set_v2_2`  
Production impact: **NONE**  
Holdout: **UNTOUCHED**

## Scope and governance

This document records the parallel work performed after v2.2 failed its pre-holdout promotion gate but showed positive non-holdout economics.

The following tracks were executed without changing frozen v2.2:

- P1 portfolio/correlation diagnostics;
- P2 execution economics;
- P3 VSA/volume features plus canonical VSA parity;
- P4 prospective/shadow infrastructure hardening;
- P5 robustness and cross-provider portability;
- P6 FAST/SWING research architecture.

All historical splits below were already visible during research. Therefore these diagnostics may generate hypotheses, but **must not be promoted into v2.2 gates using the same validation data**.

## P1 — Portfolio / correlation layer

Artifact:

`/data/research/phase11g/strategy_benchmark_v1/combined_rules/portfolio_correlation_v2_2/report.json`

SHA256:

`e3840e1314f57195e00682f29a20db6639ff567ca2c1ab3cb06454539a085de9`

Results:

- raw frozen v2.2 non-holdout trades: `37`;
- diagnostic correlated-family count: `36`;
- multi-trade diagnostic families: `1`;
- maximum diagnostic family size: `2`;
- maximum concurrent positions: `5`;
- maximum concurrent LONG positions: `5`;
- maximum concurrent SHORT positions: `1`;
- top-symbol trade share: approximately `16.2%`;
- symbol-trade HHI: approximately `0.100`;
- only material `|rho| >= 0.70` return-correlation cluster among traded symbols: `1000PEPEUSDT / DOGEUSDT / TRUMPUSDT`.

Interpretation:

- the 37-trade count is not materially inflated by this particular correlation-family definition;
- simultaneous exposure can still reach five positions and therefore portfolio-level risk is relevant;
- the diagnostic family grouping is not yet the canonical `setup_family_id` definition.

## P2 — Execution economics

Artifact:

`/data/research/phase11g/strategy_benchmark_v1/combined_rules/execution_economics_v2_2/report.json`

SHA256:

`f9af9afe82eade380ad718f198c7240c7c876f6a13bb0531bc88b4a23840183c`

Results:

- base-slippage trades: `37`;
- stress-slippage trades: `37`;
- zero-slippage trades: `36`;
- median explicit fee+funding cost: approximately `0.041R`;
- median zero-to-base full-path execution drag: approximately `0.009R`;
- median base-to-stress full-path drag: approximately `0.015R`;
- median explicit cost + zero-to-base drag: approximately `0.051R`.

Narrower executed stop-distance buckets pay materially more cost as a fraction of initial R. This is arithmetic and execution-sensitive, but the associated profitability differences are observational and must not be converted into a new min-stop hard gate from this same sample.

One base-path trade had no exact zero-slippage matched episode:

- `ARBUSDT SHORT`, entry `2026-09-09T23:45:00Z`;
- base executed risk approximately `1.267%`;
- base outcome approximately `+2.912R`.

This confirms that changing slippage can alter eligibility/path identity rather than merely subtracting a constant cost. Execution stress therefore requires full-path replay.

## P3 — VSA / volume research

### Heuristic candidate-feature layer

Artifact:

`/data/research/phase11g/strategy_benchmark_v1/combined_rules/vsa_volume_features_v2_2/report.json`

SHA256:

`9f562913c8c1affaa03b2210f8cd68bbf4a2ca5fe3bef821dd5c080780b06cb2`

Some high-volume and BC-like heuristic buckets looked positive, but development/validation behavior was not sufficiently stable and some labels were sparse. These labels remain hypotheses only.

### Canonical raw-VSA parity

Canonical source:

`src/ktrader/evidence/vsa.py` blob `26f90b3a1ca5523970ccbe7dabebdd84d9dc8d4d`.

Artifact:

`/data/research/phase11g/strategy_benchmark_v1/combined_rules/canonical_vsa_raw_v2_2/report.json`

SHA256:

`020c6a29dab4d9cdb15b6e6416f360f0fed0dec606df42a0a00166bc014dad70`

On frozen trade signal bars:

- canonical raw VSA event present in `10/37` non-holdout trades;
- the observed raw events were directionally `OPPOSING` to the trade side in this sample;
- non-holdout `OPPOSING` bucket still had positive expectancy;
- no evidence supports a rule requiring raw VSA direction to match the trade direction.

Interpretation:

Raw VSA must remain contextual. The current canonical design already requires level/regime context and later confirmation for validated VSA. Raw bar labels alone must not be used as an entry gate.

## Canonical level-clustering parity

Canonical sources:

- `structure/pivots.py` blob `2fd673027fa660fa20cacf7e566f6736e7baf86b`;
- `structure/levels.py` blob `de25e3e764623c0361e334f89ffa0abbd5961e75`.

Artifact:

`/data/research/phase11g/strategy_benchmark_v1/combined_rules/canonical_level_parity_v2_2/report.json`

SHA256:

`82298b60fdfb9983ce2894605e6c02d60a3bb84fb6c7ce96993d9305e789238c`

Using only the canonical static `radius=2`, `0.15 ATR`, `2 touches` clustering semantics:

- canonical static clustering classified `35/37` non-holdout trades as open-space;
- Level Context v2 classified only `22/37` as H1 open-space.

Therefore the useful discrimination seen in Level Context v2 is not reproduced by simply substituting the current canonical static cluster detector. The richer touch/context representation remains a separate research layer.

This parity audit intentionally does not reconstruct the full canonical BROKEN/MIRROR lifecycle.

## P4 — Prospective infrastructure

Implemented:

- immutable fixed-panel provider-recorded bundle capture;
- exact frozen-harness SHA verification;
- protocol SHA verification;
- per-run bundle provenance;
- setup-family IDs;
- Level Context diagnostic features recorded without affecting eligibility;
- ledger de-duplication;
- invalid-snapshot rejection;
- fail-closed cycle status.

Frozen boundary:

`2026-09-11T20:00:00Z`

### Valid snapshot 1

As-of:

`2026-09-11T20:30:00Z`

- panel: `19/19`;
- causally entry-evaluable symbol-bars: `19`;
- frozen v2.2 events: `0`;
- eligible families: `0`.

### Invalid infrastructure attempt

As-of `20:45Z`, first canonical-runner attempt wrote multiple bundles to a shared path. The capture correctly returned 19 missing symbols. This run is explicitly marked:

`INVALID_INFRASTRUCTURE`

and is rejected by the prospective ledger.

It is not evidence.

### Valid snapshot 2

As-of:

`2026-09-11T20:45:00Z`

Run:

`/data/research/phase11g/v2_2_shadow_20260911T204500Z_r2`

- panel: `19/19`;
- causally entry-evaluable symbol-bars: `38`;
- signal range: `20:00` through `20:15` M15 open times;
- frozen v2.2 events: `0`;
- eligible families: `0`;
- frozen harness SHA unchanged.

Cycle summary SHA256:

`0003e2ebe803da64e641ecd86367474dbb8db1a987056573b03114f06ba7b34b`

Shadow summary SHA256:

`f99c08fb7d4cda584e3b1a06e8cd9b5161eee200f7b61e77460c6f9fa5352cee`

Ledger SHA256:

`389c6a4a0c2c0210e49a80c415866260ba9f06e02c8f98aefe4f426a4bf2c2f8`

Current independent-evidence state:

`NO_ELIGIBLE_FAMILIES_YET`

## P5 — robustness

Artifact:

`/data/research/phase11g/strategy_benchmark_v1/combined_rules/robustness_v2_2/report.json`

SHA256:

`7edb61d440697c543557f0b7d7f1cb8bb060366b0b901fed9c7ceb66db4d18f1`

This is **not independent OOS**. It is stability/concentration analysis of already-seen non-holdout data.

Chronological quartiles remain mixed but mostly positive. Five-day block bootstrap remained positive at its lower expectancy quantile, but five UTC days are far too few for an independence claim.

Material single-symbol warning:

- `IOSTUSDT` contributed four winning trades with unusually high mean R;
- removing `IOSTUSDT` leaves non-holdout expectancy positive but reduces it from approximately `+0.289R` to approximately `+0.046R`;
- PF falls to approximately `1.079`;
- WR falls to approximately `39.4%`.

Therefore current historical economics are materially dependent on one symbol contribution even though removing it does not flip expectancy negative.

Independent frozen prospective validation remains:

`WAITING_FOR_FRESH_FROZEN_SHADOW_FAMILIES`.

## P5 — cross-provider portability

Bybit supports `16/19` fixed-panel symbols. Missing:

- `PUMPUSDT`;
- `RAYSOLUSDT`;
- `VTHOUSDT`.

A synchronized `2026-09-11T20:45:00Z` Binance-vs-Bybit portability audit was run on the fixed 16-symbol intersection.

Artifact:

`/data/research/phase11g/strategy_benchmark_v1/combined_rules/cross_provider_portability_v2_2_20260911T204500Z/report.json`

SHA256:

`51a00dacda57602fe981dac5388dbe6127e0530784bb07345f83d183e42bb7e6`

Results:

- common symbols: `16`;
- median symbol M15 return correlation: `0.9984`;
- median symbol absolute close basis: approximately `4.32 bps`;
- Binance post-freeze frozen decision events: `0`;
- Bybit post-freeze frozen decision events: `0`.

This supports short-window data portability only. It is not profitability validation and cannot replace prospective outcome evidence.

## P6 — horizon-profile architecture

Research specification:

`docs/research/PROFILE_RESEARCH_SPECS_FAST_SWING_V0.md`

Initial research envelopes:

- FAST: H1/M15 context, M15 setup, M5 trigger, approximately up to 4h;
- SWING: D1/H4 context, H1 trigger, approximately 2–4 days;
- POSITION: architecture-reserved W1/D1 -> H4, approximately 7–21 days.

No INTRADAY v2.2 threshold is automatically inherited into another profile.

The earlier `docs/TRADING_HORIZON_PROFILES.md` remains the source for the already-accepted production FAST TTL and earlier lifecycle studies. The new research profile document does not silently rename or modify production profile contracts.

## Combined conclusions

1. Frozen v2.2 remains the strongest current INTRADAY research candidate, but still fails promotion gates.
2. Portfolio correlation does not materially reduce 37 historical trades to a much smaller family count under the current diagnostic grouping, although concurrent exposure reaches five positions.
3. Execution costs are material at approximately `~0.05R` median when explicit costs and base execution drag are combined.
4. Current historical expectancy is materially supported by IOSTUSDT and therefore lacks strong symbol-robustness evidence.
5. Raw VSA cannot be used as a mandatory directional gate.
6. Level Context v2 contains information not reproduced by the current simple canonical static cluster detector.
7. True independent evidence is still prospective and currently contains zero eligible frozen-v2.2 families.
8. No threshold, feature, profile or management rule is promoted by these diagnostics.

## Next evidence boundary

Continue immutable prospective shadow capture under exact v2.2 rules.

Do not change frozen parameters until the prospective family count reaches the applicable evidence gate. Research on new strategy versions may continue separately, but any post-hoc hypothesis derived here must start a new version/evidence cycle rather than modifying v2.2 in place.
