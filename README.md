# K-Trader

K-Trader is a read-only, exchange-agnostic market scanner and analysis backend for a Custom GPT.

## v1 objective

Collect confirmed public derivatives market data, normalize and validate it, maintain MTF history/live state, evaluate indicators/structure/traps/VSA, build deterministic setup geometry and scoring, and expose only high-quality read-only results to K_Trader.

## Principles

- Read-only v1: no order placement, account access or exchange credentials.
- Exchange-agnostic core: Binance, Bybit, OKX, KuCoin and future providers are adapters, not the engine.
- Never mix OHLCV series across providers.
- Confirmed source data only; stale/gapped/insufficient context fails closed.
- UTC is canonical for storage/aggregation.
- Open live candles are provisional only.
- Quality > quantity; `NO_TRADE` is preferred to weak setup.
- RR >=3 for tradable setup.
- Setup Score is rule-based, not statistical probability.

## Target flow

Public Exchange API -> REST/WS Provider -> Normalized Data -> Validation/SQLite -> Universe/Liquidity -> ATR/MA -> Structure/Levels -> Trap -> VSA -> Setup Geometry -> Setup Score -> A/A+ -> TradingDecision -> Read-only API -> Custom GPT

## Implemented phases

### Phase 1 - Provider foundation

- exchange-agnostic provider contract;
- Binance USD-M + Bybit Linear public adapters;
- public REST history, symbols/tickers, price/liquidity filtering and fallback.

### Phase 2 - Market-data core

- `1d/4h/1h/15m/5m` bootstrap;
- SQLite WAL;
- UTC/gap/freshness validation;
- atomic MTF persistence.

### Phase 3 - Live market data

- Binance/Bybit public WebSocket;
- 5m base stream;
- local 15m/1h/4h/1d aggregation;
- stale/reconnect/REST reconciliation/gap recovery.

### Phase 4 - Indicators

- Wilder ATR14;
- canonical ATR5D;
- SMA/EMA MA50/200;
- relative volume/spread;
- ATR-used helper.

### Phase 5 - Market structure

- swing structure and MTF regime;
- directional strength;
- DST-aware sessions;
- confirmed MTF levels and lifecycle.

### Phase 6 - Trap + VSA

- failed-break/return/confirmation trap engine;
- ND/NS/T/UT/BC/SC/SV;
- HTF/location/confirmation hard filters.

### Phase 7 - Setup / Rating Engine

- three canonical setup types;
- confirmed-evidence identity matching;
- STRONG confirmed/mirror primary-level hard gate;
- Entry trigger from confirmation bar;
- luft = `max(1 tick, 0.02 * ATR14)`;
- structural Stop using level/sweep extreme;
- nearest confirmed opposing structural Target;
- no synthetic 3R target;
- RR >=3 hard gate;
- ATR-used based on UTC-day directional extreme -> proposed Entry;
- deterministic 100-point Setup Score;
- A+ >=90, A >=80, B >=70, C <70;
- hard reject -> C / public score <=69 / NO_TRADE;
- optional explicit account-risk sizing;
- final `TradingDecision`.

## Verification

- Phase 1: 7 deterministic tests.
- Phase 2: 9 deterministic tests.
- Phase 3: 10 deterministic tests.
- Phase 4: 12 deterministic tests.
- Phase 5: 12 deterministic tests.
- Phase 6: 14 deterministic tests.
- Phase 7: 17 exact-module isolated checks; repository test file committed.

Repository-wide pytest/CI and real target-VPS REST/WS acceptance are Phase 9 gates and are not yet claimed.

## Smoke utilities

REST:

`PYTHONPATH=src python scripts/provider_smoke.py --providers binance_usdm bybit_linear`

WebSocket:

`PYTHONPATH=src python scripts/ws_smoke.py --provider binance_usdm --symbol BTCUSDT`

or

`PYTHONPATH=src python scripts/ws_smoke.py --provider bybit_linear --symbol BTCUSDT`

No exchange credentials are used.

## Canonical documentation

- `ROADMAP.md`
- `REQUIREMENTS.md`
- `ARCHITECTURE.md`
- `custom_gpt/SYSTEM_K_TRADER_v1_1.md`
- `docs/*_SPEC.md`
- `docs/PHASE_*_CHECKPOINT.md`
- `docs/adr/*.md`

## Current phase

Phase 7 implementation complete.

Next: Phase 8 - read-only FastAPI/OpenAPI layer for Custom GPT integration.
