# K-Trader Roadmap v1.0

Status: APPROVED baseline, 2026-08-23.

## Phase 0 - Foundation

Status: COMPLETE.

- Repository structure and canonical documentation.
- System instruction baseline.
- Data/provider contracts.
- Testing, security and deployment policy.

Exit: PASSED.

## Phase 1 - Exchange-Agnostic Market Data Foundation

Status: IMPLEMENTATION COMPLETE / LIVE VPS ACCEPTANCE PENDING.

- Define `MarketDataProvider` interface and provider capability model. DONE.
- Implement first public derivatives provider. DONE: Binance USD-M.
- Implement a second provider before Trading Engine work to validate abstraction. DONE: Bybit Linear.
- Discover tradable perpetual instruments and normalize symbols/tickers/candles. DONE.
- Separate canonical symbol from native `provider_symbol`. DONE.
- Support configurable price limit, including disabled/all-assets mode. DONE.
- Rank candidates by liquidity. DONE.
- Implement priority-provider fallback without cross-provider data fusion. DONE.
- Offline contract/pagination/failover/universe tests. DONE: 7 passed.
- Target-VPS public endpoint smoke acceptance. PENDING TARGET VPS.

Exit condition: two independent adapters satisfy equivalent normalized contracts; target-VPS live smoke confirms at least one legally accessible public provider without credentials.

## Phase 2 - Market Data Core

Status: IMPLEMENTATION COMPLETE / TARGET-VPS LIVE ACCEPTANCE PENDING.

- REST bootstrap for 1d/4h/1h/15m/5m. DONE.
- Default closed-history depth: 250/250/250/250/300. DONE.
- SQLite WAL persistence. DONE.
- Decimal-preserving storage and idempotent candle upsert. DONE.
- UTC candle boundaries and normalized close-time contract. DONE.
- Missing-bar detection and fail-closed validation. DONE.
- Provider/source identity preservation. DONE.
- Interval-relative freshness tracking. DONE.
- Atomic MTF snapshot persistence only after every requested timeframe passes. DONE.
- Bootstrap audit records. DONE.
- Deterministic Phase 2 tests. DONE: 9 passed; compileall PASS.
- Real provider historical bootstrap on target VPS. PENDING TARGET VPS.

Exit condition: offline integrity contract is implemented and tested; target-VPS live bootstrap confirms a fresh, contiguous persisted MTF snapshot from an accessible public provider.

## Phase 3 - Live Market Data

Status: IMPLEMENTATION COMPLETE / TARGET-VPS LIVE ACCEPTANCE PENDING.

- Provider-independent live candle event contract. DONE.
- Public WebSocket ingestion for Binance USD-M and Bybit Linear. DONE.
- Primary live `5m` candle state. DONE.
- Open candle remains provisional/in-memory; only confirmed closed 5m persists. DONE.
- Local complete UTC aggregation to `15m/1h/4h/1d`. DONE.
- Provider-versus-aggregate storage provenance and SQLite schema v2 migration. DONE.
- Automatic reconnect/stale detection. DONE.
- Periodic REST reconciliation. DONE.
- Gap-triggered REST recovery. DONE.
- Duplicate closed-event idempotency. DONE.
- Public WebSocket VPS smoke utility. DONE.
- Deterministic Phase 3 tests. DONE: 10 passed; compileall PASS.
- Continuous real-provider WebSocket/reconnect/gap-recovery acceptance. PENDING TARGET VPS.

Exit condition: target VPS receives continuous public 5m data from an accessible provider, persists closed bars, builds complete parent bars, survives reconnects and reconciles gaps without silent data loss.

## Phase 4 - Indicators

- ATR14, ATR5D, MA50/200.
- Volume statistics, relative volume/spread and ATR-used metrics.

## Phase 5 - Market Structure

- Market regime and strength.
- Session context.
- MTF levels and level lifecycle.

## Phase 6 - Trap + VSA

- Trap/liquidity-sweep engine.
- VSA events: ND, NS, T, UT, BC, SC, SV.
- Context and confirmation hard rules.
- Replay tests.

## Phase 7 - Setup / Rating Engine

Mandatory evaluation order:
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

Hard rejects include RR < 3, unconfirmed floating level, ATR used > 80%, missing confirmation and stale data.

Exit: deterministic A+/A/B/C classification; only A/A+ can produce a tradable signal.

## Phase 8 - Read-only K-Trader API

- FastAPI HTTPS API.
- Health, universe, market snapshot, analysis, candidates, signals and scanner-status endpoints.
- OpenAPI schema for Custom GPT Action.

## Phase 9 - VPS / Docker / CI-CD

- Ubuntu VPS.
- Docker + Docker Compose.
- Persistent `/opt/k-trader` data/config/logs.
- Private-repo self-hosted GitHub Runner.
- Push-to-main test/build/deploy/health-check workflow.
- Execute pending live provider acceptance from Phases 1, 2 and 3.

## Phase 10 - Custom GPT Update

- Deploy SYSTEM instructions.
- Connect read-only Action/OpenAPI schema.
- Validate source/freshness reporting and NO TRADE behavior.

## Phase 11 - Hardening

- Replay and regression testing.
- Signal history and outcome capture.
- Metrics, backup, recovery, rate limiting and stale-data fail-closed behavior.

## Phase 12 - Multi-provider expansion

- Add further exchanges/providers through the same interface.
- Keep engines provider-independent.

## Deferred beyond v1

- Exchange account credentials.
- Order execution / automatic trading.
- Account reads.
- PostgreSQL/TimescaleDB, Redis, Kafka and Kubernetes unless justified by measured load.
- Statistical win probability until calibrated on confirmed historical outcomes.
- Full order-book storage.
