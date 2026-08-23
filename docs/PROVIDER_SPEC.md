# Provider Specification v1.0

## Interface

A `MarketDataProvider` SHALL provide normalized access to:

- provider identity and health;
- instrument discovery;
- ticker/liquidity data;
- historical candles;
- live public market streams;
- instrument specifications;
- provider capability metadata.

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
- native higher-timeframe candles;
- REST/WS limits relevant to scheduler design.

Unsupported optional data returns null/unsupported, never inferred.

## Initial provider candidates

- Binance USD-M Futures
- Bybit Linear Perpetual
- OKX USDT-margined SWAP
- KuCoin Futures

Provider priority is configuration, not architecture.

## Fallback

Fallback is triggered only by defined health/freshness policy. On fallback, bootstrap a complete coherent snapshot from the selected provider. Never splice provider histories.

## Acceptance

Phase 1 is not complete until two independent adapters pass the same provider contract tests and return normalized equivalent objects.
