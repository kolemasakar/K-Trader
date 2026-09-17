# K_AI -> K-Trader MT4 Market Context

Status: integration staging only; not production-activated.

## Decision

The owner explicitly interrupted the 2026-09-17 data-only development pause for this bounded integration change. Phase 11G strategy semantics, frozen v2.2, holdout state, production trading state, and risk/execution logic remain unchanged.

## Boundary

Data flow:

`MT4 -> K_AI MT4 Bridge -> K_AI market-context API -> K-Trader KAIMT4MarketContextAdapter`

K-Trader is a consumer only. This integration must not expose or invoke K_AI `OrderSend`, risk manager, local executor, authorization, `signal.json`, or broker execution paths.

## K_AI API contract

Expected private endpoint:

`POST /v1/market-context/acquire`

Request body contains only `symbol` and `market`. K_AI owns `run_id`, acquisition, MT4 validation, canonical persistence and archive selection. A successful response is the validated canonical `MARKET_CONTEXT` payload, not a newly transformed OHLCV copy.

The adapter defaults to `KAI_MT4_BASE_URL=http://127.0.0.1:8765`; optional bearer authentication uses `KAI_MT4_API_TOKEN`. The intended deployment transport is private; no public HP-OMEN listener is required.

## Schema handling

- schema `1.0`: exactly `D1/H1/M5`; accepted only for backward-compatible consumers;
- schema `1.1`: exactly `D1/H1/M15/M5`;
- M15-dependent K-Trader flows must call with `require_m15=True` and fail closed on schema `1.0`;
- K-Trader must never synthesize M15 from three M5 candles in this integration;
- all scopes must contain closed, strictly chronological bars with `bar_depth == len(bars)`.

## K-Trader validation hardening

Before a K_AI payload is accepted, the adapter fails closed on:

- missing, non-numeric or non-finite market facts;
- `ask < bid`, non-positive `point/tick_value/tick_size/contract_size`, negative `spread/stop_level/freeze_level`, or invalid `digits`;
- missing, non-numeric or non-finite OHLCV values;
- OHLC invariant violations (`high` below open/close/low or `low` above open/close/high);
- negative volume;
- duplicate or non-chronological bar timestamps;
- `latest_closed_bar_time` not matching the last supplied bar;
- `current_bar_time <= latest_closed_bar_time`;
- mixed timezone-aware and timezone-naive values inside one scope.

These are validation-only checks. They do not register the provider, transform the strategy, alter risk/execution rules or authorize any broker action.

## Timestamp semantics

Current K_AI/MT4 timestamps are broker-server wall-clock values and do not carry a UTC offset. K-Trader therefore treats them as source timestamps and does not silently relabel them as UTC. Schema 1.1 should make timezone/offset semantics explicit when K_AI can do so reliably.

## Activation gate

This branch does not register `kai_mt4` in the production provider registry and does not change the active `binance_usdm` provider. Activation requires a separate explicit decision after K_AI schema 1.1 and a live end-to-end market-context acceptance test are available.
