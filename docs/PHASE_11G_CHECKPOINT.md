# Phase 11G Checkpoint - Dataset Catalogue Expansion and Corrected Historical Discovery

Updated: 2026-09-08

Status: VERIFIED FOUNDATION / TWO PRODUCTION CHAINS CATALOGUED / CORRECTED DISCOVERY ACTIVE / RR-GEOMETRY AUDIT NEXT.

## Foundation

Phase 11G retains the deterministic `ktrader.dataset_catalogue.v1` research audit chain linking one coherent provider/symbol dataset through:

- `ktrader.mtf_bundle.v1`;
- `ktrader.universe_archive.v1`;
- `ktrader.study_cohort.v1`;
- `ktrader.replay_study.v1`;
- `ktrader.study_run_provenance.v1`;
- optional immutable `ktrader.outcome_sample.v1`.

Catalogue verification reopens and validates source artifacts and relationships rather than trusting stored hashes alone. Paths remain constrained to the artifact root; provider/symbol/context/study identities are cross-checked fail-closed.

`Setup Score` remains deterministic and non-probabilistic. `estimated_probability` remains null/N/A. Immutable outcome samples remain WIN/LOSS-only and are not created when no binary outcomes exist.

## Canonical operator tooling

Current utilities include:

- `scripts/build_universe_archive.py`;
- `scripts/build_study_cohort.py`;
- `scripts/export_mtf_history.py`;
- `scripts/run_replay_study.py`;
- `scripts/export_outcome_sample.py`;
- `scripts/build_dataset_catalogue.py`.

Replay bounds are part of canonical `ReplayStudyConfig` and therefore part of deterministic study identity.

## Repository verification history

Original Phase 11G foundation:

- PR #10 CI run `32657337221`: repository-wide pytest 163 PASS, compile/shell PASS, amd64/arm64 Docker/runtime PASS;
- squash merge `96de78d503432122d98e1c9ad1f01299802862a8`.

Production-readiness work completed on 2026-09-07:

- PR #27 fixed the fresh-process replay import cycle;
- PR #28 exposed canonical inclusive UTC replay `--start` / `--end` bounds;
- PR #29 added the reproducible universe-archive builder CLI;
- PR #30 documented the first production chain.

Capture cadence hardening:

- PR #32 changed research-capture scheduling from elapsed-time drift to UTC-slot semantics;
- accepted pre-contract-fix main SHA: `095610463a500c711f1cdaa6cf91bdcdfc333cbd`.

Side/regime contract correction:

- PR #33: `Fix Phase 11G side-to-regime scoring contract`;
- canonical main SHA before this documentation checkpoint: `7fa20c3d7f0d89ae628eb2bf21e4c50164eb3eab`;
- post-merge Tests run `34177001398`: PASS;
- post-merge CI run `34177001482`: pytest PASS, Docker amd64 PASS, Docker arm64 PASS;
- Deploy Production #9 run `34177978988`: SUCCESS;
- deployed image: `k-trader:7fa20c3d7f0d89ae628eb2bf21e4c50164eb3eab`;
- container health, provider REST/WS, MTF API and Phase 10 Action live acceptance: PASS.

## Strict research policy

The active Phase 11G policy remains:

- production provider scope: `binance_usdm`;
- `max_context_age_seconds=300`;
- historical context membership uses the newest snapshot at or before each cutoff;
- no historical rank/context reconstruction from current data;
- no freshness widening merely to create eligible samples;
- MTF depths: `1d=300`, `4h=300`, `1h=300`, `15m=300`, `5m=400`;
- full-engine replay before writes;
- no zero-signal materialization merely to grow the catalogue;
- no synthetic outcomes;
- outcome samples only when actual binary WIN/LOSS outcomes exist;
- no probability calibration;
- no Phase 12 expansion while the current discovery/geometry gate is unresolved.

## Current canonical dataset catalogue

Path:

`/data/research/phase11g/catalogue.json`

State:

- schema: `ktrader.dataset_catalogue.v1`;
- entry count: `2`;
- catalogue SHA: `057ff750966d2bc5043fffd7fdc37583dd0133480452c131b51f84109d2fb4b6`;
- prior final `load_dataset_catalogue(..., verify_artifacts=True)`: PASS.

No catalogue writes occurred during the corrected historical-discovery work.

### Chain #1 — SUIUSDT

- provider: `binance_usdm`;
- root: `/data/research/phase11g/binance_usdm/SUIUSDT/20260905T144500Z_160000Z`;
- replay: `2026-09-05T14:45Z` through `16:00Z`;
- universe archive SHA: `3c830d8410b913aa4b39afd8cb5be57e96a18b4a1ae4d46fa709fc11f70ccdda`;
- cohort SHA: `c63b90a1905149462e1eb31a842fff7c5f15290a7f4963107d7c8c4cf2273686`;
- bundle SHA: `c0112c0d3688cddb86cabc54ae1c9da05e04ff2cef63f395b438448e3070d344`;
- study ID: `ebfd16b0b9059c5bd51f948d4c1b0086f4a2966a610e58dd7a6fb0d8ee474f5e`;
- provenance SHA: `08ba2378253dfa744ffbfc2fc74cae2ab6ff02264a9b60e6170d1992f6297c35`;
- catalogue entry ID: `f056dadd63c2283c07b0b2aa37b3bb2236d15e916d6fa3cf5a11fc71b38b814a`;
- analyzed cutoffs: `15`;
- unique tradable signals: `0`;
- binary outcomes: `0`;
- outcome sample: `null`.

### Chain #2 — XRPUSDT

