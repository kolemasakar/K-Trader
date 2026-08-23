# K-Trader Roadmap v1.2

Status: APPROVED baseline with runtime coordinator implemented, 2026-08-23.

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

Repository-wide CI remains Phase 9.

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

Status: IMPLEMENTATION COMPLETE / REPOSITORY-WIDE CI EXECUTION PENDING PHASE 9.

Implemented:

- provider priority/fallback refresh per scanner cycle;
- current liquidity-ranked universe publication;
- configurable top-N analysis shortlist;
- bounded MTF bootstrap/analysis concurrency;
- retained Phase 3 live WebSocket task for the selected provider/shortlist;
- MTF readiness and freshness validation before every analysis;
- indicators -> structure -> Trap/VSA -> Phase 7 Trading Engine orchestration;
- per-symbol failure isolation;
- explicit `NO_SETUP` -> `NO_TRADE` sentinel only for valid/fresh data;
- no fabricated decision when mandatory market data is invalid/stale;
- atomic replacement of status/universe/candles/decisions in `ApiReadModel`;
- provider/aggregate/mixed candle-series provenance;
- expanded runtime status and clean shutdown;
- production entrypoint `uvicorn ktrader.runtime.app:app`;
- orchestration tests committed.

Exit condition for implementation: satisfied.

Validation gate: Phase 9 must execute repository-wide pytest before deployment. No Phase 8.5 PASS count is claimed before that CI run.

## Phase 9 - VPS / Docker / CI-CD

NEXT.

Mandatory first gate:

- run complete repository pytest suite;
- fix any regression before container/deployment work.

Then:

- Dockerfile + Docker Compose;
- Ubuntu VPS persistent `/opt/k-trader` layout;
- scanner coordinator + API runtime service;
- private-repo self-hosted GitHub Runner;
- push-to-main test/build/deploy/health workflow;
- target-VPS public REST/bootstrap/WebSocket acceptance for Phases 1-3;
- HTTPS exposure for read-only API.

## Phase 10 - Custom GPT Update

- deploy canonical SYSTEM instructions;
- replace `.invalid` OpenAPI server with deployed HTTPS host;
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
