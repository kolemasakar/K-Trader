# Phase 11E Checkpoint - Historical Universe / Liquidity Capture and Study Cohorts

Date: 2026-08-23

Status: VERIFIED.

## Implemented

- provider-native timestamped universe/liquidity snapshot schema `ktrader.universe_snapshot.v1`;
- captured instrument identity plus ticker inputs used by liquidity scoring, including last price, 24h quote/base volume, trade count and bid/ask when available;
- deterministic liquidity rank and live-compatible universe size under an explicit `UniverseConfig`;
- strict single-provider snapshot validation and future-ticker timestamp rejection;
- append-only digest-verified archive schema `ktrader.universe_archive.v1`;
- per-snapshot SHA-256 plus archive-level SHA-256;
- archive rejection for provider/config mixing, duplicate/non-chronological snapshots and tampering;
- reproducible study cohort schema `ktrader.study_cohort.v1`;
- explicit cohort time window and optional symbol subset;
- automatic per-symbol `ReplayStudyContext` generation using only captured snapshots;
- replay liquidity points use snapshot capture timestamps, captured liquidity score/rank and the captured live-compatible universe size;
- missing symbols and changed analysis-critical instrument metadata fail closed;
- cohort/context digests and safe context-file path validation;
- operator utilities `scripts/capture_universe_snapshot.py` and `scripts/build_study_cohort.py`.

## Historical-data guardrail

Current public ticker endpoints expose current market state; they do not provide a trustworthy historical universe/rank series retroactively.

Phase 11E therefore never reconstructs an old liquidity rank or universe size from today's data. Historical replay context is valid only when a timestamped provider-native universe snapshot was actually captured at or before the replay cutoff and remains within the configured context-age window.

This means useful historical universe archives must be accumulated prospectively once a continuously running host is available.

## Provider consistency

One universe archive belongs to exactly one provider and one universe configuration. No provider fallback/splicing occurs inside an archive or study cohort. A provider switch starts a separate coherent archive/cohort.

## Study flow

```text
provider list_instruments + get_tickers
    -> UniverseConfig filters/ranking
    -> ktrader.universe_snapshot.v1
    -> append-only ktrader.universe_archive.v1
    -> time/symbol cohort selection
    -> ktrader.study_cohort.v1
    -> per-symbol ktrader.replay_context.v1
    -> Phase 11D full-engine replay
    -> Phase 11B conservative outcome evaluation
```

## Verification evidence

PR #8 (`Phase 11E historical universe capture and study cohorts`) GitHub Actions CI run:

`32654162474`

Integrated result:

- Python compile: PASS;
- shell syntax validation: PASS;
- repository-wide pytest: **147 passed, 1 dependency deprecation warning**;
- linux/amd64 Docker build/runtime import: PASS;
- linux/arm64 QEMU/Buildx build: PASS;
- ARM64 architecture assertion: PASS;
- ARM64 production ASGI import: PASS;
- packaged target-host acceptance utility on both architectures: PASS.

PR #8 was squash-merged to `main` as:

`3c2a21644442e1d621ca8402e9c1c97bedb0fe80`

## Probability guardrail

Phase 11E does not calculate or expose win probability. `Setup Score` remains a deterministic rule score and `estimated_probability` remains null/N/A.

## Current limitations / next work

- real historical universe archives do not exist retroactively; collection begins prospectively when a continuous host is available;
- archive capture is currently an operator utility and is not yet wired as a persistent periodic production service;
- real long provider-recorded MTF bundles plus matching universe archives still need to be captured and catalogued;
- transaction costs, funding, slippage and execution quality remain outside the current OHLC outcome model;
- statistical calibration remains a separate later approval gate.

## Remaining hardening

- production periodic universe-snapshot persistence integrated with runtime/operations;
- canonical real-provider dataset catalogue linking MTF bundle digests, universe archive/cohort digests and study results;
- operations hardening: SQLite backup/recovery, disk/log guards, metrics and restart/recovery validation;
- later approved statistical methodology with time-separated out-of-sample validation.
