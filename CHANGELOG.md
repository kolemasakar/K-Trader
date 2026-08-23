# Changelog

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
