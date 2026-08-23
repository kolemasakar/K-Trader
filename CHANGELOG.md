# Changelog

## 2026-08-23 - Phase 9 CI / Docker / production preparation

- Added GitHub-hosted repository-wide CI and separated it from the production self-hosted runner.
- Real integrated CI initially found two invalid synthetic fixtures; fixed fixtures without weakening production candle validation.
- Real Docker import found a FastAPI lifecycle compatibility regression; migrated runtime startup/shutdown to ASGI lifespan.
- CI run `32636825758`: **92 tests passed**, compile PASS, Compose PASS, Docker build PASS, production runtime import PASS.
- Added hardened non-root Dockerfile and read-only Compose runtime with loopback-only application bind.
- Added optional Caddy HTTPS profile.
- Added manual-only `main` production deploy workflow.
- Added immutable commit-SHA releases and rollback when process/live acceptance fails.
- Added target-VPS REST acceptance for 5m/15m/1h/4h/1d and public 5m WebSocket acceptance.
- Added scanner `data_ready` and MTF API acceptance gate.
- Added Ubuntu/Docker provisioning and checksum-verified GitHub runner registration automation.
- Updated CI/deploy workflows to current Node-24 action major versions.
- Final production-prep CI run `32637233264`: pytest/compile/Compose/Docker/runtime/acceptance-packaging PASS.
- Phase 9 remains open only for external VPS provisioning, live acceptance, persistence/restart and HTTPS verification.

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
- Phase 8.5 code is now included in the Phase 9 repository-wide **92-test PASS** baseline.

## 2026-08-23 - Phase 8 read-only API

- Added FastAPI read-only application boundary.
- Added thread-safe `ApiReadModel` for scanner-published runtime state.
- Added health/status/universe/market/candles/analysis/candidates/signals endpoints.
- Added exact Decimal-as-string serialization and UTC ISO-8601 timestamps.
- Added provider ambiguity detection with HTTP 409; no silent provider substitution.
- Added candle source provenance and A/A+ LONG/SHORT-only signal filtering.
- Added application-level fixed-window rate limiter.
- Added Custom GPT OpenAPI schema and Action guide.
- Verification: isolated Phase 8 API harness 7/7 PASS.

## 2026-08-23 - Phase 7 setup / rating engine

- Added provider-independent Trading Engine package and canonical setup discovery/geometry/scoring.
- Added evidence/STRONG-level/HTF/RR/ATR hard gates.
- Added structural Entry/Stop/Target and prohibited synthetic 3R targets.
- Added 100-point Setup Score, A+/A/B/C and hard-reject override.
- Added optional explicit RiskContext sizing.
- Verification: exact Phase 7 module logic 17/17 isolated checks PASS.

## 2026-08-23 - Phase 6 trap + VSA

- Added trap engine and VSA ND/NS/T/UT/BC/SC/SV with HTF/location/confirmation rules.
- Verification: isolated Phase 6 harness 14 tests passed.

## 2026-08-23 - Phase 5 market structure

- Added swings, MTF regime/strength, DST-aware sessions, levels/lifecycle and consolidation.
- Verification: isolated Phase 5 harness 12 tests passed.

## 2026-08-23 - Phase 4 indicators

- Added Wilder ATR14, canonical ATR5D, SMA/EMA MA50/200 and relative volume/spread metrics.
- Verification: isolated Phase 4 harness 12 tests passed.

## 2026-08-23 - Phase 3 live market data

- Added Binance USD-M and Bybit Linear public WebSocket streaming, local MTF aggregation, reconnect and REST reconciliation/gap recovery.
- Verification: isolated Phase 3 harness 10 tests passed.
- Target-VPS continuous REST/WS acceptance remains pending.

## 2026-08-23 - Phase 2 market-data core

- Added UTC validation, missing-bar/freshness rules, fail-closed MTF bootstrap and SQLite WAL persistence.
- Verification: isolated Phase 2 harness 9 tests passed.
- Target-VPS live bootstrap acceptance remains pending.

## 2026-08-23 - Phase 1 market-data foundation

- Added exchange-agnostic MarketDataProvider contract, Binance USD-M + Bybit Linear public REST adapters, universe/liquidity filtering and fallback.
- Verification: 7 tests passed.
- Target-VPS provider acceptance remains pending.

## 2026-08-23 - Phase 0 foundation

- Approved K-Trader Roadmap v1.0 and read-only exchange-agnostic architecture.
- Approved SYSTEM K_Trader v1.1.
- Replaced uncalibrated Probability with Setup Score for v1.
- Defined canonical data, ATR, VSA, levels, trap, scoring, signal, API, deployment, test and security contracts.
