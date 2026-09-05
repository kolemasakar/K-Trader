# K-Trader

K-Trader is a read-only, exchange-agnostic market scanner and analysis backend for a Custom GPT.

## v1 objective

Collect confirmed public derivatives market data, normalize and validate it, maintain MTF history/live state, evaluate indicators/structure/traps/VSA, build deterministic setup geometry/scoring, run an autonomous scanner, and expose high-quality read-only results to K_Trader through HTTPS.

## Principles

- Read-only v1: no order placement, account access or exchange credentials.
- Exchange-agnostic core: Binance, Bybit, OKX, KuCoin and future providers are adapters, not the engine.
- Never mix OHLCV series across providers.
- Confirmed source data only; stale/gapped/insufficient context fails closed.
- UTC is canonical for storage/aggregation.
- Open live candles are provisional only.
- Quality > quantity; `NO_TRADE` is preferred to weak setup.
- RR >=3 for tradable setup.
- Setup Score is rule-based, not statistical probability.

## Target flow

Public Exchange API -> REST/WS Provider -> Normalized Data -> Validation/SQLite -> Universe/Liquidity -> ATR/MA -> Structure/Levels -> Trap -> VSA -> Setup Geometry -> Setup Score -> TradingDecision -> Runtime Coordinator -> Read-only API -> Custom GPT

## Implemented

### Phase 1-3 - Market data

- exchange-agnostic provider contract;
- Binance USD-M + Bybit Linear public REST/WS adapters;
- universe/liquidity filtering and provider fallback;
- MTF bootstrap `1d/4h/1h/15m/5m`;
- SQLite WAL, UTC/gap/freshness validation;
- live 5m state, MTF aggregation, reconnect and REST reconciliation.

### Phase 4-7 - Analysis engine

- Wilder ATR14 and canonical ATR5D;
- MA50/200 and relative volume/spread;
- MTF regime/strength/sessions/levels;
- Trap + ND/NS/T/UT/BC/SC/SV;
- canonical setup geometry, RR/ATR hard gates, Setup Score and A+/A/B/C;
- final `TradingDecision`.

### Phase 8-8.5 - API and runtime coordinator

- FastAPI health/status/universe/market/candles/analysis/candidates/signals;
- thread-safe `ApiReadModel`;
- exact Decimal strings and UTC timestamps;
- provider ambiguity fail-closed behavior;
- autonomous provider -> universe -> readiness -> indicators -> structure -> Trap/VSA -> Trading Engine flow;
- bounded concurrency, per-symbol failure isolation and atomic publication;
- explicit valid/fresh `NO_SETUP` -> `NO_TRADE`;
- production ASGI lifespan entrypoint.

### Phase 9-9.1 - Production / Oracle ARM64

Phase 9 localhost production is **LIVE AND VERIFIED**.

- GitHub-hosted repository-wide CI;
- hardened non-root/read-only Docker runtime;
- manual-only production deployment on `main`;
- immutable commit-SHA releases and rollback;
- optional Caddy HTTPS;
- target-host REST/WebSocket/scanner acceptance utilities;
- Oracle Cloud Always Free Ampere A1 production host in Frankfurt;
- Ubuntu 24.04 Minimal aarch64;
- active allocation 1 OCPU / 6 GB RAM;
- production runner label `k-trader-prod-arm64`;
- amd64 compatibility retained;
- multi-arch Docker CI with QEMU/Buildx ARM64 runtime import;
- dynamic runtime UID/GID alignment between the production runner user and the container bind-mounted SQLite data tree;
- fail-closed writable-data check before production build;
- health semantics aligned with partial per-symbol degradation without weakening stale-data protection.

Verified production deployment on 2026-09-04:

