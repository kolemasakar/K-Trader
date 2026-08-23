# K-Trader Roadmap v1.1

Status: APPROVED baseline with runtime-coordinator correction, 2026-08-23.

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

Mandatory evaluation order implemented:

1. Market regime
2. Liquidity
3. Session
4. Trap
5. MTF levels
6. Strength
7. Setup Score
8. ATR
9. Setup type
10. Stop
11. Entry + luft
12. Position size
13. Risk
14. Rating

Implemented:

- setup candidate discovery from confirmed evidence;
- `TRAP_VSA_CONFIRMATION`, `VSA_LEVEL_CONFIRMATION`, `TRAP_LEVEL_CONFIRMATION`;
- evidence identity and setup-type consistency gates;
- STRONG confirmed/mirror primary-level hard gate;
- canonical luft `max(1 tick, 0.02*ATR14)`;
- confirmation-trigger Entry;
- structural SL;
- nearest confirmed opposing structural TP;
- no synthetic 3R target;
- RR >=3 hard gate;
- ATR-used origin from UTC-day directional extreme to proposed Entry;
- 100-point deterministic score;
- A+ >=90, A >=80, B >=70, C <70;
- hard rejects force C and public score <=69;
- optional explicit RiskContext sizing;
- final LONG/SHORT/NO_TRADE TradingDecision;
- deterministic Phase 7 exact-module harness: 17 passed.

Exit: PASSED for implementation. Repository-wide CI remains Phase 9.

## Phase 8 - Read-only K-Trader API

Status: IMPLEMENTATION COMPLETE.

- FastAPI read-only application boundary;
- `/health`, scanner-status, universe, market, candles, analysis, candidates and signals endpoints;
- internal `ApiReadModel` populated by scanner runtime;
- Decimal-as-string exact serialization;
- UTC ISO-8601 timestamps;
- provider ambiguity -> HTTP 409, never silent provider substitution;
- provider/aggregate candle provenance;
- A/A+ LONG/SHORT-only `/v1/signals`;
- single-process rate-limit baseline with HTTP 429;
- FastAPI/Uvicorn runtime dependencies;
- `custom_gpt/openapi.yaml` with stable operation IDs;
- Custom GPT Action guide;
- isolated API harness: 7 passed.

Exit: API implementation PASSED.

## Phase 8.5 - Runtime Scanner Coordinator

Status: REQUIRED / NEXT.

This phase was added after Phase 8 repository audit identified a missing application-level orchestration layer.

Purpose: turn the already implemented Phase 1-7 modules into one autonomous scanner process and publish its state to the Phase 8 API read model.

Required flow:

provider selection
-> universe/liquidity shortlist
-> REST bootstrap and live state readiness
-> indicators
-> market structure/levels/session
-> Trap/VSA
-> Setup/Rating Engine
-> ranked decisions/signals
-> `ApiReadModel`

Requirements:

- provider-independent orchestration;
- read-only only;
- no cross-provider OHLCV mixing;
- fail closed on stale/gapped/incomplete data;
- no TradingDecision until all mandatory inputs are confirmed;
- repeatable scanner cycle;
- per-symbol exception isolation;
- scanner runtime status/error reporting;
- deterministic orchestration tests;
- clean shutdown/restart boundaries for Phase 9 Docker service.

Exit: one process can autonomously produce current universe/candidates/signals and continuously update the API read model without manual calls.

## Phase 9 - VPS / Docker / CI-CD

- Ubuntu VPS;
- Docker + Docker Compose;
- persistent `/opt/k-trader` data/config/logs;
- private-repo self-hosted GitHub Runner;
- repository-wide pytest/build/deploy/health workflow;
- run scanner coordinator + API as production services;
- execute pending live provider acceptance from Phases 1-3.

## Phase 10 - Custom GPT Update

- deploy canonical SYSTEM instructions;
- replace `.invalid` server in OpenAPI with deployed HTTPS host;
- connect read-only Action/OpenAPI schema;
- validate source/freshness/NO_TRADE output;
- add valid Privacy Policy URL if GPT distribution mode requires it.

## Phase 11 - Hardening

- replay/regression history;
- signal outcomes;
- metrics/backup/recovery/rate limiting;
- stale-data fail-closed validation.

## Phase 12 - Multi-provider expansion

- add OKX/KuCoin/other public adapters through same provider contract;
- keep Trading Engine provider-independent.

## Deferred beyond v1

- exchange credentials/account reads;
- order execution/automatic trading;
- PostgreSQL/TimescaleDB/Redis/Kafka/Kubernetes unless measured load justifies them;
- statistical win probability until calibrated from confirmed outcomes;
- full order-book storage.
