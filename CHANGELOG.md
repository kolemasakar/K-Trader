# Changelog

## 2026-08-23 - Phase 5 market structure

- Added strict swing-high/swing-low detection on validated closed contiguous candles.
- Added per-timeframe regime from swing structure plus MA50/200 alignment.
- Added MTF regime precedence for 1d/4h/1h.
- Added deterministic strength evidence from structure, MA alignment and relative-volume participation.
- Added DST-aware Tokyo/London/New York session context using IANA timezones.
- Added historical swing-level clustering with ATR-scaled zones.
- Added touch-based FLOATING/CONFIRMED level state and WEAK/MODERATE/STRONG strength.
- Added BROKEN/MIRROR/INVALIDATED lifecycle.
- Excluded BROKEN levels from active validation until mirror retest confirmation.
- Added MTF priority and nearest active support/resistance lookup.
- Added consolidation-zone detector.
- Added explicit LIMIT/PARANORMAL_BAR evidence types without fabricated automatic geometry.
- Added integrated MarketStructureSnapshot contract.
- Added MARKET_STRUCTURE_SPEC v1.0, LEVELS_SPEC v1.1 and TRADING_ENGINE_SPEC v1.1.
- Added Phase 5 config/test/checkpoint documentation.
- Verification: local isolated Phase 5 harness 12 tests passed; syntax/compile validation PASS.
- Repository-wide CI remains a Phase 9 gate.
- One intermediate `noop` commit temporarily truncated README; the following fast-forward corrective commit restored it and no history rewrite/force-push was used.

## 2026-08-23 - Phase 4 indicators

- Added provider-independent indicator package.
- Added standard True Range and Wilder ATR14.
- Added D1 ATR5D filtering against same-bar ATR14, avoiding look-ahead in replay.
- Preserved the approved no-replacement/no-duplication abnormal-bar rule.
- Added SMA and EMA calculations with canonical MA50/200 baseline `sma`.
- Added previous-20-bar volume baseline and relative volume.
- Added VSA candle-spread baseline and relative spread.
- Added optional relative quote volume only when all required quote-volume data is confirmed.
- Added generic ATR-used calculation and exact STRONG/ACCEPTABLE/LATE_REJECT boundaries.
- Kept ATR-used move origin explicitly deferred to Phase 7.
- Added normalized indicator snapshot.
- Verification: Phase 4 deterministic harness 12 tests passed; compileall PASS.

## 2026-08-23 - Phase 3 live market data

- Added provider-independent `LiveCandleEvent` contract.
- Added generic public JSON WebSocket transport.
- Added Binance USD-M public kline WebSocket streaming.
- Added Bybit Linear public kline WebSocket streaming and application heartbeat.
- Added normalized Binance/Bybit live candle parsers.
- Added provisional open-candle handling: open 5m bars stay in memory and are not canonical closed history.
- Added provider-confirmed closed 5m persistence.
- Added complete UTC local aggregation from 5m to 15m/1h/4h/1d.
- Added provider-versus-aggregate candle provenance.
- Migrated SQLite schema from v1 to v2 without deleting historical data.
- Added periodic REST reconciliation and gap-triggered recovery.
- Added stale-state detection and exponential reconnect baseline.
- Added duplicate closed-event idempotency.
- Added target-VPS public WebSocket smoke utility.
- Verification: Phase 3 deterministic harness 10 tests passed; compileall PASS.
- Target-VPS continuous REST/WS acceptance remains pending by design.

## 2026-08-23 - Phase 2 market-data core

- Added canonical UTC timeframe utilities for 1d/4h/1h/15m/5m.
- Added normalized candle integrity validation and missing-bar detection.
- Added interval-relative configurable freshness policy.
- Added fail-closed historical MTF bootstrap service.
- Added target+1 request behavior to preserve required closed-history depth when a current bar is open.
- Added SQLite WAL candle repository.
- Added Decimal-as-TEXT precision-preserving persistence.
- Added idempotent candle upsert and bootstrap audit records.
- Added atomic MTF snapshot persistence only after all timeframes pass validation.
- Verification: Phase 2 isolated harness 9 tests passed; compileall PASS.
- Target-VPS live bootstrap acceptance remains pending by design.

## 2026-08-23 - Phase 1 market-data foundation

- Added Python package baseline and dependency metadata.
- Added exchange-agnostic `MarketDataProvider` contract.
- Added provider capability declarations.
- Added normalized instrument, ticker and candle models.
- Separated canonical symbol from native `provider_symbol` for future OKX/other naming schemes.
- Added Binance USD-M public REST adapter.
- Added Bybit Linear public REST adapter with instrument pagination.
- Added quote-turnover liquidity ranking with confirmed spread penalty where bid/ask is available.
- Added configurable price filtering and all-price mode.
- Added priority-provider fallback without cross-provider market-series mixing.
- Added VPS provider smoke utility.
- Added provider contract, Bybit pagination, universe and fallback tests.
- Verification: 7 tests passed; compileall PASS.
- Live target-VPS provider acceptance remains pending by design.

## 2026-08-23 - Phase 0 foundation

- Approved K-Trader Roadmap v1.0.
- Established read-only v1 boundary.
- Reworked architecture from Binance-centric to exchange-agnostic provider model.
- Added provider fallback without cross-exchange OHLCV mixing.
- Added canonical normalized market-data contract.
- Approved SYSTEM K_Trader v1.1 and recorded owner-applied status.
- Replaced uncalibrated Probability with Setup Score for v1.
- Defined ATR5D valid-bar collection algorithm.
- Defined VSA/levels/trap/scoring/signal/API contracts.
- Defined VPS/Docker/self-hosted-runner deployment baseline.
- Defined test, operations and security baselines.
