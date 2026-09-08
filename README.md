# K-Trader

K-Trader is a read-only, exchange-agnostic market scanner and analysis backend for a Custom GPT.

## v1 objective

Collect confirmed public derivatives market data, normalize and validate it, maintain coherent MTF history/live state, evaluate indicators/structure/traps/VSA, build deterministic setup geometry/scoring, run an autonomous scanner, and expose high-quality read-only results to K_Trader through HTTPS.

## Principles

- Read-only v1: no order placement, account access or exchange credentials.
- Exchange-agnostic core: providers are adapters; the Trading Engine is provider-independent.
- Never mix OHLCV series across providers.
- Confirmed source data only; stale, gapped, insufficient or ambiguous context fails closed.
- UTC is canonical for storage, aggregation and replay.
- Quality > quantity; `NO_TRADE` is preferred to a weak setup.
- `RR >= 3` is a hard tradability gate.
- Setup Score is deterministic and rule-based, not statistical probability.
- `estimated_probability` remains null/N/A until a separately approved calibration methodology exists.

## Target flow

```text
Public Exchange API
  -> REST/WS Provider
  -> Normalized Data
  -> Validation/SQLite
  -> Universe/Liquidity
  -> ATR/MA
  -> Structure/Levels
  -> Trap/VSA
  -> Setup Geometry
  -> Setup Score
  -> TradingDecision
  -> Runtime Coordinator
  -> Read-only API
  -> Caddy HTTPS
  -> Custom GPT Action
  -> K_Trader
```

## Current production state

Production is **LIVE AND VERIFIED** on Oracle Cloud ARM64.

```text
Host: Oracle Cloud Ampere A1, Frankfurt
OS: Ubuntu 24.04 Minimal aarch64
Allocation: 1 OCPU / 6 GB RAM
Runner: k-trader-prod-arm64
Public origin: https://ktrader-api.duckdns.org
Provider: binance_usdm
Deploy Production #9: run 34177978988 -> SUCCESS
Deployed SHA: 7fa20c3d7f0d89ae628eb2bf21e4c50164eb3eab
Image: k-trader:7fa20c3d7f0d89ae628eb2bf21e4c50164eb3eab
REST/WebSocket acceptance: PASS
Scanner: DEGRADED, 18 ready / 2 failed
MTF API: PASS
K-Trader container: healthy
HTTPS/TLS: PASS
Phase 10 Action live acceptance: PASS
```

The scanner may be `DEGRADED` while service health remains acceptable when canonical data is fresh and usable. Partial per-symbol failures do not weaken stale-data protection.

The application remains bound to host loopback at `127.0.0.1:8000`; public access is through Caddy HTTPS. Production `/v1/*` endpoints are Bearer-protected.

## Implemented phases

### Phase 1-3 - Market data

- Binance USD-M and Bybit Linear public REST/WS adapters;
- normalized instruments, tickers and candles;
- provider fallback without series mixing;
- canonical MTF bootstrap `1d/4h/1h/15m/5m`;
- SQLite WAL, UTC/gap/freshness validation;
- live 5m state, MTF aggregation, reconnect and reconciliation.

### Phase 4-7 - Analysis and TradingDecision engine

- Wilder ATR14 / canonical ATR5D;
- MA50/200, volume/VSA spread metrics;
- MTF regime/strength, sessions, levels and consolidation;
- Trap + ND/NS/T/UT/BC/SC/SV;
- canonical Entry/Luft/SL/structural-target geometry;
- RR and ATR-used hard gates;
- deterministic Setup Score and A+/A/B/C grades;
- LONG/SHORT/NO_TRADE `TradingDecision`.

### Phase 8-8.5 - API and runtime coordinator

- FastAPI health/status/universe/market/candles/analysis/candidates/signals;
- thread-safe `ApiReadModel`;
- exact Decimal strings and UTC timestamps;
- autonomous provider -> universe -> readiness -> analysis -> Trading Engine flow;
- bounded concurrency, per-symbol failure isolation and atomic publication;
- explicit valid/fresh no-setup -> `NO_TRADE`;
- production ASGI lifespan entrypoint.

