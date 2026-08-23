# Provider Public Endpoint Baseline

Verified against current official provider documentation on 2026-08-23.

This file records the public REST and WebSocket contracts used by K-Trader. No account credentials are used.

## Binance USD-M Futures

REST base URL:

`https://fapi.binance.com`

REST endpoints:

- `GET /fapi/v1/exchangeInfo` - instrument/exchange metadata.
- `GET /fapi/v1/ticker/24hr` - 24h ticker statistics and quote/base turnover inputs.
- `GET /fapi/v1/ticker/bookTicker` - best bid/ask inputs.
- `GET /fapi/v1/klines` - historical candlesticks and reconciliation.

Public WebSocket base used by Phase 3:

`wss://fstream.binance.com/market/stream`

Kline stream subscription:

`{symbol}@kline_{interval}`

The provider adapter uses canonical 5m live input and preserves Binance quote volume, trade count and taker-buy fields from kline events.

Canonical REST/WS intervals used by K-Trader:

- 5m -> `5m`
- 15m -> `15m`
- 1h -> `1h`
- 4h -> `4h`
- 1d -> `1d`

Official documentation root:

`https://developers.binance.com/en/docs/products/derivatives-trading-usds-futures/Introduction`

## Bybit V5 Linear

REST base URL:

`https://api.bybit.com`

REST endpoints:

- `GET /v5/market/instruments-info?category=linear` - instrument metadata; pagination required because the linear universe can exceed the default page size.
- `GET /v5/market/tickers?category=linear` - ticker, turnover, volume, bid/ask and supported market fields.
- `GET /v5/market/kline?category=linear` - historical candlesticks and reconciliation.

Public Linear WebSocket:

`wss://stream.bybit.com/v5/public/linear`

Kline topic:

`kline.{interval}.{symbol}`

`confirm=true` is normalized as a closed candle. K-Trader sends an application-level `{"op":"ping"}` approximately every 20 seconds in addition to transport keepalive.

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
- `https://bybit-exchange.github.io/docs/v5/ws/connect`

## Operational rule

Published endpoint availability does not prove target-region or target-VPS reachability. REST and WebSocket smoke tests on the actual VPS remain mandatory before production use.