```text
GitHub Actions run: 33920829993 -> SUCCESS
Deployed SHA: 9ed572349ed0195e518f128894a1f187419dbcc1
Runtime uid:gid: 1002:1002
Data owner: ktrader:ktrader
API bind: 127.0.0.1:8000
Provider: binance_usdm
REST: 5m,15m,1h,4h,1d PASS
WebSocket: 5m PASS
Scanner: DEGRADED, data_ready=true, 13 ready / 7 failed
MTF API: PASS
Docker: healthy
/health: status=ok, mode=read_only, data_ready=true
```

The numeric UID/GID is host-specific. Production deployment derives it dynamically rather than hard-coding an image-system UID.

Historical note: Oracle A1 capacity was unavailable during the original 2026-08-23 provisioning attempts; capacity later became available and the production VM was created successfully.

### Phase 10 preparation - Custom GPT Action

Repository-side preparation is **VERIFIED**; live activation is pending public HTTPS.

- exact read-only OpenAPI schemas for eight Action operations;
- optional Bearer API-key enforcement for `/v1/*`;
- `KTRADER_ACTION_API_KEY` production secret wiring;
- public `/health` and `/privacy`;
- OpenAPI render/validation script for the eventual real HTTPS origin;
- live Action acceptance script;
- Builder checklist and privacy-policy baseline.

The canonical OpenAPI file deliberately keeps `https://api.k-trader.invalid` until a real host passes live Phase 10 acceptance.

### Phase 11A - Replay / Regression Hardening

- deterministic chronological replay harness;
- level lifecycle replay;
- causal Trap lifecycle: `BROKEN -> RETURNED -> CONFIRMED`, or `BROKEN -> EXPIRED` only after the return window elapses;
- gap/cross-provider fail-closed replay validation;
- ATR no-future-lookahead regression;
- freshness boundary regression;
- deterministic replay digest.

### Phase 11B - Provider History / Signal Outcomes

- versioned `ktrader.history.v1` JSONL dataset;
- canonical SHA-256 candle-content digest;
- closed/contiguous/single-provider history validation;
- conservative no-lookahead TradingDecision outcome tracking;
- explicit OHLC ambiguity instead of guessed intrabar ordering;
- deterministic decision fingerprints and SQLite outcome persistence;
- WIN/LOSS-only extraction for later statistical research.

### Phase 11C - Deep History / MTF Replay Bundles

- backward provider pagination with explicit UTC end cursor;
- Binance USD-M `endTime` and Bybit Linear `end` support;
- exact-depth multi-page closed-history collection;
- strict cursor progress, page deduplication and fail-closed gap/identity checks;
- deterministic `ktrader.mtf_bundle.v1` bundle for `1d/4h/1h/15m/5m`;
- one provider/symbol and one UTC `as_of` cutoff across all timeframes;
- per-timeframe SHA-256 plus bundle-level SHA-256;
- no-lookahead MTF slicing at explicit replay cutoff;
- deep single-timeframe and MTF public-data export utilities.

### Phase 11D - Full-engine Historical Replay / Outcome Studies

Repository-side implementation is **VERIFIED**:

- live runtime and historical replay share the same `analyze_candle_snapshot()` analysis path;
- chronological replay walks 5m cutoffs with MTF `as_of` slicing;
- versioned `ktrader.replay_context.v1` carries confirmed timestamped liquidity score/rank/universe size;
- missing or stale historical liquidity context fails closed rather than being approximated;
- deterministic `ktrader.replay_study.v1` study artifacts;
- exact decision fingerprints remain audit identities;
- stable setup-geometry keys deduplicate unchanged signals across consecutive cutoffs;
- unique tradable signals feed the conservative Phase 11B future-candle outcome evaluator and optional SQLite outcome store;
- explicit optional outcome horizon; no universal holding period is invented.

### Phase 11E - Historical Universe / Liquidity Capture + Study Cohorts

Repository-side implementation is **VERIFIED**:

