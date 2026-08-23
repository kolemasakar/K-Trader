# Provider Public Endpoint Baseline

Verified against current official provider documentation on 2026-08-23.

This file records the Phase 1 REST contracts. No account credentials are used.

## Binance USD-M Futures

Base URL:

`https://fapi.binance.com`

Endpoints used by Phase 1:

- `GET /fapi/v1/exchangeInfo` - instrument/exchange metadata.
- `GET /fapi/v1/ticker/24hr` - 24h ticker statistics and quote/base turnover inputs.
- `GET /fapi/v1/ticker/bookTicker` - best bid/ask inputs.
- `GET /fapi/v1/klines` - historical candlesticks.

Canonical intervals used by K-Trader:

- 5m -> `5m`
- 15m -> `15m`
- 1h -> `1h`
- 4h -> `4h`
- 1d -> `1d`

Official documentation root:

`https://developers.binance.com/en/docs/products/derivatives-trading-usds-futures/Introduction`

## Bybit V5 Linear

Base URL:

`https://api.bybit.com`

Endpoints used by Phase 1:

- `GET /v5/market/instruments-info?category=linear` - instrument metadata; pagination required because the linear universe can exceed the default page size.
- `GET /v5/market/tickers?category=linear` - ticker, turnover, volume, bid/ask and supported market fields.
- `GET /v5/market/kline?category=linear` - historical candlesticks.

Canonical interval mapping:

- 5m -> `5`
- 15m -> `15`
- 1h -> `60`
- 4h -> `240`
- 1d -> `D`

Official documentation:

- `https://bybit-exchange.github.io/docs/v5/market/instrument`
- `https://bybit-exchange.github.io/docs/v5/market/tickers`
- `https://bybit-exchange.github.io/docs/v5/market/kline`

## Operational rule

Endpoint availability from documentation does not prove target-region reachability. Target VPS smoke tests remain mandatory before production use.