- provider: `binance_usdm`;
- root: `/data/research/phase11g/binance_usdm/XRPUSDT/20260905T144500Z_160000Z`;
- replay: `2026-09-05T14:45Z` through `16:00Z`;
- universe archive SHA: `3c830d8410b913aa4b39afd8cb5be57e96a18b4a1ae4d46fa709fc11f70ccdda`;
- cohort SHA: `f417e64f9c2a31916564037709554971035adbb14054a3f83b2b76261e2ee58c`;
- bundle SHA: `8b276ab7d8ffa5614c38759a7fbccdf3fdf27c855e4460b04f8e4693b8b090af`;
- study ID: `886d2a5c136af427657d005655d3b654b046dd9ede19b922390bb403fbe60c80`;
- provenance SHA: `6397ce7c1786d1ebb5d1e11f297995c3b3c68abb2a44476a29c994164bfcff65`;
- catalogue entry ID: `4788384b5268ae8062eaa1a225de8d54cbd12e59e17ea3905d702ed5545a8eef`;
- analyzed cutoffs: `15`;
- unique tradable signals: `0`;
- binary outcomes: `0`;
- outcome sample: `null`.

## Historical discovery windows

Four read-only provider-recorded windows were scanned before the side/regime defect was corrected:

- Window #1: `2026-09-07T18:55Z` through `20:10Z`, 40 MTF-passing symbol-window runs;
- Window #2: `20:15Z` through `21:30Z`, 42 MTF-passing runs;
- Window #3: `21:35Z` through `22:50Z`, archive SHA `b511599cce4116aa1cd93f07e1836ab5a4ce19e2750b07f27b372cf4c9b002ff`, 41 MTF-passing runs;
- Window #4: `22:55Z` through `00:10Z`, archive SHA `bed603828a997570149f01d42e7a979d96eb6ff0247c68f045b7e65bbe2c0477`, 40 MTF-passing runs.

The original aggregate zero-signal conclusion across these windows is compromised as evidence of natural signal absence because the rejection funnel found a deterministic scoring vocabulary mismatch.

The windows remain useful evidence for provider-recorded context, deep-history and deterministic replay mechanics.

## PR #33 root cause and fix

Pre-fix Window #4 funnel:

- analyzed cutoffs: `600`;
- candidate decisions: `7596`;
- `NO_TRADE`: `7596`;
- grade C: `7596`;
- `HTF_CONTEXT_MISMATCH`: `7596/7596` = 100%.

Root cause:

- candidate direction vocabulary: `LONG` / `SHORT`;
- canonical MTF regime vocabulary: `BULLISH` / `BEARISH` / `RANGE` / `MIXED`;
- direct equality made valid directional alignment impossible.

PR #33 introduced:

- `LONG -> BULLISH`;
- `SHORT -> BEARISH`;
- aligned `context_strength()` fallback with canonical MTF semantics so 4h+1h cannot override directionally opposite D1; lower-timeframe fallback applies only when D1 is non-directional.

## Corrected Window #4 validation

The corrected read-only replay used the deployed `7fa20c3...` engine and newest-snapshot-at/before-cutoff semantics.

Preflight/result:

- archive SHA: `bed603828a997570149f01d42e7a979d96eb6ff0247c68f045b7e65bbe2c0477`;
- selected snapshots: `16`;
- context ages: approximately 259–260 seconds, within the 300-second policy;
- strict symbols: `45`;
- MTF passed: `40`;
- MTF rejected: `5`;
- analyzed cutoffs: `600`;
- total candidate decisions: `7596`;
- HTF rejected: `7161`;
- HTF aligned: `435`;
- tradable decisions: `0`;
- unique tradable signals: `0`.

Deep-history rejects:

- CFGUSDT: 176/300 daily bars;
- MARSCOINUSDT: 7/300;
- PIEVERSEUSDT: 298/300;
- PONSUSDT: 2/300;
- 牛来USDT: 9/300.

PR #33 is therefore historically replay-validated: 435 candidates now pass the formerly impossible HTF direction gate.

## Conditional 435-candidate audit

Reference reproduction:

- `htf_aligned_candidates=435`;
- `reference_aligned_candidates=435`;
- `reference_match=true`;
- all aligned candidates: `LONG -> BULLISH`;
- no aligned SHORT sample in this window.

Independent aligned hard reasons:

- `PRIMARY_LEVEL_NOT_STRONG`: 233;
- `RR_BELOW_3`: 271;
- `INVALID_GEOMETRY`: 87;
- `ATR_USED_OVER_80`: 68.

Sequential funnel:

```text
435 HTF aligned
  -> 202 after primary level strength
  -> 168 after valid geometry
  -> 142 after ATR <= 80%
  ->   0 after RR >= 3
```

All 142 candidates reaching the final RR gate were rejected only by `RR_BELOW_3`. No unexpected hard-reject reason remained.

Examples show high raw scores can still be correctly blocked by hard geometry/RR rules, including WLDUSDT raw score 90 with only `RR_BELOW_3` and RR 0.225. This is not evidence for lowering the threshold.

## Current gate

The next task is a read-only RR-geometry audit of the 142 RR-only candidates.

Audit entry/stop/target construction, risk and reward distances, target level identity/type/timeframe, RR distribution and repeated unchanged setup geometry across neighboring cutoffs. Deduplicate geometry-equivalent observations before interpreting the distribution.

Do not change the `RR >= 3` threshold until this audit distinguishes genuine market conditions from any target-selection or geometry-construction bias.

After geometry is understood, rerun corrected discovery for historical Windows #1–#4 and materialize only naturally useful deterministic chains. Catalogue verification remains mandatory after any future registration.

Detailed current recovery state:

`docs/checkpoints/2026-09-08_PHASE11G_CORRECTED_REPLAY_RR_GEOMETRY_GATE.md`

Phase 12 multi-provider expansion remains future work.
