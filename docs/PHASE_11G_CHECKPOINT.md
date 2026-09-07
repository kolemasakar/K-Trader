# Phase 11G Checkpoint - Dataset Catalogue Foundation and Production Dataset Expansion

Updated: 2026-09-07

Status: VERIFIED REPOSITORY-SIDE / TWO PRODUCTION CHAINS COMPLETE, VERIFIED AND CATALOGUED.

## Foundation implemented

- deterministic audit catalogue schema `ktrader.dataset_catalogue.v1`;
- one catalogue entry links one coherent provider/symbol research chain:
  - `ktrader.mtf_bundle.v1`;
  - `ktrader.universe_archive.v1`;
  - `ktrader.study_cohort.v1`;
  - `ktrader.replay_study.v1`;
  - `ktrader.study_run_provenance.v1`;
  - optional immutable `ktrader.outcome_sample.v1`;
- every registered artifact carries both its semantic identity/digest and an exact file/tree content SHA-256;
- catalogue entry ID and catalogue SHA-256 are deterministic from the complete registered relationship graph;
- artifact paths are stored relative to one explicit artifact root; absolute paths, path traversal and symlink escapes are rejected;
- catalogue load can re-open and re-validate every referenced artifact, not only trust stored hashes;
- provider, canonical symbol, bundle, archive, cohort, context, study and outcome relations are cross-checked fail-closed;
- replay-study inspection validates manifest/decision/outcome identity, counts, duplicate decision IDs and keeps `estimated_probability=null`;
- canonical replay runs using `--cohort` emit a separate versioned study-run provenance sidecar;
- provenance records SHA-256 for the exact replay study file, bundle, cohort, symbol context, complete `RuntimeScannerConfig` and `ReplayStudyConfig`;
- immutable binary outcome sample export validates that WIN/LOSS rows in `OutcomeRepository` exactly match replay-study embedded outcomes before writing the sample;
- non-binary outcomes are excluded from the immutable calibration sample by contract.

## Canonical operator tooling

Current canonical utilities include:

- `scripts/build_universe_archive.py` — assemble immutable Phase 11F one-snapshot capture files/directories into one verified chronological same-provider archive, with UTC start/end filtering, duplicate-digest rejection and post-write canonical reload;
- `scripts/build_study_cohort.py` — derive timestamped symbol contexts from a verified archive;
- `scripts/export_mtf_history.py` — materialize provider-recorded MTF history at an explicit `as_of`;
- `scripts/run_replay_study.py` — canonical cohort-linked replay with provenance and inclusive UTC `--start` / `--end` study bounds;
- `scripts/export_outcome_sample.py` — optional immutable WIN/LOSS-only sample export when binary outcomes actually exist;
- `scripts/build_dataset_catalogue.py` — register and re-verify a fully linked chain.

Replay window bounds are part of the canonical `ReplayStudyConfig` and therefore part of deterministic study identity. Do not compare a pre-window-CLI in-memory study ID with a final bounded canonical study ID as if they were the same configuration.

## Canonical audit chain

```text
provider-recorded MTF bundle SHA
        |
        +-> universe archive SHA
              |
              +-> study cohort SHA
                    |
                    +-> exact symbol replay-context SHA
                          |
                          +-> scanner-config SHA
                          +-> study-config SHA
                          |
                          +-> replay-study ID + file SHA
                                |
                                +-> optional immutable WIN/LOSS outcome-sample SHA
                                      |
                                      +-> dataset-catalogue entry SHA
                                            |
                                            +-> catalogue SHA
```

A catalogue is an integrity and reproducibility index. It does not edit, repair, interpolate or synthesize market/context/outcome artifacts.

## Repository verification history

Original Phase 11G foundation verification:

- PR #10 CI run `32657337221`;
- repository-wide pytest: **163 passed, 1 dependency deprecation warning**;
- compile/shell PASS;
- linux/amd64 Docker/runtime PASS;
- linux/arm64 QEMU/Buildx image/architecture/runtime PASS;
- PR #10 squash merge: `96de78d503432122d98e1c9ad1f01299802862a8`.

