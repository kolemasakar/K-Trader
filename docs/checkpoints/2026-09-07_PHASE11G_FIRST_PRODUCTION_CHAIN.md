# K-Trader Phase 11G — First Production Evidence Chain Checkpoint

Date: 2026-09-07

Status: COMPLETE / VERIFIED / CATALOGUED.

## Purpose

This checkpoint records the first fully materialized, provider-recorded, production-host Phase 11G evidence chain after the repository-side Phase 11A–11G implementation was already verified.

It is an audit/recovery checkpoint. It does not change Trading Engine setup discovery, RR, ATR-used, VSA/Trap, scoring, grading, signal eligibility or read-only product behavior.

## Accepted repository/runtime baseline

- repository: `kolemasakar/K-Trader`;
- default branch: `main`;
- accepted code/runtime SHA before this documentation checkpoint: `b75b1e3d74b5834e7c404555caa6bdf34f87fe12`;
- PR #27 fixed the fresh-process replay import cycle;
- PR #28 exposed inclusive UTC `--start` / `--end` replay bounds through the canonical CLI;
- PR #29 added reproducible assembly of immutable Phase 11F captures through `scripts/build_universe_archive.py`;
- post-merge CI run `34139445282`: pytest PASS, Docker amd64 PASS, Docker arm64 PASS;
- post-merge Tests run `34139445313`: PASS;
- Deploy Production #7 run `34139956047`: SUCCESS;
- deployed production SHA: `b75b1e3d74b5834e7c404555caa6bdf34f87fe12`.

The documentation checkpoint branch is based on that accepted code/runtime SHA. After this docs-only checkpoint is merged, repository HEAD may be newer than the deployed runtime while runtime behavior remains unchanged.

## Production runtime verification

Verified after Deploy Production #7:

- `/opt/k-trader/DEPLOYED_SHA` = `b75b1e3d74b5834e7c404555caa6bdf34f87fe12`;
- container `k-trader-ktrader-1` healthy;
- `/health`: `status=ok`, `mode=read_only`, `data_ready=true`;
- scanner status observed as `DEGRADED` while canonical data remained ready;
- provider: `binance_usdm`;
- Action authentication enabled;
- fresh-process imports: PASS without the temporary preflight shim;
- replay CLI exposes `--start`, `--end`, `--horizon-bars`;
- universe archive builder CLI is packaged and runnable in production.

## Phase 11F production accumulation acceptance

Before materialization, real continuous production universe capture was semantically verified:

- all inspected capture artifacts valid;
- schema: `ktrader.universe_archive.v1`;
- provider: `binance_usdm`;
- universe config: `USDT`, price limit enabled, max price `3`, max candidates `50`;
- duplicate snapshot SHA count: `0`;
- filename/path identity mismatches: `0`;
- non-monotonic capture ordering: `0`;
- no capture gaps above the accepted verification threshold;
- strict replay context policy remained `max_context_age_seconds=300` and was not widened to manufacture eligibility.

Phase 11F immutable source captures remain under `/data/research/universe` and are not modified by Phase 11G materialization.

## First canonical production chain

Identity:

- provider: `binance_usdm`;
- canonical symbol: `SUIUSDT`;
- replay cutoff window: `2026-09-05T14:45:00Z` through `2026-09-05T16:00:00Z`, inclusive;
- materialized root: `/data/research/phase11g/binance_usdm/SUIUSDT/20260905T144500Z_160000Z`.

### Universe archive

Selected 16 immutable production captures:

- first snapshot: `2026-09-05T14:40:13.613625Z`;
- last snapshot: `2026-09-05T15:59:13.890630Z`;
- archive SHA-256:
  `3c830d8410b913aa4b39afd8cb5be57e96a18b4a1ae4d46fa709fc11f70ccdda`.

### Study cohort

- symbol: `SUIUSDT`;
- snapshot count: `16`;
- strict maximum context age: `300` seconds;
- cohort SHA-256:
  `c63b90a1905149462e1eb31a842fff7c5f15290a7f4963107d7c8c4cf2273686`.

