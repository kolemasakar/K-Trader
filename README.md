# K-Trader

K-Trader is a read-only, exchange-agnostic market scanner and analysis backend for a Custom GPT.

## v1 objective

Continuously collect confirmed public derivatives market data, normalize it, evaluate multi-timeframe structure, ATR, levels, traps and VSA, rank only high-quality setups, and expose structured results to K_Trader through a read-only HTTPS API.

## Principles

- Read-only in v1: no order placement, account access or exchange credentials.
- Exchange-agnostic core: Binance, Bybit, OKX, KuCoin and future providers are adapters, not the engine.
- One coherent market series per analysis; never mix OHLCV from different exchanges.
- Confirmed data only; stale or insufficient data produces NO TRADE.
- Capital preservation: quality over quantity; RR >= 3 for a tradable setup.
- Rule-based Setup Score in v1; statistical probability is deferred until calibrated from outcomes.

## Target flow

Public Exchange API -> Provider Adapter -> Normalized Market Data -> Universe/Liquidity -> ATR/MA -> Levels -> Trap -> VSA -> Setup Score -> A/A+ -> Signal -> Read-only API -> Custom GPT K_Trader

## Canonical documentation

- `ROADMAP.md`
- `REQUIREMENTS.md`
- `ARCHITECTURE.md`
- `custom_gpt/SYSTEM_K_TRADER_v1_1.md`
- `docs/*_SPEC.md`
- `docs/adr/*.md`

## Current phase

Phase 0 - Foundation and canonical specification.
