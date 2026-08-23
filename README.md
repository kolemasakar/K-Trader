# K-Trader

K-Trader is a read-only, exchange-agnostic market scanner and analysis backend for a Custom GPT.

## v1 objective

Continuously collect confirmed public derivatives market data, normalize it, validate and persist multi-timeframe history/live state, evaluate indicators, market structure, levels, traps and VSA, rank only high-quality setups, and expose structured results to K_Trader through a read-only HTTPS API.

## Principles

- Read-only in v1: no order placement, account access or exchange credentials.
- Exchange-agnostic core: Binance, Bybit, OKX, KuCoin and future providers are adapters, not the engine.
- One coherent market series per analysis; never mix OHLCV from different exchanges.
- Canonical symbol and native `provider_symbol` are separate concepts.
- Confirmed data only; stale, gapped or insufficient data fails closed.
- UTC is canonical for candle storage and aggregation.
- Open live candles are provisional and never treated as closed confirmations.
- Capital preservation: quality over quantity; RR >= 3 for a tradable setup.
- Rule-based Setup Score in v1; statistical probability is deferred until calibrated from outcomes.

## Target flow

Public Exchange API -> REST/WS Provider Adapter -> Normalized Market Data -> Validation/SQLite -> Universe/Liquidity -> ATR/MA -> Market Structure/Levels -> Trap -> VSA -> Setup Score -> A/A+ -> Signal -> Read-only API -> Custom GPT K_Trader

## Current implementation

### Phase 1 - provider foundation

- `MarketDataProvider` contract and capability model;
- normalized instrument/ticker/candle models;
- Binance USD-M and Bybit Linear public REST adapters;
- provider fallback without cross-provider data fusion;
- configurable price filter and liquidity ranking.

### Phase 2 - market-data core

- REST bootstrap for `1d/4h/1h/15m/5m`;
- default closed-history depth `250/250/250/250/300`;
- UTC boundary/OHLCV/gap/freshness validation;
- SQLite WAL persistence and Decimal-preserving storage;
- atomic MTF snapshot writes and bootstrap audit.

### Phase 3 - live market data

- Binance USD-M and Bybit Linear public WebSocket candle streams;
- canonical live base interval `5m`;
- open candle held in memory only;
- provider-confirmed closed 5m persistence;
- complete UTC aggregation to `15m/1h/4h/1d`;
- source provenance (`provider` vs `aggregate`);
- stale detection, reconnect, REST reconciliation and gap recovery;
- target-VPS WebSocket smoke utility.

### Phase 4 - indicators

- provider-independent True Range and Wilder ATR14;
- canonical D1 ATR5D with abnormal-range filtering and no rejected-bar replacement;
- configurable SMA/EMA with v1 MA50/200 baseline `sma`;
- 20-bar previous-only volume and VSA candle-spread baselines;
- relative volume/quote-volume/spread;
- generic ATR-used calculation with 40/80% classifications;
- ATR-used move origin reserved for Phase 7 Trading Engine rules.

### Phase 5 - market structure

- deterministic swing-point detection;
- regime from swing structure plus MA50/200 alignment;
- MTF regime precedence across `1d/4h/1h`;
- strength evidence from structure, MA alignment and configured participation threshold;
- DST-aware Tokyo/London/New York session context for 24/7 crypto;
- historical swing-level clustering into ATR-scaled zones;
- FLOATING/CONFIRMED/BROKEN/MIRROR/INVALIDATED lifecycle;
- trend-break and mirror lifecycle evidence;
- consolidation-zone detector;
- MTF level priority and nearest confirmed support/resistance lookup;
- `LIMIT` and `PARANORMAL_BAR` remain explicit evidence inputs rather than invented automatic geometry.

## Verification

- Phase 1 contract suite: 7 tests passed.
- Phase 2 deterministic harness: 9 tests passed; compileall PASS.
- Phase 3 deterministic harness: 10 tests passed; compileall PASS.
- Phase 4 deterministic harness: 12 tests passed; compileall PASS.
- Phase 5 local isolated harness: 12 tests passed; syntax/compile validation PASS.
- Target-VPS REST/bootstrap/WebSocket acceptance remains pending until the VPS exists.

## Smoke utilities

REST provider:

`PYTHONPATH=src python scripts/provider_smoke.py --providers binance_usdm bybit_linear`

WebSocket:

`PYTHONPATH=src python scripts/ws_smoke.py --provider binance_usdm --symbol BTCUSDT`

or:

`PYTHONPATH=src python scripts/ws_smoke.py --provider bybit_linear --symbol BTCUSDT`

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
- `docs/PHASE_3_CHECKPOINT.md`
- `docs/PHASE_4_CHECKPOINT.md`
- `docs/PHASE_5_CHECKPOINT.md`
- `docs/adr/*.md`

## Current phase

Phase 5 - implementation complete. Target-VPS acceptance for Phases 1-3 remains pending until deployment.
