# K-Trader

K-Trader is a read-only, exchange-agnostic market scanner and analysis backend for a Custom GPT.

## v1 objective

Collect confirmed public derivatives market data, normalize and validate it, maintain MTF history/live state, evaluate indicators/structure/traps/VSA, build deterministic setup geometry/scoring, run an autonomous scanner, and expose high-quality read-only results to K_Trader through HTTPS.

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

Public Exchange API -> REST/WS Provider -> Normalized Data -> Validation/SQLite -> Universe/Liquidity -> ATR/MA -> Structure/Levels -> Trap -> VSA -> Setup Geometry -> Setup Score -> TradingDecision -> Runtime Coordinator -> Read-only API -> Custom GPT

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

- Wilder ATR14 and canonical ATR5D;
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

- canonical setup types;
- STRONG confirmed/mirror primary-level hard gate;
- confirmation-based Entry + luft;
- structural Stop and nearest confirmed opposing Target;
- no synthetic 3R target;
- RR >=3 hard gate;
- UTC-day ATR-used rule;
- deterministic 100-point Setup Score;
- A+/A/B/C and hard-reject override;
- optional explicit risk sizing;
- final `TradingDecision`.

### Phase 8 - Read-only API

- FastAPI read-only service;
- `GET /health`;
- `GET /v1/scanner/status`;
- `GET /v1/universe`;
- `GET /v1/market/{symbol}`;
- `GET /v1/candles/{symbol}`;
- `GET /v1/analysis/{symbol}`;
- `GET /v1/candidates`;
- `GET /v1/signals`;
- internal thread-safe `ApiReadModel`;
- Decimal values serialized as exact strings;
- UTC ISO-8601 timestamps;
- provider ambiguity returns HTTP 409;
- candle provenance `provider|aggregate`;
- rate-limit baseline;
- `custom_gpt/openapi.yaml` and `ACTION_GUIDE.md`.

## Runtime correction

Repository audit after Phase 8 found that the original roadmap omitted the application-level coordinator required to continuously compose Phases 1-7 and publish results into the API.

Therefore **Phase 8.5 - Runtime Scanner Coordinator** is required before Docker/VPS deployment.

It will connect:

provider -> universe -> data readiness -> indicators -> structure -> Trap/VSA -> Trading Engine -> ranked decisions -> `ApiReadModel`.

## Verification

- Phase 1: 7 deterministic tests.
- Phase 2: 9 deterministic tests.
- Phase 3: 10 deterministic tests.
- Phase 4: 12 deterministic tests.
- Phase 5: 12 deterministic tests.
- Phase 6: 14 deterministic tests.
- Phase 7: 17 isolated exact-module checks.
- Phase 8: 7 isolated API tests.

Repository-wide pytest/CI and real target-VPS REST/WS acceptance remain Phase 9 gates.

## Development API

After dependencies are installed:

`PYTHONPATH=src uvicorn ktrader.api.app:app --host 127.0.0.1 --port 8000`

The default process starts with an empty/degraded read model until the runtime coordinator publishes scanner state.

## Smoke utilities

REST provider:

`PYTHONPATH=src python scripts/provider_smoke.py --providers binance_usdm bybit_linear`

WebSocket:

`PYTHONPATH=src python scripts/ws_smoke.py --provider binance_usdm --symbol BTCUSDT`

No exchange credentials are used.

## Canonical documentation

- `ROADMAP.md`
- `REQUIREMENTS.md`
- `ARCHITECTURE.md`
- `custom_gpt/SYSTEM_K_TRADER_v1_1.md`
- `custom_gpt/openapi.yaml`
- `custom_gpt/ACTION_GUIDE.md`
- `docs/*_SPEC.md`
- `docs/PHASE_*_CHECKPOINT.md`
- `docs/adr/*.md`

## Current phase

Phase 8 implementation complete.

Next required checkpoint: Phase 8.5 - Runtime Scanner Coordinator.
