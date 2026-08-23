# K-Trader

K-Trader is a read-only, exchange-agnostic market scanner and analysis backend for a Custom GPT.

## v1 objective

Continuously collect confirmed public derivatives market data, normalize it, validate and persist multi-timeframe history, evaluate structure/ATR/levels/traps/VSA, rank only high-quality setups, and expose structured results to K_Trader through a read-only HTTPS API.

## Principles

- Read-only in v1: no order placement, account access or exchange credentials.
- Exchange-agnostic core: Binance, Bybit, OKX, KuCoin and future providers are adapters, not the engine.
- One coherent market series per analysis; never mix OHLCV from different exchanges.
- Canonical symbol and native `provider_symbol` are separate concepts.
- Confirmed data only; stale, gapped or insufficient data fails closed.
- UTC is canonical for candle storage and aggregation.
- Capital preservation: quality over quantity; RR >= 3 for a tradable setup.
- Rule-based Setup Score in v1; statistical probability is deferred until calibrated from outcomes.

## Target flow

Public Exchange API -> Provider Adapter -> Normalized Market Data -> Validation/SQLite -> Universe/Liquidity -> ATR/MA -> Levels -> Trap -> VSA -> Setup Score -> A/A+ -> Signal -> Read-only API -> Custom GPT K_Trader

## Current implementation

Phase 1 provider foundation:

- `MarketDataProvider` contract and capability model;
- normalized instrument/ticker/candle models;
- Binance USD-M and Bybit Linear public REST adapters;
- provider fallback without cross-provider data fusion;
- configurable price filter and liquidity ranking.

Phase 2 market-data core:

- REST bootstrap for `1d/4h/1h/15m/5m`;
- default closed-history depth `250/250/250/250/300`;
- UTC boundary/OHLCV/gap/freshness validation;
- SQLite WAL persistence;
- Decimal-preserving storage;
- idempotent candle upsert;
- atomic MTF snapshot writes;
- bootstrap SUCCESS/FAILED audit records.

Verification:

- Phase 1 contract suite: 7 tests passed.
- Phase 2 isolated deterministic harness: 9 tests passed; compileall PASS.
- Target-VPS live provider/bootstrap acceptance remains pending until the VPS exists.

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
- `docs/PHASE_2_CHECKPOINT.md`
- `docs/adr/*.md`

## Current phase

Phase 2 - implementation complete; target-VPS live acceptance pending.