### Phase 9-10 - Production and Custom GPT Action

- hardened non-root/read-only Docker runtime;
- manual-only deployment from approved `main`;
- immutable commit-SHA releases and rollback;
- Oracle ARM64 self-hosted production runner;
- Caddy HTTPS/TLS;
- Bearer API-key protection for `/v1/*`;
- public `/health`, `/privacy` and `/action-openapi.yaml`;
- canonical Action schema at `custom_gpt/openapi.yaml`;
- GPT Builder recognizes all eight required read-only operations;
- Builder Preview acceptance and live Action acceptance passed;
- canonical `NO TRADE` and fail-closed `WATCHLIST ONLY` behavior verified.

Phase 10 is **COMPLETE** for the current single-provider read-only v1 product boundary.

### Phase 11A-11F - Replay, history and research operations

Repository-side implementation is **VERIFIED**:

- deterministic chronological replay and no-lookahead regressions;
- provider-recorded history and conservative signal outcomes;
- exact-depth MTF history bundles;
- full-engine historical replay using the same analysis path as live runtime;
- provider-recorded historical universe/liquidity snapshots and study cohorts;
- continuous immutable research capture;
- online SQLite backup/integrity/retention;
- disk guard and scanner-age watchdog;
- bounded container logs.

### Phase 11G - Dataset catalogue and corrected discovery

The catalogue foundation is **VERIFIED** and two real provider-recorded chains are **COMPLETE / VERIFIED / CATALOGUED**.

Current catalogue:

```text
schema: ktrader.dataset_catalogue.v1
entries: 2
symbols: SUIUSDT, XRPUSDT
catalogue SHA: 057ff750966d2bc5043fffd7fdc37583dd0133480452c131b51f84109d2fb4b6
verify_artifacts=True: PASS
```

Strict research controls remain unchanged:

- provider: `binance_usdm` for the current production-research scope;
- `max_context_age_seconds=300`;
- newest universe snapshot at/before each replay cutoff defines historical membership;
- canonical MTF depths: `1d=300`, `4h=300`, `1h=300`, `15m=300`, `5m=400`;
- no historical rank/context fabrication;
- no freshness widening to manufacture eligibility;
- no synthetic outcomes;
- outcome samples only from actual binary WIN/LOSS results;
- no probability calibration;
- no Phase 12 expansion while the current Phase 11G gate remains unresolved.

## Phase 11G corrected historical replay checkpoint

PR #33 fixed the setup-side / MTF-regime contract:

```text
LONG  -> BULLISH
SHORT -> BEARISH
```

and aligned D1 fallback semantics in `context_strength()` with the canonical regime contract.

Accepted code/runtime SHA:

`7fa20c3d7f0d89ae628eb2bf21e4c50164eb3eab`

Post-merge validation:

- Tests run `34177001398`: PASS;
- CI run `34177001482`: pytest PASS, Docker amd64 PASS, Docker arm64 PASS;
- Deploy Production #9 run `34177978988`: SUCCESS.

Corrected Window #4 discovery (`2026-09-07T22:55Z` through `2026-09-08T00:10Z`):

```text
strict symbols: 45
MTF passed: 40
MTF rejected: 5
replay analyzed cutoffs: 600
total candidate decisions: 7596
HTF rejected: 7161
HTF aligned: 435
aligned direction/regime: 435 LONG -> BULLISH
tradable decisions: 0
unique tradable signals: 0
```

Conditional downstream funnel:

```text
435 HTF aligned
  -> 202 after primary-level strength
  -> 168 after valid geometry
  -> 142 after ATR <= 80%
  ->   0 after RR >= 3
```

All 142 final survivors were rejected only by `RR_BELOW_3`. No unexpected hard reject was present.

This means PR #33 is historically replay-validated, but **the RR gate must not be relaxed from this evidence alone**. The next task is to determine whether the observed RR distribution reflects real market geometry or a geometry/target-selection defect.

