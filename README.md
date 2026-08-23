# K-Trader

K-Trader is a read-only, exchange-agnostic market scanner and analysis backend for a Custom GPT.

## v1 objective

Continuously collect confirmed public derivatives market data, normalize it, evaluate multi-timeframe structure, ATR, levels, traps and VSA, rank only high-quality setups, and expose structured results to K_Trader through a read-only HTTPS API.

## Principles

- Read-only in v1: no order placement, account access or exchange credentials.
- Exchange-agnostic core: Binance, Bybit, OKX, KuCoin and future providers are adapters, not the engine.
- One coherent market series per analysis; never mix OHLCV from different exchanges.
- Canonical symbol and native `provider_symbol` are separate concepts.
- Confirmed data only; stale or insufficient data produces NO TRADE.
- Capital preservation: quality over quantity; RR >= 3 for a tradable setup.
- Rule-based Setup Score in v1; statistical probability is deferred until calibrated from outcomes.

## Target flow

Public Exchange API -> Provider Adapter -> Normalized Market Data -> Universe/Liquidity -> ATR/MA -> Levels -> Trap -> VSA -> Setup Score -> A/A+ -> Signal -> Read-only API -> Custom GPT K_Trader

## Current implementation

Phase 1 provider foundation is implemented with:

- `MarketDataProvider` contract and capability model;
- normalized instrument/ticker/candle models;
- Binance USD-M public REST adapter;
- Bybit Linear public REST adapter;
- provider fallback without cross-provider data fusion;
- configurable price filter and liquidity ranking;
- offline contract/pagination/failover/universe tests.

Local verification: `7 passed` plus Python compileall PASS.

Live regional/API acceptance remains intentionally pending until the target VPS is available.

## Provider smoke test

`PYTHONPATH=src python scripts/provider_smoke.py --providers binance_usdm bybit_linear`

No exchange credentials are used.

## Canonical documentation

- `ROADMAP.md`
- `REQUIREMENTS.md`
- `ARCHITECTURE.md`
- `custom_gpt/SYSTEM_K_TRADER_v1_1.md`
- `docs/*_SPEC.md`
- `docs/PROVIDER_ENDPOINTS.md`
- `docs/PHASE_1_CHECKPOINT.md`
- `docs/adr/*.md`

## Current phase

Phase 1 - implementation complete; live VPS acceptance pending.
