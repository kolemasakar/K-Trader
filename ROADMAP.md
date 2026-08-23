# K-Trader Roadmap v1.0

Status: APPROVED baseline, 2026-08-23.

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

NEXT.

- FastAPI read-only service.
- Health endpoint.
- Universe/current market snapshot.
- Per-symbol analysis.
- Candidates/signals/scanner-status endpoints.
- Structured serialization of Phase 7 TradingDecision.
- OpenAPI schema for Custom GPT Action.
- API-level source/freshness and NO_TRADE guarantees.

## Phase 9 - VPS / Docker / CI-CD

- Ubuntu VPS.
- Docker + Docker Compose.
- Persistent `/opt/k-trader` data/config/logs.
- Private-repo self-hosted GitHub Runner.
- Repository-wide pytest/build/deploy/health workflow.
- Execute pending live provider acceptance from Phases 1-3.

## Phase 10 - Custom GPT Update

- deploy canonical SYSTEM instructions;
- connect read-only Action/OpenAPI schema;
- validate source/freshness/NO_TRADE output.

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