Pre-fix zero-signal results from Windows #1-#3 are not canonical evidence of natural signal absence until they are rerun with the corrected engine.

## Current Phase 11G gate

Current state:

**`CORRECTED_REPLAY_VALIDATED / RR_GEOMETRY_AUDIT_READY`**

Immediate next work is a **read-only RR-geometry audit of the 142 RR-only Window #4 candidates** covering:

- entry;
- stop;
- structural target;
- risk distance;
- reward distance;
- target level identity/type/timeframe;
- RR distribution;
- deduplication of unchanged setup geometry across neighboring cutoffs.

Do not change `RR >= 3`, ATR thresholds, freshness, catalogue entries, materialization rules or probability semantics before the geometry audit is understood.

Canonical checkpoint:

`docs/checkpoints/2026-09-08_PHASE11G_CORRECTED_REPLAY_RR_GEOMETRY_GATE.md`

## Latest CI / deployment evidence

- PR #33 post-merge Tests `34177001398`: PASS.
- PR #33 post-merge CI `34177001482`: pytest PASS, Docker amd64 PASS, Docker arm64 PASS.
- Deploy Production #9 `34177978988`: SUCCESS on `7fa20c3d7f0d89ae628eb2bf21e4c50164eb3eab`.
- PR #34 documentation checkpoint initial Tests `34182557243`: PASS.
- PR #34 documentation checkpoint initial CI `34182557216`: pytest PASS, Docker amd64 PASS, Docker arm64 PASS.

Historical validation evidence remains in `ROADMAP.md`, `CHANGELOG.md` and the phase/checkpoint documents.

## Runtime entrypoint

```bash
PYTHONPATH=src uvicorn ktrader.runtime.app:app --host 127.0.0.1 --port 8000
```

API-only entrypoint:

```bash
PYTHONPATH=src uvicorn ktrader.api.app:app --host 127.0.0.1 --port 8000
```

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
- `scripts/build_universe_archive.py`
- `scripts/build_study_cohort.py`
- `scripts/export_outcome_sample.py`
- `scripts/build_dataset_catalogue.py`
- `scripts/backup_sqlite.py`
- `scripts/provision_vps.sh`
- `scripts/register_runner.sh`
- `scripts/deploy.sh`

No exchange credentials are used by the market-data/research path.

## Canonical documentation

Start recovery/current-state reading here:

- `docs/CURRENT_STATE.md`
- `docs/checkpoints/2026-09-08_PHASE11G_CORRECTED_REPLAY_RR_GEOMETRY_GATE.md`
- `ROADMAP.md`
- `docs/PHASE_11G_CHECKPOINT.md`
- `docs/DEPLOYMENT.md`

Core contracts and product documentation:

- `REQUIREMENTS.md`
- `ARCHITECTURE.md`
- `docs/HISTORICAL_REPLAY_SPEC.md`
- `docs/DATASET_CATALOGUE_SPEC.md`
- `docs/SECURITY.md`
- `docs/VPS_PROVISIONING.md`
- `docs/PHASE_10_PRODUCT_ACCEPTANCE.md`
- `custom_gpt/SYSTEM_K_TRADER_v1_2_COMPACT.md`
- `custom_gpt/openapi.yaml`
- `custom_gpt/ACTION_GUIDE.md`
- `custom_gpt/BUILDER_CHECKLIST.md`
- `custom_gpt/PRIVACY_POLICY.md`

Historical transition checkpoints remain under `docs/checkpoints/`.

## Current phase

Phase 9 production and Phase 10 Custom GPT integration are complete. Phase 11A-11G repository-side foundations are verified. Two Phase 11G dataset chains are catalogued, continuous Phase 11F research capture remains active, and corrected Phase 11G discovery is currently stopped at the **RR-geometry audit gate**.

Phase 12 multi-provider expansion is **future / not active**. Statistical win probability remains deferred until adequate confirmed outcomes and a separately approved time-separated calibration methodology exist.
