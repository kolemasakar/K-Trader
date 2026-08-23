# Phase 11G Checkpoint - Dataset Catalogue Foundation

Date: 2026-08-23

Status: VERIFIED.

## Implemented

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
- canonical replay runs using `--cohort` now emit a separate versioned study-run provenance sidecar;
- provenance records SHA-256 for the exact replay study file, bundle, cohort, symbol context, complete `RuntimeScannerConfig` and `ReplayStudyConfig`;
- scanner-config hashing includes all dataclass fields, so a VSA/Trap/ATR/runtime threshold change produces a different provenance identity even when the underlying market data are identical;
- immutable binary outcome sample export validates that WIN/LOSS rows in `OutcomeRepository` exactly match the replay-study embedded outcomes before writing the sample;
- non-binary outcomes are excluded from the immutable calibration sample by contract;
- operator utilities:
  - `scripts/export_outcome_sample.py`;
  - `scripts/build_dataset_catalogue.py`;
  - upgraded `scripts/run_replay_study.py` with canonical `--cohort` provenance mode.

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
                                +-> immutable WIN/LOSS outcome-sample SHA
                                      |
                                      +-> dataset-catalogue entry SHA
                                            |
                                            +-> catalogue SHA
```

A catalogue is therefore an integrity and reproducibility index. It does not edit, repair, interpolate or synthesize any market or outcome artifact.

## Study provenance guardrail

`study_id` remains the Phase 11D deterministic study identity. Phase 11G adds a stronger external provenance identity that records the complete scanner and study configuration plus exact source context/cohort and study-file SHA.

This avoids treating two studies as equivalent merely because their broad data inputs are similar while analysis thresholds or operational study parameters differ.

## Outcome sample guardrail

`ktrader.outcome_sample.v1` is an immutable study-specific binary sample. It may contain only `WIN` and `LOSS` rows that are already present in the replay study and that exactly match the corresponding rows in `OutcomeRepository`.

`AMBIGUOUS`, `OPEN`, `PENDING_ENTRY`, expired and `NOT_ELIGIBLE` rows remain outside the binary sample. The sample does not calculate a win probability.

## Verification evidence

PR #10 (`Phase 11G dataset catalogue foundation`) GitHub Actions CI run:

`32657337221`

Integrated result:

- Python compile: PASS;
- shell syntax validation: PASS;
- repository-wide pytest: **163 passed, 1 dependency deprecation warning**;
- linux/amd64 Docker build/runtime import: PASS;
- linux/arm64 QEMU/Buildx build: PASS;
- ARM64 architecture assertion: PASS;
- ARM64 production ASGI import: PASS;
- packaged target-host acceptance utility on both architectures: PASS.

PR #10 was squash-merged to `main` as:

`96de78d503432122d98e1c9ad1f01299802862a8`

## Trading / probability guardrails

Phase 11G does not change Trading Engine setup discovery, RR, ATR-used, VSA/Trap, scoring, grading, signal eligibility or execution behavior.

`Setup Score` remains a deterministic rule score and is not statistical probability. `estimated_probability` remains null/N/A.

## Remaining work

- real Oracle-host prospective market/universe capture and live dataset catalogue population;
- optional catalogue automation after scheduled replay-study jobs exist;
- repository governance/release hardening;
- target-host live persistence/backup/restart/HTTPS acceptance;
- statistical calibration only after a separately approved methodology and sufficient real outcome sample.
