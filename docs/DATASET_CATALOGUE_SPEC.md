# Dataset Catalogue Spec v1.1

Updated: 2026-09-07

## Purpose

The K-Trader dataset catalogue provides a deterministic audit index over research artifacts. It is designed to answer one question exactly: which immutable market/context/configuration/study/outcome artifacts produced this research result?

Schema version: `ktrader.dataset_catalogue.v1`.

The catalogue is not a database of market values and does not modify any source artifact.

## Entry model

One catalogue entry represents one replay-study chain for one provider and one canonical symbol.

Required references:

- MTF bundle (`ktrader.mtf_bundle.v1`);
- universe archive (`ktrader.universe_archive.v1`);
- study cohort (`ktrader.study_cohort.v1`);
- replay study (`ktrader.replay_study.v1`);
- study-run provenance (`ktrader.study_run_provenance.v1`).

Optional reference:

- immutable binary outcome sample (`ktrader.outcome_sample.v1`).

The outcome sample is optional by design. A study with zero binary-resolved WIN/LOSS outcomes must not fabricate one merely to satisfy catalogue registration.

Each artifact reference stores:

- artifact kind;
- schema version;
- path relative to the catalogue artifact root;
- semantic identity/digest defined by that artifact contract;
- exact file/tree content SHA-256.

The catalogue entry itself has a deterministic SHA-256 `entry_id`. The catalogue has a deterministic `catalogue_sha256` over all sorted entries.

## Relationship validation

A catalogue entry is accepted only when all of the following are true:

- all artifacts remain under one explicit artifact root;
- no absolute/traversal/symlink escape is present;
- MTF bundle, universe archive, cohort, replay study and provenance use one provider;
- the replay-study symbol is present in the cohort;
- the cohort references the supplied universe archive SHA;
- the replay study references the supplied MTF bundle SHA;
- provenance references the exact study ID, bundle SHA, cohort SHA and replay-study file SHA;
- provenance context SHA equals the exact cohort context for the replay-study symbol;
- an outcome sample, when present, references the exact study ID and replay-study file SHA;
- every artifact loader's own integrity checks pass.

Catalogue verification re-opens referenced artifacts and rebuilds the entry. Stored hashes alone are not treated as sufficient evidence.

## Study-run provenance

Schema version: `ktrader.study_run_provenance.v1`.

The provenance sidecar records:

- replay study ID;
- provider and canonical symbol;
- bundle SHA-256;
- cohort SHA-256;
- exact symbol replay-context SHA-256;
- complete `RuntimeScannerConfig` SHA-256;
- `ReplayStudyConfig` SHA-256;
- exact replay-study file SHA-256;
- provenance SHA-256.

The scanner configuration is canonicalized from the complete dataclass configuration. Decimal values and UTC timestamps use deterministic textual forms. This makes configuration changes visible in provenance even when market-data artifacts are unchanged.

Canonical replay studies should use `scripts/run_replay_study.py --cohort ...`. Legacy standalone `--context` remains supported but does not produce canonical cohort-linked provenance unless the cohort relationship is known.

When an explicit study time window is intended, use UTC-only inclusive `--start` and `--end` bounds. These fields are part of `ReplayStudyConfig` and therefore part of deterministic study identity. Changing them creates a different canonical study configuration even when the selected analyzed cutoffs happen to overlap an earlier ad-hoc preflight.

## Universe archive materialization

Continuous Phase 11F capture stores immutable one-snapshot `ktrader.universe_archive.v1` files prospectively. Phase 11G study materialization may assemble a selected coherent subset into one deterministic study archive using:

```text
scripts/build_universe_archive.py
```

The builder:

- loads every source through the canonical universe-archive verifier;
- accepts one or more files/directories;
- filters by one explicit provider and optional UTC start/end bounds;
- sorts selected snapshots chronologically;
- rejects duplicate snapshot digests;
- rebuilds the combined archive with the existing canonical digest function;
- writes a new artifact without modifying Phase 11F source captures;
- reloads the written archive before reporting success.

Provider/config mixing remains invalid. `max_context_age_seconds` is a cohort/replay policy and must not be widened merely to manufacture more eligible historical windows.

## Replay-study artifact inspection

Before registration, replay-study JSONL is checked for:

