# K-Trader — Frozen v2.2 Causal Rolling Replay Acceptance

Date: 2026-09-13
Status: ACCEPTED HISTORICAL METHODOLOGY CORRECTION / PHASE 11G ACTIVE

## Scope

This checkpoint supersedes the earlier historical-inference use of Historical Expansion v1 and the first R90/R180/R365 robustness results because those runs supplied a larger H1 history to a frozen structural-space detector that scans all supplied prior H1 pivots. The resulting effective context differed from the production/prospective path.

Frozen candidate rules were not changed. The correction changes only the historical replay engine so that every historical decision is evaluated with the same bounded context available to the canonical prospective runner.

## Frozen identity

- strategy: `candidate_rule_set_v2_2`
- frozen harness SHA256: `b8471af989090375dec9e25daae184814674a776ab9b46b45e660e35b368be08`
- target: `3R`
- max hold: `32 x M15`
- same-bar ambiguity: STOP first
- fees/slippage/funding: frozen economics retained
- holdout: UNTOUCHED / NOT AUTHORIZED
- production action: false

## Corrected bounded context

Every historical decision uses:

- M15 context cap: exactly `400` closed bars once fully warmed;
- H1 context cap: exactly `300` closed bars once fully warmed;
- only information available at the historical decision timestamp;
- original frozen `signal_at()` and `level_features()` logic;
- no parameter or direction filter changes.

Global context audit:

- decision bars: `630240`;
- symbols: `19`;
- M15 min/max context: `400 / 400`;
- H1 min/max context: `300 / 300`;
- raw frozen-signal cases: `21964`.

Context-audit SHA256:

`4e7ee32542c0ec15d6e166a285fcc1252529cf73420d70d869b1c73625ec82f9`

## Prospective parity gate

Reference snapshot:

`/data/research/phase11g/v2_2_shadow_20260913T083000Z/bundles`

Parity result:

- symbols checked: `19/19`;
- M15 decision bars checked: `96 x 19 = 1824`;
- frozen signal cases: `70`;
- structural-level cases: `69`;
- mismatches: `0`;
- status: `PASS`.

Parity SHA256:

`47b03d3c7280d8cc2c7f3f73af529fb2fa89e9ccf47c8b2132d289438396effe`

## Accepted corrected historical results

All windows end strictly before the hard external cutoff `2026-09-05T14:45:00Z`.

| Window | Cohort | Completed trades | Win rate | Expectancy R | PF_R | Stress expectancy R | Stress PF_R |
|---|---:|---:|---:|---:|---:|---:|---:|
| P25 | 19 | 214 | 44.86% | +0.259415 | 1.5193 | +0.224861 | 1.4459 |
| R90 | 19 | 531 | 39.36% | +0.031637 | 1.0574 | -0.009676 | 0.9829 |
| R180 | 19 | 1073 | 39.14% | -0.013131 | 0.9761 | -0.042896 | 0.9232 |
| R365 | 17 | 2099 | 37.54% | -0.051000 | 0.9096 | -0.074531 | 0.8704 |

R365 excludes `AKEUSDT` and `METUSDT` only under the preregistered age/readiness rule, not because of performance.

Report SHA256 values:

- P25: `2056ebc0cc21b6c7bfaa2f1409eb1173d37f64f6e65fd1dfd83eb42d4212e3e5`
- R90: `a9f4d32728edf497814da5d8400166ff0c6e70312e1239d6b1d9ce360c8f7141`
- R180: `f8229a31588adee8653b4455528b832f7fd7f2426d56f41a449cec9b0d09ae1e`
- R365: `70702597daa0c50d59fe939ea1436e09fc62edcf417ff5256f73c455a0ea1faf`

Corrected result index SHA256:

`5db748737535254ac9983fa55f6c971e7198d9a6ffe80899e08f2d3ac23ea528`

## Direction diagnostics

Base results:

- P25 LONG: n=165, expectancy `+0.457787R`; SHORT: n=49, `-0.408573R`.
- R90 LONG: n=308, `+0.209006R`; SHORT: n=223, `-0.213339R`.
- R180 LONG: n=541, `+0.084231R`; SHORT: n=532, `-0.112140R`.
- R365 LONG: n=793, `-0.011860R`; SHORT: n=1306, `-0.074765R`.

These are diagnostics only. They do not authorize a LONG-only modification of frozen v2.2.

## Interpretation

The corrected evidence shows material edge decay with horizon:

`P25 +0.259R -> R90 +0.032R -> R180 -0.013R -> R365 -0.051R`.

Therefore frozen v2.2 is currently classified as a recent/regime-dependent candidate, not a historically robust long-horizon strategy. R90 is only marginally positive under base economics and becomes slightly negative under frozen stress slippage. R180 and R365 are negative under both base and stress conditions.

No in-place retuning is authorized. Any rule change must create a new preregistered candidate version and receive fresh OOS/prospective validation.

## Reproducibility

Protocol:

`docs/research/FROZEN_V2_2_CAUSAL_ROLLING_CONTEXT_REPLAY_V1_PROTOCOL.md`

Base evaluator:

`research/strategy_benchmark_v1/historical_causal_rolling_replay_v1_1.py`

Base evaluator commit:

`196df4948f292505ffdb8c7b5966781843c5c878`

Accepted runtime optimization is a lossless short-circuit applied before expensive M15 indicator calculation. It rejects only cases that the frozen rule must reject by H1 side/separation or signal-bar geometry. Prospective parity remained zero-mismatch after this optimization.

Persisted patch:

`research/strategy_benchmark_v1/patches/historical_causal_rolling_replay_v1_1_lossless_short_circuit.patch`

Patch commit:

`a90585ca4ac5068fe434b8f52767ae3f4b426b4c`

Runtime evaluator SHA256:

`c0dead4957622515a7d432d8142ac7ae8915f46e36905a5cc0e483c93e78b7e7`

Persisted patch SHA256:

`59c591d803f0656ce729b099409b73b2350392d30cb2e76dfaf64371f6e1e3bf`

## Track A continuation

A new canonical prospective capture at `2026-09-13T12:00:00Z` is accepted at the capture/ledger layer:

- panel: `19/19`;
- signal bars evaluated: `3021`;
- deduplicated events: `124`;
- eligible observations: `17`;
- unique eligible families: `12`;
- holdout: unopened;
- bundle set SHA256: `6b3f9762be7e1704d9db6dc9490b25f44e99cd79903c8511dc26b192b44843dc`;
- shadow summary SHA256: `fac14d51f33958adb2e8aab98320477a02910687a2c60b383ab329c6e80541c0`;
- ledger event-set SHA256: `39477107acb99b0a5a8b4443bbe27d10f8828c809fd5dcc29c4adfa05fcc0d78`.

The deterministic resolver for the 12:00Z state is pending because the execution channel blocked the resolver invocation before server execution. The previous accepted resolver state remains 9 resolved / 2 unresolved at 08:30Z until a fresh deterministic resolver run succeeds. Capture/ledger evidence is retained and will be resolved causally on the next permitted run.

Phase 11G remains ACTIVE. Phase 12 remains FUTURE / NOT ACTIVE.
