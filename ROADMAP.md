# K-Trader Roadmap v1.3

Status: APPROVED baseline; repository-side implementation complete through Phase 9 production preparation, 2026-08-23.

## Phase 0 - Foundation

Status: COMPLETE.

## Phase 1 - Exchange-Agnostic Market Data Foundation

Status: IMPLEMENTATION COMPLETE / TARGET-VPS LIVE ACCEPTANCE PENDING.

- provider contract/capabilities;
- Binance USD-M + Bybit Linear public adapters;
- normalized instruments/tickers/candles;
- native provider symbols;
- price/liquidity universe;
- provider fallback without series mixing;
- deterministic tests: 7 passed.

## Phase 2 - Market Data Core

Status: IMPLEMENTATION COMPLETE / TARGET-VPS LIVE ACCEPTANCE PENDING.

- REST MTF bootstrap `1d/4h/1h/15m/5m`;
- SQLite WAL / Decimal persistence;
- UTC/gap/freshness validation;
- atomic MTF persistence;
- deterministic tests: 9 passed.

## Phase 3 - Live Market Data

Status: IMPLEMENTATION COMPLETE / TARGET-VPS LIVE ACCEPTANCE PENDING.

- Binance/Bybit public WebSocket;
- live 5m base state;
- local 15m/1h/4h/1d aggregation;
- reconnect/stale/reconciliation/gap recovery;
- deterministic tests: 10 passed.

## Phase 4 - Indicators

Status: IMPLEMENTATION COMPLETE.

- Wilder ATR14 / canonical ATR5D;
- SMA/EMA MA50/200;
- volume/VSA spread metrics;
- generic ATR-used metric;
- deterministic tests: 12 passed.

## Phase 5 - Market Structure

Status: IMPLEMENTATION COMPLETE.

- swings/regime/strength;
- DST-aware sessions;
- MTF levels and lifecycle;
- consolidation;
- deterministic tests: 12 passed.

## Phase 6 - Trap + VSA

Status: IMPLEMENTATION COMPLETE.

- liquidity-sweep/trap engine;
- ND/NS/T/UT/BC/SC/SV;
- HTF/location/confirmation hard rules;
- deterministic tests: 14 passed.

## Phase 7 - Setup / Rating Engine

Status: IMPLEMENTATION COMPLETE.

- approved 14-component evaluation flow;
- canonical setup types and evidence gates;
- Entry/Luft/SL/structural TP;
- RR >=3 and ATR-used hard gates;
- deterministic Setup Score and A+/A/B/C;
- explicit optional RiskContext;
- LONG/SHORT/NO_TRADE TradingDecision;
- Phase 7 isolated harness: 17 passed.

## Phase 8 - Read-only K-Trader API

Status: IMPLEMENTATION COMPLETE.

- FastAPI read-only boundary;
- health/status/universe/market/candles/analysis/candidates/signals;
- Decimal-as-string and UTC serialization;
- provider ambiguity fail-closed behavior;
- API rate limiting;
- Custom GPT OpenAPI/Action guide;
- isolated API harness: 7 passed.

## Phase 8.5 - Runtime Scanner Coordinator

Status: IMPLEMENTATION COMPLETE / REPOSITORY-WIDE CI VERIFIED.

- provider priority/fallback refresh per scanner cycle;
- liquidity-ranked universe and configurable top-N analysis shortlist;
- bounded MTF bootstrap/analysis concurrency;
- retained live WebSocket task unless provider/shortlist changes;
- MTF readiness/freshness gate before analysis;
- indicators -> structure -> Trap/VSA -> Trading Engine orchestration;
- per-symbol failure isolation;
- valid/fresh no-setup -> explicit NO_TRADE;
- stale/incomplete input -> no fabricated decision;
- atomic `ApiReadModel` publication;
- provider/aggregate/mixed provenance;
- production ASGI lifespan entrypoint and clean shutdown.

Repository-wide CI result including Phase 8.5: **92 tests passed**.

## Phase 9 - VPS / Docker / CI-CD

Status: REPOSITORY-SIDE COMPLETE / TARGET-VPS DEPLOYMENT AND LIVE ACCEPTANCE PENDING.

Completed and CI-verified:

- GitHub-hosted repository-wide CI;
- compile + pytest gate;
- Docker Compose validation;
- hardened production Docker image;
- production image runtime import;
- manual-only `main` deployment workflow for repository-scoped self-hosted runner;
- immutable `/opt/k-trader/releases/<sha>` deployment model;
- rollback on failed health/live acceptance;
- optional Caddy HTTPS profile;
- Ubuntu/Docker provisioning automation;
- checksum-verified GitHub runner registration baseline;
- public REST acceptance on `5m/15m/1h/4h/1d`;
- public 5m WebSocket acceptance;
- scanner readiness + MTF API acceptance utility.

CI evidence:

- run `32636825758`: 92 pytest PASS, Compose PASS, Docker build/import PASS;
- run `32637233264`: final production-prep pytest/Compose/Docker/runtime/packaging PASS.

Pending only on real external infrastructure:

- provision Ubuntu VPS;
- register `k-trader-prod` self-hosted runner;
- execute production deploy;
- pass target-VPS REST/WS/runtime acceptance;
- verify persistence across real restart;
- configure DNS/TLS and verify public HTTPS.

Phase 9 exit occurs only after those live checks pass.

## Phase 10 - Custom GPT Update

- replace `.invalid` OpenAPI server with the deployed HTTPS host;
- connect read-only Action/OpenAPI schema;
- validate source/freshness/NO_TRADE output;
- add Privacy Policy URL if distribution mode requires it.

## Phase 11 - Hardening

- replay/regression history;
- signal outcomes;
- metrics/backup/recovery/rate limiting;
- stale-data fail-closed validation.

## Phase 12 - Multi-provider expansion

- add OKX/KuCoin/other public adapters through the same provider contract;
- keep Trading Engine provider-independent.

## Deferred beyond v1

- exchange credentials/account reads;
- order execution/automatic trading;
- PostgreSQL/TimescaleDB/Redis/Kafka/Kubernetes unless measured load justifies them;
- statistical win probability until calibrated from confirmed outcomes;
- full order-book storage.