### MTF bundle

- `as_of`: `2026-09-05T18:15:00Z`;
- candle counts: `1d=300`, `4h=300`, `1h=300`, `15m=300`, `5m=400`;
- bundle SHA-256:
  `c0112c0d3688cddb86cabc54ae1c9da05e04ff2cef63f395b438448e3070d344`.

The materialized archive, cohort and MTF bundle reproduced the earlier read-only preflight semantic identities exactly.

### Full-engine replay

Canonical CLI configuration:

- `step_bars=1`;
- `horizon_bars=None`;
- `start=2026-09-05T14:45:00Z`;
- `end=2026-09-05T16:00:00Z`.

Result:

- analyzed cutoffs: `15`;
- skipped insufficient history: `0`;
- skipped missing context: `0`;
- unique tradable signals: `0`;
- outcome counts: `{}`;
- binary resolved count: `0`;
- `estimated_probability=null`;
- canonical study ID:
  `ebfd16b0b9059c5bd51f948d4c1b0086f4a2966a610e58dd7a6fb0d8ee474f5e`;
- provenance SHA-256:
  `08ba2378253dfa744ffbfc2fc74cae2ab6ff02264a9b60e6170d1992f6297c35`.

The earlier in-memory preflight study ID is not the canonical production identity because the final canonical `ReplayStudyConfig` includes explicit replay `start`/`end` bounds in the study hash. The physically materialized ID above is authoritative.

### Dataset catalogue

Registered under `/data/research/phase11g/catalogue.json`:

- schema: `ktrader.dataset_catalogue.v1`;
- entry count: `1`;
- entry ID:
  `f056dadd63c2283c07b0b2aa37b3bb2236d15e916d6fa3cf5a11fc71b38b814a`;
- catalogue SHA-256:
  `749c3aa20d02788b1c75b48e3325d854d7182f5b0729fea39dcf888af367b864`;
- outcome sample: `null`.

No outcome sample was fabricated because this study produced zero tradable signals and therefore zero binary WIN/LOSS outcomes.

## Final integrity gate

`load_dataset_catalogue(..., verify_artifacts=True)` completed without exception and rebuilt the registered entry from the physical artifacts.

The final verification re-confirmed all of these relationships and identities:

- bundle -> replay study;
- universe archive -> cohort;
- cohort symbol context -> provenance;
- replay study -> provenance;
- semantic IDs -> exact file/tree content hashes;
- catalogue entry digest -> catalogue digest.

Result: first real Phase 11G production evidence chain is formally COMPLETE / VERIFIED / CATALOGUED.

## Canonical operator rules established by this checkpoint

- use `scripts/build_universe_archive.py` to assemble immutable Phase 11F capture files into a deterministic archive;
- keep provider and universe configuration coherent;
- use UTC-only inclusive replay bounds through `run_replay_study.py --start/--end` when a study window is intended;
- keep `max_context_age_seconds=300` unless a separately approved policy change is made;
- do not fabricate historical rank/context or widen freshness just to increase eligible duration;
- do not fabricate outcome samples when no binary-resolved outcomes exist;
- register only fully linked chains and always perform catalogue reload with `verify_artifacts=True` after registration;
- keep Setup Score non-probabilistic and `estimated_probability` null/N/A until a separately approved calibration methodology passes out-of-sample validation.

## Next work

Phase 11 remains operational/research work rather than a new engine rewrite:

- continue prospective Phase 11F capture accumulation;
- materialize additional coherent provider/symbol/time-window study chains;
- accumulate real tradable decisions and conservative outcomes naturally;
- register each new immutable chain in the dataset catalogue;
- exercise backup/restore/restart/disk-guard/watchdog behavior over longer target-host periods;
- only later define and approve statistical calibration methodology with time-separated out-of-sample validation.

Phase 12 multi-provider expansion remains future work and must not begin implicitly from Phase 11 research accumulation.
