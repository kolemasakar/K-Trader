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

- `MarketDataProvider` interface and capability model. DONE.
- Binance USD-M public provider. DONE.
- Bybit Linear second provider. DONE.
- Normalized instruments/tickers/candles and native `provider_symbol`. DONE.
- Configurable price limit and liquidity ranking. DONE.
- Provider fallback without cross-provider series mixing. DONE.
- Contract/pagination/failover/universe tests. DONE: 7 passed.
- Target-VPS public endpoint acceptance. PENDING TARGET VPS.

## Phase 2 - Market Data Core

Status: IMPLEMENTATION COMPLETE / TARGET-VPS LIVE ACCEPTANCE PENDING.

- REST MTF bootstrap `1d/4h/1h/15m/5m`. DONE.
- Closed-history depth 250/250/250/250/300. DONE.
- SQLite WAL and Decimal-preserving persistence. DONE.
- UTC boundaries, missing-bar validation, freshness. DONE.
- Atomic MTF persistence and bootstrap audit. DONE.
- Deterministic tests. DONE: 9 passed; compileall PASS.
- Real provider historical bootstrap on target VPS. PENDING TARGET VPS.

## Phase 3 - Live Market Data

Status: IMPLEMENTATION COMPLETE / TARGET-VPS LIVE ACCEPTANCE PENDING.

- Public Binance/Bybit WebSocket ingestion. DONE.
- Live `5m` base state; open candle provisional only. DONE.
- Closed 5m persistence. DONE.
- Complete UTC aggregation to `15m/1h/4h/1d`. DONE.
- Provider/aggregate provenance. DONE.
- Reconnect, stale detection, REST reconciliation and gap recovery. DONE.
- WebSocket smoke utility. DONE.
- Deterministic tests. DONE: 10 passed; compileall PASS.
- Continuous real-provider VPS acceptance. PENDING TARGET VPS.

## Phase 4 - Indicators

Status: IMPLEMENTATION COMPLETE.

- True Range and Wilder ATR14. DONE.
- ATR5D with same-bar ATR14 abnormal filter and five valid D1 ranges. DONE.
- No rejected-bar replacement/duplication. DONE.
- SMA/EMA; canonical MA50/200 baseline `sma`. DONE.
- Previous-20-bar relative volume and relative candle spread. DONE.
- Optional confirmed relative quote volume. DONE.
- Generic ATR-used metric and 40/80% boundaries. DONE.
- ATR-used move origin deferred to Phase 7. DONE.
- Deterministic tests. DONE: 12 passed; compileall PASS.

## Phase 5 - Market Structure

Status: IMPLEMENTATION COMPLETE.

- Strict swing-high/swing-low detection. DONE.
- Per-timeframe regime from swing structure + MA50/200 alignment. DONE.
- MTF regime precedence across `1d/4h/1h`. DONE.
- Directional strength evidence from structure, MA alignment and participation. DONE.
- DST-aware Tokyo/London/New York session context. DONE.
- Historical level clustering using ATR-scaled zones. DONE.
- Level strength by independent swing touches. DONE.
- FLOATING/CONFIRMED/BROKEN/MIRROR/INVALIDATED lifecycle. DONE.
- BROKEN level excluded from active validation until mirror confirmation. DONE.
- MTF level priority `1d > 4h > 1h > 15m > 5m`. DONE.
- Consolidation-zone detector. DONE.
- LIMIT/PARANORMAL_BAR explicit evidence support without invented automatic geometry. DONE.
- Deterministic Phase 5 tests. DONE: 12 passed; compile validation PASS.

Exit: deterministic provider-independent market structure/session/level context is available for Trap/VSA and later scoring.

## Phase 6 - Trap + VSA

Status: IMPLEMENTATION COMPLETE.

- Provider-independent trap evidence contract. DONE.
- Confirmed/mirror support/resistance eligibility. DONE.
- Failed-break LONG/SHORT sequence with ATR-scaled break threshold. DONE.
- Return and directional confirmation windows. DONE.
- Trap states `RETURNED / CONFIRMED / EXPIRED`. DONE.
- Raw VSA events ND, NS, T, UT, BC, SC, SV. DONE.
- Previous-20-bar relative volume/spread baseline. DONE.
- Strict HTF regime and confirmed-level location filters. DONE.
- ATR-scaled level proximity and next-bar confirmation. DONE.
- Same-level confirmed trap confluence. DONE.
- VSA states `RAW / IGNORED / VALID_CONTEXT / CONFIRMED`. DONE.
- Deterministic Phase 6 harness. DONE: 14 passed; compile validation PASS.

Exit: VSA/trap events are rule-backed evidence and cannot independently create a trade outside approved structure/location/context. No Setup Score or rating is assigned in Phase 6.

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

Hard rejects include RR < 3, unconfirmed/floating primary level, ATR used > 80%, missing confirmation and stale data.

Phase 7 must define the canonical setup-specific origin for ATR-used `move_distance`.

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
- Execute pending live provider acceptance from Phases 1-3.

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