- correct schema and manifest record;
- SHA-shaped study and bundle identities;
- provider/symbol consistency for every decision and outcome;
- unique decision IDs;
- consistency of analyzed-cutoff count;
- consistency of unique signal count;
- consistency of outcome counts and binary-resolved count;
- `estimated_probability` remains null at study and decision level.

The exact study-file SHA-256 is then recorded in provenance/catalogue.

## Outcome sample

Schema version: `ktrader.outcome_sample.v1`.

The outcome sample is an immutable study-specific export for later statistical work. It contains only binary-resolved `WIN` and `LOSS` records.

Before export from `OutcomeRepository`, each record must exactly equal the corresponding outcome embedded in the replay-study artifact. Missing or divergent repository rows fail closed.

The sample manifest records:

- source study ID;
- source replay-study file SHA-256;
- provider and canonical symbol;
- allowed statuses (`LOSS`, `WIN`);
- record count;
- content SHA-256.

No probability is calculated by the outcome-sample or catalogue layers.

If a study has zero eligible binary outcomes, omit `--outcome-sample` during catalogue registration and record the catalogue entry with `outcome_sample=null`.

## Operator workflow

Canonical sequence after provider-recorded data and prospective universe captures exist:

```text
1. Select and canonically assemble verified Phase 11F universe captures into one study archive.
2. Build/verify the study cohort from that archive with the approved context-age policy.
3. Build/verify a provider-recorded MTF bundle at one explicit UTC as_of.
4. Run canonical cohort-linked replay with explicit UTC start/end bounds when a bounded window is intended; emit provenance.
5. Export an immutable WIN/LOSS outcome sample only when binary-resolved outcomes actually exist.
6. Register the fully linked chain in the dataset catalogue.
7. Re-load the catalogue with artifact verification before accepting the study for later research/calibration.
```

Relevant utilities:

```text
scripts/build_universe_archive.py
scripts/build_study_cohort.py
scripts/export_mtf_history.py
scripts/run_replay_study.py
scripts/export_outcome_sample.py
scripts/build_dataset_catalogue.py
```

## First production acceptance reference

The first fully materialized production-host chain was accepted on 2026-09-07 for `binance_usdm` / `SUIUSDT`.

Canonical identities:

- universe archive SHA: `3c830d8410b913aa4b39afd8cb5be57e96a18b4a1ae4d46fa709fc11f70ccdda`;
- cohort SHA: `c63b90a1905149462e1eb31a842fff7c5f15290a7f4963107d7c8c4cf2273686`;
- MTF bundle SHA: `c0112c0d3688cddb86cabc54ae1c9da05e04ff2cef63f395b438448e3070d344`;
- replay study ID: `ebfd16b0b9059c5bd51f948d4c1b0086f4a2966a610e58dd7a6fb0d8ee474f5e`;
- provenance SHA: `08ba2378253dfa744ffbfc2fc74cae2ab6ff02264a9b60e6170d1992f6297c35`;
- catalogue entry ID: `f056dadd63c2283c07b0b2aa37b3bb2236d15e916d6fa3cf5a11fc71b38b814a`;
- catalogue SHA: `749c3aa20d02788b1c75b48e3325d854d7182f5b0729fea39dcf888af367b864`;
- outcome sample: null because the study produced zero tradable/binary-resolved signals.

Final acceptance used `load_dataset_catalogue(..., verify_artifacts=True)` and passed full artifact/cross-link reconstruction.

Detailed evidence: `docs/checkpoints/2026-09-07_PHASE11G_FIRST_PRODUCTION_CHAIN.md`.

## Tamper model

The catalogue detects changes at two layers:

- semantic artifact validation through the existing artifact loaders/digests;
- exact file/tree content SHA-256 stored in the catalogue entry.

Changing a registered file, directory member, context, cohort, replay study or sample makes verification fail. A changed artifact must be registered as a new audit chain rather than silently replacing the previous one.

## Probability guardrail

The catalogue may later index calibration results, but Phase 11G does not create such results.

Until a separately approved calibration phase establishes sufficient sample size, time-separated validation, bias handling, transaction-cost assumptions, confidence intervals and out-of-sample performance, `Setup Score` remains non-probabilistic and `estimated_probability` remains N/A/null.
