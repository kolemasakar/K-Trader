# Dataset Catalogue Spec v1.0

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

## Operator workflow

Canonical sequence after provider-recorded data and prospective universe captures exist:

```text
1. Build/verify an MTF bundle.
2. Build/verify a universe archive and study cohort.
3. Run replay using the cohort context and produce study provenance.
4. Export an immutable WIN/LOSS outcome sample from OutcomeRepository.
5. Register the chain in the dataset catalogue.
6. Re-load the catalogue with artifact verification before using the study in later research/calibration.
```

Relevant utilities:

```text
scripts/run_replay_study.py
scripts/export_outcome_sample.py
scripts/build_dataset_catalogue.py
```

## Tamper model

The catalogue detects changes at two layers:

- semantic artifact validation through the existing artifact loaders/digests;
- exact file/tree content SHA-256 stored in the catalogue entry.

Changing a registered file, directory member, context, cohort, replay study or sample makes verification fail. A changed artifact must be registered as a new audit chain rather than silently replacing the previous one.

## Probability guardrail

The catalogue may later index calibration results, but Phase 11G does not create such results.

Until a separately approved calibration phase establishes sufficient sample size, time-separated validation, bias handling, transaction-cost assumptions, confidence intervals and out-of-sample performance, `Setup Score` remains non-probabilistic and `estimated_probability` remains N/A/null.
