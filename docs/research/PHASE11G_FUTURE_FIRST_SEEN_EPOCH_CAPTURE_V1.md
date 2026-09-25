# Phase 11G isolated first-seen epoch capture protocol v1

**Approval:** user instruction `go` following the separate future-epoch proposal, 2026-09-25.  
**Implementation state:** code pending CI/registration; no epoch may be backdated.  
**Classification:** `FORWARD_FIRST_SEEN_DATA_ONLY`.

## Why the new epoch starts as data-only

The legacy eight-stage prospective pipeline reads/writes a shared Phase 11G ledger and the original pre-registered fixed panel. It cannot be pointed at a new dynamically recorded top-19 panel or a separate ledger without changing the execution boundary. The old recorded cohort has an accepted 54/100 resolved families; an incomplete 2026-09-18 06:30 UTC cycle remains immutable in its original namespace.

The authorized **first stage** registers a new, strictly future-looking, separately named capture epoch. It captures contemporaneous K-Trader-owned Binance USD-M context and causal fully closed MTF candles, including first-seen source-file checksums. This is not yet a frozen v2.2 candidate outcome engine. It records **zero admitted new prospective families** until isolated strategy/resolver/evidence parity and governance are independently accepted.

## Immutable registration gate

The server creates `/data/research/phase11g/prospective_epochs/<epoch_id>/registration.json` before the future `start_cutoff_utc`. Registration is one-shot and includes:

- actual server UTC `registered_at_utc`;
- first fully closed M15 cutoff **strictly more than 15 minutes after registration**; final bounded inclusive M15 cutoff;
- pinned SHA256 of the exact installed recorder;
- pinned SHA256 of the accepted 2026-09-18 06:15Z state, original ledger, original frozen harness and original protocol;
- independently verified contemporaneous universe configuration;
- fixed selection rule **first 19 canonical recorded liquidity ranks at each cutoff**; no lower-ranked substitutions;
- provider exclusively `binance_usdm`, maximum archive-context age `300s`, settlement `180s`, absolute last acceptable capture delay `300s`;
- explicit `strategy_evaluation_enabled=false`, `trading_authorized=false`, `holdout_opened=false`, `hp_omen_allowed=false`, `admitted_new_prospective_families=0`.

The original `candidate_rule_set_v2_2`, frozen harness SHA `b8471af989090375dec9e25daae184814674a776ab9b46b45e660e35b368be08` and protocol SHA `ba671cbed71fdc79380f37a72b75f93e75aa3ee895f5385ef433f497165de5a3` are *read-only pins*, **not** modified.

## Causal collection

At `cutoff + 180s`, once and only once:

- require independent K-Trader local production `/health` to remain `read_only` and `data_ready=true`;
- find the latest K-Trader-owned archived snapshot with `captured_at <= cutoff`, fail-closed at `>300s`, validate its canonical digest, rank ordering, provider and registered universe configuration;
- take ranks `1..19` exactly as archived, even when some ranks have inadequate history;
- read existing SQLite in `mode=ro` and a single `PRAGMA query_only=ON` transaction;
- for each exact selected rank, record `1d=20`, `4h=80`, `1h=300`, `15m=400`, `5m=20` historical closed-bar observations, preserving OHLCV/source fields and ingestion timestamps;
- require each timeframe's final bar to be **fully closed by the cutoff**, exact sequence, sufficient depth, and historical ingestion timestamps no later than the cutoff+180s limit;
- persist every selected rank's independent structural and ingestion status; **do not replace missing ranks**;
- write the full snapshot under an isolated temporary cutoff directory, hash all MTF source files, atomically rename to the final cutoff directory; duplicate/partial collisions are fatal;
- refuse to classify an attempt as timely first-seen if capture ends after cutoff+300s.

A failed universe/capture/immutable-source invariant stops the bounded runner `FAIL_CLOSED`, preserving any partial output for audit. Status and event logs are mutable operational metadata; completed per-cutoff manifests and raw data files are read-only.

## Execution surface

- Only the existing independent K-Trader Oracle container `k-trader-ktrader-1`; no production-image change, no public endpoint, no provider trades.
- Script: `research/strategy_benchmark_v1/prospective_epoch_capture_v1.py`.
- The installed script and registration stay together in their isolated `prospective_epochs/<epoch_id>` directory; registration binds the installed script SHA.
- An approved, bounded, manually staged detached background collection may be used; a container restart is **not** proof of continued first-seen capture. No retrospective catch-up after interruption.
- No HP-OMEN, K_AI/MT4 backend, tunnel or auxiliary PC may be queried, directly or indirectly.

## Acceptance gates and accounting

- Mandatory GitHub Research Safety CI focused tests for epoch timing, MTF closure, source age, immutable output, registration pins and no-backdating.
- Exact server-side self-tests and registration preflight before launching the bounded runner.
- Verify the first new cutoff and source-file hashes; then allow further bounded causal capture until the registration end boundary unless it fails closed.
- Treat first-seen data-only observations as a **separate cohort**; the old 54 resolved families are never combined automatically with newly collected raw data.
- Isolated frozen-strategy/resolver implementation, cross-epoch comparability and admissible family accounting need separate documented acceptance. Phase 12, holdout and trade execution remain unauthorized.
