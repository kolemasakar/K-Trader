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

## Implemented

### Phase 1-3 - Market data

- exchange-agnostic provider contract;
- Binance USD-M + Bybit Linear public REST/WS adapters;
- universe/liquidity filtering and provider fallback;
- MTF bootstrap `1d/4h/1h/15m/5m`;
- SQLite WAL, UTC/gap/freshness validation;
- live 5m state, MTF aggregation, reconnect and REST reconciliation.

### Phase 4-7 - Analysis engine

- Wilder ATR14 and canonical ATR5D;
- MA50/200 and relative volume/spread;
- MTF regime/strength/sessions/levels;
- Trap + ND/NS/T/UT/BC/SC/SV;
- canonical setup geometry, RR/ATR hard gates, Setup Score and A+/A/B/C;
- final `TradingDecision`.

### Phase 8 - Read-only API

- FastAPI endpoints for health/status/universe/market/candles/analysis/candidates/signals;
- thread-safe `ApiReadModel`;
- exact Decimal strings and UTC timestamps;
- provider ambiguity fail-closed behavior;
- rate limiting;
- Custom GPT OpenAPI/Action guide.

### Phase 8.5 - Runtime Scanner Coordinator

- autonomous provider -> universe -> data readiness -> indicators -> structure -> Trap/VSA -> Trading Engine flow;
- configurable top-N liquidity shortlist;
- bounded bootstrap/analysis concurrency;
- retained live WebSocket task unless provider/shortlist changes;
- per-symbol failure isolation;
- explicit `NO_SETUP` -> `NO_TRADE` sentinel for valid/fresh symbols without setup;
- no fabricated decision for stale/incomplete data;
- atomic read-model publication;
- `provider|aggregate|mixed` series provenance;
- expanded runtime health/status;
- production entrypoint `ktrader.runtime.app:app`.

## Verification status

- Phase 1: 7 deterministic tests.
- Phase 2: 9 deterministic tests.
- Phase 3: 10 deterministic tests.
- Phase 4: 12 deterministic tests.
- Phase 5: 12 deterministic tests.
- Phase 6: 14 deterministic tests.
- Phase 7: 17 isolated exact-module checks.
- Phase 8: 7 isolated API tests.
- Phase 8.5 orchestration tests are committed but are not yet claimed as executed.

Repository-wide pytest/CI is the first mandatory Phase 9 gate. Real target-VPS REST/WS acceptance also remains Phase 9.

## Runtime entrypoint

`PYTHONPATH=src uvicorn ktrader.runtime.app:app --host 127.0.0.1 --port 8000`

The legacy API-only entrypoint remains available for isolated API development:

`PYTHONPATH=src uvicorn ktrader.api.app:app --host 127.0.0.1 --port 8000`

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

Phase 8.5 implementation complete.

Next: Phase 9 - repository-wide CI, Docker/VPS deployment and live acceptance.
