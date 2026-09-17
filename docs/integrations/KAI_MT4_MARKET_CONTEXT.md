# K_AI -> K-Trader MT4 Market Context

Status: integration staging only; not production-activated.

## Decision

The owner explicitly interrupted the 2026-09-17 data-only development pause for this bounded integration change. Phase 11G strategy semantics, frozen v2.2, holdout state, production trading state, and risk/execution logic remain unchanged.

## Authoritative K_AI producer source

For the native M15 upgrade, do not use K_AI `main` as source of truth yet.

- repository: `kolemasakar/K_AI-Trading-System`;
- authoritative branch: `feature/native-m15-market-context-1.1`;
- architecture review commit: `b04ef2439fec48f13f85e3a056228f6614bb1f22`;
- implementation commit: `4ac4e5d5e3b35d6fb0dc2dda252e1b8eb0241b72`;
- producer `main` remains outside this upgrade until its repository-integration incident is resolved.

The producer completion record reports focused `45 passed`, active repository regression `358 passed`, MQ4 v1.9 compile `0 errors, 0 warnings`, runtime `alive_validation_only`, and live broker-disabled validation run `M15LIVE_20260917_135101_433422` for `ETHUSDt` with imported `D1/H1/M15/M5` and native M15 depth/count `300`.

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

- schema `1.0`: exactly `D1/H1/M5`; accepted for backward-compatible read/replay;
- schema `1.1`: exactly `D1/H1/M15/M5` and canonical live transport;
- M15-dependent K-Trader flows must call with `require_m15=True` and fail closed on schema `1.0`;
- K-Trader must never synthesize M15 from three M5 candles in this integration;
- canonical live bar depths are `D1=60`, `H1=200`, `M15=300`, `M5=300`;
- all scopes must contain closed, strictly chronological bars with `bar_depth == len(bars)` and no duplicate timestamps.

K_AI `required_timeframes` for current Strategy A/Evidence may remain `D1/H1/M5`; that is a decision-scope setting and does not weaken the schema 1.1 transport requirement of exact `D1/H1/M15/M5` scopes.

## K-Trader validation hardening

Before a K_AI payload is accepted, the adapter fails closed on:

- unsupported schema or wrong exact scope set;
- schema `1.0` when `require_m15=True`;
- schema `1.1` timestamp semantics other than `BROKER_SERVER_WALL_CLOCK_OPAQUE`;
- schema `1.1` with missing/non-null `utc_offset_minutes`;
- schema `1.1` source timestamps carrying `Z` or any UTC offset;
- canonical live bar-depth mismatch, including M15 depth other than `300`;
- missing, non-numeric or non-finite market facts;
- `ask < bid`, non-positive `point/tick_value/tick_size/contract_size`, negative `spread/stop_level/freeze_level`, or invalid `digits`;
- missing, non-numeric or non-finite OHLCV values;
- OHLC invariant violations (`high` below open/close/low or `low` above open/close/high);
- negative volume;
- duplicate or non-chronological bar timestamps;
- `latest_closed_bar_time` not matching the last supplied bar;
- `current_bar_time <= latest_closed_bar_time`.

These are validation-only checks. They do not register the provider, transform the strategy, alter risk/execution rules or authorize any broker action.

## Timestamp semantics

Schema 1.1 source timestamps are opaque broker-server wall-clock values:

- `time_source=BrokerServer`;
- `timestamp_semantics=BROKER_SERVER_WALL_CLOCK_OPAQUE`;
- `utc_offset_minutes=null`.

K-Trader must not interpret these values as UTC, append `Z`, fabricate a numeric offset, or convert them to an absolute instant. They are used only as coherent source-time ordering/freshness facts within the producer contract.

Schema 1.0 remains backward-compatible and does not retroactively require the schema 1.1 timestamp metadata.

## Activation gate

This branch does not register `kai_mt4` in the production provider registry and does not change the active `binance_usdm` provider. Production activation requires a separate explicit decision after a K_AI -> K-Trader live end-to-end market-context acceptance test passes against the authoritative schema 1.1 producer implementation.
