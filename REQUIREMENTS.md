# Requirements v1.0

## Functional requirements

FR-001. The system SHALL operate read-only in v1.
FR-002. The system SHALL use only public market-data endpoints for exchange connectivity in v1.
FR-003. The core SHALL be exchange-agnostic through a `MarketDataProvider` interface.
FR-004. Supported provider adapters MAY include Binance, Bybit, OKX, KuCoin and others.
FR-005. One analysis SHALL use one coherent market-data series from one provider; cross-exchange OHLCV mixing is forbidden.
FR-006. Provider fallback SHALL start a new coherent snapshot and preserve provider identity.
FR-007. Universe discovery SHALL filter tradable perpetual derivatives by status/contract/quote semantics supported by each provider.
FR-008. User-configurable price limit SHALL support an enabled threshold and disabled/all-assets mode.
FR-009. Liquidity ranking SHALL use normalized liquidity inputs, not raw base volume alone.
FR-010. Historical bootstrap target: D1 250, 4H 250, 1H 250, 15m 250, 5m 300 bars, configurable.
FR-011. The normalized candle contract SHALL preserve OHLCV plus quote volume, trade count, taker-buy fields where available and source metadata.
FR-012. The system SHALL track freshness and reject stale inputs.
FR-013. Trading Engine SHALL evaluate the approved 14 components in canonical order.
FR-014. VSA pattern without valid location/context/confirmation SHALL NOT create a signal.
FR-015. RR < 3 SHALL be rejected.
FR-016. ATR used > 80% SHALL be rejected.
FR-017. Only A or A+ MAY be emitted as tradable setup status.
FR-018. v1 SHALL expose `Setup Score` and SHALL NOT present it as statistical probability.
FR-019. Position size/risk SHALL be N/A unless account balance, risk settings and instrument specifications are confirmed.
FR-020. The backend SHALL expose read-only HTTPS GET endpoints for Custom GPT integration.
FR-021. The Custom GPT SHALL report source and data time for live analysis.
FR-022. Insufficient confirmed data SHALL fail closed to NO TRADE.

## Non-functional requirements

NFR-001. UTC is canonical storage/aggregation time; Europe/Kyiv is presentation/default operational timezone.
NFR-002. Data persistence SHALL survive container restart.
NFR-003. WebSocket disconnects SHALL reconnect automatically and reconcile gaps through REST.
NFR-004. Engines SHALL consume normalized models only and SHALL NOT call exchange-specific APIs directly.
NFR-005. Configuration thresholds SHALL be externalized from code.
NFR-006. Core rules SHALL have deterministic unit/replay tests.
NFR-007. Deployment SHALL be reproducible with Docker Compose.
NFR-008. CI/CD SHALL deploy only approved `main` state to the VPS.
NFR-009. Secrets SHALL NOT be required for public exchange market-data collection in v1.
NFR-010. Logs SHALL not contain sensitive credentials if such credentials are introduced in later phases.

## v1 exclusions

- Trading/account API credentials.
- Automated order placement/management.
- Statistical probability claims without calibration.
- Full-depth order-book history.
