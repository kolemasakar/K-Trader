# Changelog

## 2026-08-23 - Phase 8.5 runtime scanner coordinator

- Added autonomous `ScannerCoordinator` composing provider selection, universe, data readiness, indicators, market structure, Trap/VSA, Trading Engine and API publication.
- Added configurable top-N analysis shortlist, scan interval and bounded bootstrap concurrency.
- Integrated the existing Phase 2 MTF bootstrap and Phase 3 live WebSocket service.
- Retain live subscription across cycles unless provider or shortlist changes.
- Added per-symbol failure isolation and DEGRADED runtime state.
- Added explicit `NO_SETUP` -> `NO_TRADE` sentinel for fully valid/fresh symbols with no confirmed setup.
- Stale/incomplete symbols produce no fabricated TradingDecision.
- Added atomic `ApiReadModel.publish_cycle()` and full runtime-data clearing on total failure/provider loss.
- Extended candle-series provenance to `provider|aggregate|mixed`.
- Extended runtime status with cycle/readiness/live-stream metrics.
- Added production entrypoint `ktrader.runtime.app:app` and clean shutdown boundaries.
- Added runtime orchestration test file; execution is intentionally not claimed before Phase 9 repository-wide CI.

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

- Added provider-independent Trading Engine package and canonical setup discovery/geometry/scoring.
- Added evidence/STRONG-level/HTF/RR/ATR hard gates.
- Added structural Entry/Stop/Target and prohibited synthetic 3R targets.
- Added 100-point Setup Score, A+/A/B/C and hard-reject override.
- Added optional explicit RiskContext sizing.
- Verification: exact Phase 7 module logic 17/17 isolated checks PASS; syntax compilation PASS.

## 2026-08-23 - Phase 6 trap + VSA

- Added trap engine and VSA ND/NS/T/UT/BC/SC/SV with HTF/location/confirmation rules.
- Verification: isolated Phase 6 harness 14 tests passed; compile validation PASS.

## 2026-08-23 - Phase 5 market structure

- Added swings, MTF regime/strength, DST-aware sessions, levels/lifecycle and consolidation.
- Verification: isolated Phase 5 harness 12 tests passed; compile validation PASS.

## 2026-08-23 - Phase 4 indicators

- Added Wilder ATR14, canonical ATR5D, SMA/EMA MA50/200 and relative volume/spread metrics.
- Verification: isolated Phase 4 harness 12 tests passed; compileall PASS.

## 2026-08-23 - Phase 3 live market data

- Added Binance USD-M and Bybit Linear public WebSocket streaming, local MTF aggregation, reconnect and REST reconciliation/gap recovery.
- Verification: isolated Phase 3 harness 10 tests passed; compileall PASS.
- Target-VPS continuous REST/WS acceptance remains pending.

## 2026-08-23 - Phase 2 market-data core

- Added UTC validation, missing-bar/freshness rules, fail-closed MTF bootstrap and SQLite WAL persistence.
- Verification: isolated Phase 2 harness 9 tests passed; compileall PASS.
- Target-VPS live bootstrap acceptance remains pending.

## 2026-08-23 - Phase 1 market-data foundation

- Added exchange-agnostic MarketDataProvider contract, Binance USD-M + Bybit Linear public REST adapters, universe/liquidity filtering and fallback.
- Verification: 7 tests passed; compileall PASS.
- Target-VPS provider acceptance remains pending.

## 2026-08-23 - Phase 0 foundation

- Approved K-Trader Roadmap v1.0 and read-only exchange-agnostic architecture.
- Approved SYSTEM K_Trader v1.1.
- Replaced uncalibrated Probability with Setup Score for v1.
- Defined canonical data, ATR, VSA, levels, trap, scoring, signal, API, deployment, test and security contracts.
