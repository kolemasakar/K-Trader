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

### Phase 8 - Read-only API

- FastAPI endpoints for health/status/universe/market/candles/analysis/candidates/signals;
- thread-safe `ApiReadModel`;
- exact Decimal strings and UTC timestamps;
- provider ambiguity fail-closed behavior;
- rate limiting;
- Custom GPT OpenAPI/Action guide.

### Phase 8.5 - Runtime Scanner Coordinator

- autonomous provider -> universe -> data readiness -> indicators -> structure -> Trap/VSA -> Trading Engine flow;
- configurable top-N liquidity shortlist;
- bounded bootstrap/analysis concurrency;
- retained live WebSocket task unless provider/shortlist changes;
- per-symbol failure isolation;
- explicit valid/fresh `NO_SETUP` -> `NO_TRADE` result;
- no fabricated decision for stale/incomplete data;
- atomic read-model publication;
- `provider|aggregate|mixed` series provenance;
- production ASGI lifespan entrypoint.

### Phase 9 - CI / Docker / production preparation

Repository-side implementation is complete:

- GitHub-hosted repository-wide CI;
- **92 tests PASS** on the integrated pre-ARM64 baseline;
- Docker Compose validation and production image build/import PASS;
- hardened non-root/read-only container baseline;
- manual-only production deployment on `main`;
- repository-scoped self-hosted runner provisioning baseline;
- immutable commit-SHA releases and rollback;
- optional Caddy HTTPS;
- target-host REST acceptance on all five timeframes;
- target-host public WebSocket acceptance;
- scanner/API readiness acceptance;
- Ubuntu/Docker and runner registration scripts.

### Phase 9.1 - Oracle ARM64 / Multi-arch

Primary production hosting is Oracle Cloud Always Free Ampere A1 in Germany Central (Frankfurt).

Repository adaptation includes:

- Ubuntu 24.04 Minimal aarch64 target;
- `VM.Standard.A1.Flex` target at 2 OCPU / 12 GB RAM;
- ARM64 production self-hosted runner label `k-trader-prod-arm64`;
- multi-arch runner registration for Linux arm64 and amd64;
- architecture-aware Ubuntu/Docker provisioning;
- separate CI Docker gates for linux/amd64 and linux/arm64;
- ARM64 image build/import verification under QEMU/Buildx;
- amd64 support retained as a potential fallback host path.

Oracle external status on 2026-08-23: A1 capacity was unavailable in Frankfurt AD-1, AD-2 and AD-3, including a reduced 1 OCPU / 6 GB request. No paid shape is approved as a workaround.

Potential fallback, not implemented: home Windows PC + Tailscale Funnel. Cloudflare Workers + Durable Objects is not planned for K-Trader v1 and is retained only as a future-project architecture idea.

## CI evidence

- CI run `32636825758`: repository-wide pytest **92 passed**, Compose PASS, Docker build PASS, runtime import PASS.
- CI run `32637233264`: production-prep pytest/compile/Compose/Docker/runtime/acceptance-packaging PASS.
- Phase 9.1 multi-arch PR CI: pending until the current branch gate completes.

## Runtime entrypoint

`PYTHONPATH=src uvicorn ktrader.runtime.app:app --host 127.0.0.1 --port 8000`

The API-only entrypoint remains available for isolated API development:

`PYTHONPATH=src uvicorn ktrader.api.app:app --host 127.0.0.1 --port 8000`

## Operator utilities

- `scripts/provider_smoke.py`
- `scripts/ws_smoke.py`
- `scripts/vps_acceptance.py`
- `scripts/phase9_acceptance.sh`
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
- `docs/PHASE_9_CHECKPOINT.md`
- `docs/PHASE_9_1_CHECKPOINT.md`
- `custom_gpt/SYSTEM_K_TRADER_v1_1.md`
- `custom_gpt/openapi.yaml`
- `custom_gpt/ACTION_GUIDE.md`
- `docs/*_SPEC.md`
- `docs/PHASE_*_CHECKPOINT.md`
- `docs/adr/*.md`

## Current phase

Phase 9.1 repository-side Oracle ARM64 adaptation is implemented and awaiting its multi-arch PR CI gate.

Next external checkpoint after CI: obtain Oracle A1 capacity, provision the ARM64 host, register the production runner, deploy and pass live REST/WS/runtime/HTTPS acceptance.