- `ktrader.universe_snapshot.v1` captures one provider-native ranked universe at an explicit UTC timestamp;
- snapshots preserve the ticker inputs used by liquidity scoring and the live-compatible rank/universe size;
- `ktrader.universe_archive.v1` stores strictly chronological same-provider/same-config snapshots with per-snapshot and archive SHA-256 integrity;
- current ticker data is never used to fabricate a historical rank retroactively;
- `ktrader.study_cohort.v1` selects an explicit time window and optional symbol subset;
- per-symbol `ktrader.replay_context.v1` files are generated automatically from captured snapshots;
- provider/config mixing, future ticker timestamps, missing cohort symbols, changed analysis-critical instrument metadata and stale context fail closed;
- operator utilities capture universe snapshots and build replay cohorts.

### Phase 11F - Operations Hardening / Continuous Research Capture

Repository-side implementation is **VERIFIED** and production capture can now accumulate prospectively:

- production runtime retains and reuses the exact normalized instruments/tickers from the selected live universe request cycle;
- provider-coherent universe snapshots are captured automatically at a configurable interval, default 300 seconds;
- each capture is an immutable one-snapshot digest-verified archive under the persistent `/data/research/universe` tree;
- disk-space guard runs before scanner writes and fails closed on low storage;
- online SQLite backup uses the native backup API plus `PRAGMA integrity_check` and atomic replacement;
- backup retention and operator backup utility are implemented;
- restore regression verifies that a generated backup can be opened as a fresh repository with persisted data intact;
- scanner-age watchdog can degrade `/health` without changing its public response shape;
- Docker healthcheck fails on unusable/stale runtime while allowing fresh usable partial scanner degradation;
- K-Trader/Caddy container logs use bounded json-file rotation.

### Phase 11G - Dataset Catalogue Foundation

Repository-side implementation is **VERIFIED**:

- `ktrader.dataset_catalogue.v1` links one coherent research chain from MTF bundle through universe archive/cohort, replay study/provenance and optional binary outcome sample;
- every registered artifact keeps both its semantic identity and exact file/tree content SHA-256;
- `ktrader.study_run_provenance.v1` records the exact bundle, cohort, symbol replay context, full `RuntimeScannerConfig`, `ReplayStudyConfig` and replay-study file hashes;
- canonical cohort-linked replay mode produces a provenance sidecar;
- `ktrader.outcome_sample.v1` exports immutable WIN/LOSS-only samples only after exact agreement between the replay-study artifact and `OutcomeRepository`;
- catalogue verification re-opens source artifacts and fail-closes on provider/symbol/digest/path/relationship mismatches or tampering;
- catalogue entries and the complete catalogue receive deterministic SHA-256 identities;
- artifact-root containment and symlink/path-traversal guards are enforced.

Setup Score remains non-probabilistic. `estimated_probability` remains null/N/A.

## CI evidence

- CI run `32636825758`: historical Phase 9 repository baseline, **92 tests PASS**.
- CI run `32646869264`: Phase 9.1 multi-arch gate, **92 tests PASS**, amd64/arm64 Docker/runtime PASS.
- CI run `32647828382`: Phase 10 preparation + Phase 11A, **106 tests PASS**, amd64/arm64 PASS.
- CI run `32650220382`: Phase 11B, **121 tests PASS**, amd64/arm64 PASS.
- CI run `32652044967`: Phase 11C, **134 tests PASS**, amd64/arm64 PASS.
- CI run `32653087172`: Phase 11D, **140 tests PASS**, compile/shell PASS, amd64 Docker/runtime PASS, arm64 QEMU/Buildx image/architecture/runtime PASS.
- CI run `32654162474`: Phase 11E, **147 tests PASS**, compile/shell PASS, amd64 Docker/runtime PASS, arm64 QEMU/Buildx image/architecture/runtime PASS.
- CI run `32656033224`: Phase 11F, **155 tests PASS**, compile/shell/Compose PASS, amd64 Docker/runtime PASS, arm64 QEMU/Buildx image/architecture/runtime PASS.
- CI run `32657337221`: Phase 11G, **163 tests PASS**, compile/shell PASS, amd64 Docker/runtime PASS, arm64 QEMU/Buildx image/architecture/runtime PASS.
- PR #17 final CI: **170 tests PASS**, docker-amd64 PASS, docker-arm64 PASS.
- Production run `33920829993`: deployment + live Phase 9 acceptance PASS on Oracle ARM64.