Production-readiness fixes completed on 2026-09-07:

- PR #27 fixed the fresh-process replay import cycle;
- PR #28 exposed canonical inclusive UTC replay `--start` / `--end` bounds;
- PR #29 added the reproducible universe-archive builder CLI;
- accepted code/runtime SHA: `b75b1e3d74b5834e7c404555caa6bdf34f87fe12`;
- post-merge CI run `34139445282`: pytest PASS, Docker amd64 PASS, Docker arm64 PASS;
- post-merge Tests run `34139445313`: PASS;
- Deploy Production #7 run `34139956047`: SUCCESS.

First-chain documentation checkpoint:

- PR #30 squash merge: `40cee9b17aa74ad45be1894d566ddb79f8a81ef4`;
- post-merge Tests run `34144783877`: PASS;
- post-merge CI run `34144783943`: pytest PASS, Docker amd64 PASS, Docker arm64 PASS;
- this docs-only commit did not require production redeployment; deployed runtime remains `b75b1e3d74b5834e7c404555caa6bdf34f87fe12`.

## Production accumulation / eligibility state

Continuous Phase 11F production capture remains active and immutable under `/data/research/universe`.

The strict replay context policy remains `max_context_age_seconds=300` and was not widened.

Latest read-only eligibility scan before the second chain reported:

- provider: `binance_usdm`;
- source files: `749` at scan time;
- invalid files: `0`;
- universe config: `USDT`, price limit enabled, max price `3`, max candidates `50`;
- selected unique snapshots: `749`;
- symbols seen: `90`;
- strict-policy eligible symbols: `45`;
- eligible non-SUI symbols: `44`;
- required candidate window: `16` cutoffs;
- maximum observed context age in the selected window: `286.386` seconds.

The highest-ranked next candidate, `MARSCOINUSDT`, failed deep-history preflight because only 4 daily bars were available versus the required 300. The next candidate, `XRPUSDT`, passed the canonical MTF depth preflight and was selected for chain #2.

## Common production study window

Both accepted chains use the same strict provider/context window:

- provider: `binance_usdm`;
- universe archive first selected capture: `2026-09-05T14:40:13.613625Z`;
- universe archive last selected capture: `2026-09-05T15:59:13.890630Z`;
- snapshot count: `16`;
- replay start: `2026-09-05T14:45:00Z`;
- replay end: `2026-09-05T16:00:00Z`;
- `step_bars=1`;
- `horizon_bars=None`;
- MTF bundle `as_of=2026-09-05T18:15:00Z`;
- canonical depth: `1d=300`, `4h=300`, `1h=300`, `15m=300`, `5m=400`.

The common universe archive SHA is:

`3c830d8410b913aa4b39afd8cb5be57e96a18b4a1ae4d46fa709fc11f70ccdda`

The shared archive identity is expected because both studies use the exact same immutable provider/config/time-window captures.

## Production chain #1 — SUIUSDT

Materialized root:

`/data/research/phase11g/binance_usdm/SUIUSDT/20260905T144500Z_160000Z`

Verified identities:

- cohort SHA: `c63b90a1905149462e1eb31a842fff7c5f15290a7f4963107d7c8c4cf2273686`;
- MTF bundle SHA: `c0112c0d3688cddb86cabc54ae1c9da05e04ff2cef63f395b438448e3070d344`;
- replay study ID: `ebfd16b0b9059c5bd51f948d4c1b0086f4a2966a610e58dd7a6fb0d8ee474f5e`;
- provenance SHA: `08ba2378253dfa744ffbfc2fc74cae2ab6ff02264a9b60e6170d1992f6297c35`;
- catalogue entry ID: `f056dadd63c2283c07b0b2aa37b3bb2236d15e916d6fa3cf5a11fc71b38b814a`.

Replay result:

