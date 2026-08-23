# Changelog

## 2026-08-23 - Phase 8 read-only API

- Added FastAPI read-only application boundary.
- Added thread-safe `ApiReadModel` for scanner-published runtime state.
- Added `/health`, scanner status, universe, market snapshot, candles, analysis, candidates and signals endpoints.
- Added exact Decimal-as-string serialization and UTC ISO-8601 timestamps.
- Added provider ambiguity detection with HTTP 409; no silent provider substitution.
- Added candle source provenance `provider|aggregate`.
- Added A/A+ LONG/SHORT-only signal filtering.
- Added application-level fixed-window rate limiter with HTTP 429 and Retry-After.
- Added FastAPI/Uvicorn runtime dependencies.
- Added `custom_gpt/openapi.yaml` with stable Action operation IDs.
- Added Custom GPT Action usage guide.
- Added API_SPEC v1.1 and Phase 8 config/test/checkpoint documentation.
- Verification: isolated Phase 8 API harness 7/7 PASS; FastAPI/OpenAPI generation and syntax validation PASS.
- Repository audit identified a missing autonomous scanner orchestration layer; Phase 8.5 Runtime Scanner Coordinator was inserted before deployment.

## 2026-08-23 - Phase 7 setup / rating engine

- Added provider-independent Trading Engine package.
- Added setup candidate discovery from confirmed trap/VSA evidence.
- Added canonical setup types: TRAP_VSA_CONFIRMATION, VSA_LEVEL_CONFIRMATION, TRAP_LEVEL_CONFIRMATION.
- Added evidence identity/setup-type consistency hard gates.
- Added STRONG confirmed/mirror primary-level hard gate.
- Added canonical Entry trigger and luft `max(1 tick, 0.02 * ATR14)`.
- Added structural Stop using level boundary / trap sweep extreme.
- Added nearest confirmed/mirror opposing structural Target.
- Prohibited synthetic 3R targets when no structural target exists.
- Added RR >=3 hard gate.
- Defined canonical ATR-used origin from UTC-day directional extreme to proposed Entry.
- Added 100-point deterministic scoring weights and A+/A/B/C thresholds.
- Added hard-reject public score cap <=69 and forced C grade.
- Added optional explicit RiskContext position sizing without inferring account state.
- Added final TradingDecision and best-decision selector.
- Added SETUP_SPEC v1.0, SCORING_SPEC v1.1, ATR_SPEC v1.2, SIGNAL_SPEC v1.1 and TRADING_ENGINE_SPEC v1.2.
- Verification: exact Phase 7 module logic 17/17 isolated checks PASS; syntax compilation PASS.

## 2026-08-23 - Phase 6 trap + VSA

- Added provider-independent TrapEvent evidence model.
- Added confirmed/mirror support-resistance eligibility for trap detection.
- Added ATR-scaled failed-break detection with return and directional-confirmation windows.
- Added RETURNED / CONFIRMED / EXPIRED trap states.
- Added provider-independent VSAEvent evidence model.
- Added deterministic K-Trader v1 raw heuristics for ND, NS, T, UT, BC, SC and SV.
- Added previous-20-bar relative-volume / relative-spread baseline and close-location metrics.
- Added strict HTF directional context and confirmed-level location filters.
- Added ATR-scaled level proximity and next-two-bar confirmation logic.
- Added same-level confirmed trap confluence without allowing trap evidence to create a signal independently.
- Added RAW / IGNORED / VALID_CONTEXT / CONFIRMED VSA states.
- Verification: isolated Phase 6 harness 14 tests passed; compile validation PASS.

## 2026-08-23 - Phase 5 market structure

- Added strict swing-high/swing-low detection.
- Added per-timeframe regime and MTF precedence.
- Added directional strength evidence and DST-aware session context.
- Added historical level clustering, lifecycle, MTF priority and consolidation detection.
- Added LIMIT/PARANORMAL_BAR explicit evidence support without fabricated automatic geometry.
- Verification: isolated Phase 5 harness 12 tests passed; compile validation PASS.

## 2026-08-23 - Phase 4 indicators

- Added True Range and Wilder ATR14.
- Added D1 ATR5D same-bar abnormal filter without rejected-bar replacement.
- Added SMA/EMA MA50/200.
- Added relative volume/quote volume/candle spread.
- Added generic ATR-used helper.
- Verification: isolated Phase 4 harness 12 tests passed; compileall PASS.

## 2026-08-23 - Phase 3 live market data

- Added Binance USD-M and Bybit Linear public WebSocket streaming.
- Added provisional open-candle handling, closed 5m persistence and local MTF aggregation.
- Added provider/aggregate provenance, stale detection, reconnect and REST reconciliation/gap recovery.
- Verification: isolated Phase 3 harness 10 tests passed; compileall PASS.
- Target-VPS continuous REST/WS acceptance remains pending.

## 2026-08-23 - Phase 2 market-data core

- Added UTC timeframe validation, missing-bar/freshness rules and fail-closed MTF bootstrap.
- Added SQLite WAL Decimal-preserving persistence and atomic MTF writes.
- Verification: isolated Phase 2 harness 9 tests passed; compileall PASS.
- Target-VPS live bootstrap acceptance remains pending.

## 2026-08-23 - Phase 1 market-data foundation

- Added exchange-agnostic MarketDataProvider contract and capability declarations.
- Added normalized instrument/ticker/candle models.
- Added Binance USD-M and Bybit Linear public REST adapters.
- Added configurable universe/liquidity filtering, provider fallback and smoke utility.
- Verification: 7 tests passed; compileall PASS.
- Target-VPS provider acceptance remains pending.

## 2026-08-23 - Phase 0 foundation

- Approved K-Trader Roadmap v1.0.
- Established read-only v1 boundary and exchange-agnostic provider architecture.
- Approved SYSTEM K_Trader v1.1.
- Replaced uncalibrated Probability with Setup Score for v1.
- Defined canonical data, ATR, VSA, levels, trap, scoring, signal, API, deployment, test and security contracts.
