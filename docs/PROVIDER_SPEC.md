# Provider Specification v1.1

## Interface

A `MarketDataProvider` SHALL provide normalized access to:

- provider identity and health;
- instrument discovery;
- ticker/liquidity data;
- historical candles;
- live public market streams in later phases;
- instrument specifications;
- provider capability metadata.

## Canonical vs native symbol

`NormalizedInstrument.symbol` is the canonical symbol used by provider-independent engine code.

`NormalizedInstrument.provider_symbol` is the native exchange identifier used only by the adapter.

Example future mapping:

- canonical: `BTCUSDT`
- OKX native: `BTC-USDT-SWAP`

Engine modules SHALL NOT construct provider-native identifiers themselves.

Historical candle requests therefore receive the normalized instrument and the adapter resolves `provider_symbol`.

## Capability declaration

Adapters explicitly declare support/absence for:

- perpetual derivatives;
- supported intervals;
- quote volume;
- trade count;
- taker-buy fields;
- book ticker;
- open interest;
- WebSocket candle stream;
- REST page limits relevant to scheduler design.

Unsupported optional data returns null/unsupported, never inferred.

## Implemented Phase 1 adapters

### `binance_usdm`

- public market-data only;
- USDT perpetual discovery through normalized exchange metadata;
- 24h ticker/quote turnover;
- best bid/ask input;
- historical klines for canonical 5m/15m/1h/4h/1d;
- native kline trade count and taker-buy fields retained when available.

### `bybit_linear`

- public market-data only;
- paginated linear instrument discovery;
- USDT perpetual normalization;
- 24h turnover/volume, bid/ask and open-interest fields when returned;
- historical klines for canonical 5m/15m/1h/4h/1d;
- unavailable kline trade-count/taker-buy fields remain null.

## Initial future provider candidates

- OKX USDT-margined SWAP
- KuCoin Futures
- other public derivatives providers satisfying the same contract

Provider priority is configuration, not architecture.

## Fallback

Fallback is triggered only by defined health/freshness policy. On fallback, bootstrap a complete coherent snapshot from the selected provider. Never splice provider histories.

## Acceptance

Offline contract acceptance is complete for Binance USD-M and Bybit Linear.

Target-VPS live endpoint acceptance remains pending until the VPS exists. Mock tests SHALL NOT be presented as proof of regional provider reachability.