- analyzed cutoffs: `15`;
- skipped insufficient history: `0`;
- skipped missing context: `0`;
- unique tradable signals: `0`;
- outcome counts: `{}`;
- binary resolved: `0`;
- `estimated_probability=null`;
- outcome sample: `null`.

Detailed first-chain evidence: `docs/checkpoints/2026-09-07_PHASE11G_FIRST_PRODUCTION_CHAIN.md`.

## Production chain #2 — XRPUSDT

Materialized root:

`/data/research/phase11g/binance_usdm/XRPUSDT/20260905T144500Z_160000Z`

Verified identities:

- cohort SHA: `f417e64f9c2a31916564037709554971035adbb14054a3f83b2b76261e2ee58c`;
- MTF bundle SHA: `8b276ab7d8ffa5614c38759a7fbccdf3fdf27c855e4460b04f8e4693b8b090af`;
- replay study ID: `886d2a5c136af427657d005655d3b654b046dd9ede19b922390bb403fbe60c80`;
- provenance SHA: `6397ce7c1786d1ebb5d1e11f297995c3b3c68abb2a44476a29c994164bfcff65`;
- catalogue entry ID: `4788384b5268ae8062eaa1a225de8d54cbd12e59e17ea3905d702ed5545a8eef`.

Replay result:

- analyzed cutoffs: `15`;
- skipped insufficient history: `0`;
- skipped missing context: `0`;
- unique tradable signals: `0`;
- outcome counts: `{}`;
- binary resolved: `0`;
- `estimated_probability=null`;
- outcome sample: `null`.

## Current dataset catalogue acceptance

Current path:

`/data/research/phase11g/catalogue.json`

Accepted catalogue state:

- schema: `ktrader.dataset_catalogue.v1`;
- entry count: `2`;
- current catalogue SHA: `057ff750966d2bc5043fffd7fdc37583dd0133480452c131b51f84109d2fb4b6`;
- SUI entry ID: `f056dadd63c2283c07b0b2aa37b3bb2236d15e916d6fa3cf5a11fc71b38b814a`;
- XRP entry ID: `4788384b5268ae8062eaa1a225de8d54cbd12e59e17ea3905d702ed5545a8eef`;
- outcome samples: both `null`.

Historical note: the earlier one-entry catalogue SHA `749c3aa20d02788b1c75b48e3325d854d7182f5b0729fea39dcf888af367b864` remains the accepted identity of the first-chain checkpoint but is no longer the current catalogue SHA after XRP registration.

Final acceptance used `load_dataset_catalogue(..., verify_artifacts=True)` and returned PASS with `entry_count=2`. The canonical loader therefore accepted the physical artifact relationships for both registered chains.

Detailed two-chain recovery state: `docs/checkpoints/2026-09-07_PHASE11G_TWO_CHAIN_DATASET_CHECKPOINT.md`.

## Trading / probability guardrails

Phase 11G does not change Trading Engine setup discovery, RR, ATR-used, VSA/Trap, scoring, grading, signal eligibility or execution behavior.

`Setup Score` remains a deterministic rule score and is not statistical probability. `estimated_probability` remains null/N/A.

Do not fabricate an outcome sample when a replay has no binary WIN/LOSS outcomes.

## Remaining work

The next task is dataset expansion through read-only batch discovery rather than manually materializing every eligible zero-signal symbol:

- continue real Oracle-host prospective market/universe capture;
- scan eligible provider-recorded symbols/windows under the unchanged 300-second context-age policy;
- require canonical deep MTF history before study materialization;
- run full-engine replay in memory to identify symbols/windows with naturally occurring tradable signals/outcomes;
- materialize and catalogue only coherent useful candidates;
- export immutable WIN/LOSS outcome samples only when binary-resolved outcomes actually exist;
- always re-load the catalogue with artifact verification after registration;
- continue target-host persistence/backup/restart/disk-guard/watchdog evidence accumulation;
- perform statistical calibration only after a separately approved methodology, sufficient sample size and time-separated out-of-sample validation.

Phase 12 multi-provider expansion remains future work.