## Runtime entrypoint

`PYTHONPATH=src uvicorn ktrader.runtime.app:app --host 127.0.0.1 --port 8000`

API-only entrypoint:

`PYTHONPATH=src uvicorn ktrader.api.app:app --host 127.0.0.1 --port 8000`

## Operator utilities

- `scripts/provider_smoke.py`
- `scripts/ws_smoke.py`
- `scripts/vps_acceptance.py`
- `scripts/phase9_acceptance.sh`
- `scripts/phase10_action_acceptance.py`
- `scripts/render_custom_gpt_openapi.py`
- `scripts/export_provider_history.py`
- `scripts/export_mtf_history.py`
- `scripts/run_replay_study.py`
- `scripts/capture_universe_snapshot.py`
- `scripts/build_study_cohort.py`
- `scripts/export_outcome_sample.py`
- `scripts/build_dataset_catalogue.py`
- `scripts/backup_sqlite.py`
- `scripts/provision_vps.sh`
- `scripts/register_runner.sh`
- `scripts/deploy.sh`

No exchange credentials are used.

## Canonical documentation

- `ROADMAP.md`
- `REQUIREMENTS.md`
- `ARCHITECTURE.md`
- `docs/HOSTING_OPTIONS.md`
- `docs/VPS_PROVISIONING.md`
- `docs/DEPLOYMENT.md`
- `docs/SECURITY.md`
- `docs/HISTORICAL_REPLAY_SPEC.md`
- `docs/DATASET_CATALOGUE_SPEC.md`
- `docs/PHASE_9_CHECKPOINT.md`
- `docs/PHASE_9_1_CHECKPOINT.md`
- `docs/PHASE_10_PREP_CHECKPOINT.md`
- `docs/PHASE_11A_CHECKPOINT.md`
- `docs/PHASE_11B_CHECKPOINT.md`
- `docs/PHASE_11C_CHECKPOINT.md`
- `docs/PHASE_11D_CHECKPOINT.md`
- `docs/PHASE_11E_CHECKPOINT.md`
- `docs/PHASE_11F_CHECKPOINT.md`
- `docs/PHASE_11G_CHECKPOINT.md`
- `docs/checkpoints/2026-09-05_PHASE9_PRODUCTION_ACCEPTANCE.md`
- `custom_gpt/SYSTEM_K_TRADER_v1_1.md`
- `custom_gpt/openapi.yaml`
- `custom_gpt/ACTION_GUIDE.md`
- `custom_gpt/BUILDER_CHECKLIST.md`
- `custom_gpt/PRIVACY_POLICY.md`
- `docs/*_SPEC.md`
- `docs/PHASE_*_CHECKPOINT.md`
- `docs/adr/*.md`

## Current phase

Repository-side Phase 10 preparation and Phase 11A/11B/11C/11D/11E/11F/11G hardening are **VERIFIED**. Phase 9 localhost production is **LIVE AND ACCEPTED** on Oracle ARM64.

Historical full-engine outcome studies require coherent provider-recorded MTF bundles plus timestamped universe/liquidity context captured prospectively. Continuous production runtime now provides the basis for that accumulation; missing historical ranks are never fabricated from current ticker data.

The current external critical path is Phase 10 public activation: choose a real API domain, configure DNS to the Oracle production host, allow public 80/443, configure the Action API key, redeploy with Caddy HTTPS, pass public Action acceptance, then render and install the deployment-specific Custom GPT OpenAPI schema.
