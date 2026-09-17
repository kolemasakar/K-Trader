# K_AI -> K-Trader MT4 Market Context

Status: consumer contract staging only; remote transport not yet implemented or production-activated.

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

## Verified producer transport

The authoritative K_AI branch implements market-context acquisition locally:

`MT4BridgeAgent.acquire_market_context(run_id, symbol, market)`

The verified flow is:

`K_AI Python -> market_context_request.json -> MT4 Bridge -> market_context_<run_id>.json -> K_AI validation/import/archive`

The request contains separate configured `d1_bars`, `h1_bars`, `m15_bars`, and `m5_bars`. The response is validated atomically before canonical persistence.

No remote HTTP market-context endpoint is established by the inspected authoritative M15 implementation. K-Trader therefore must not assume `/v1/market-context/acquire`, a localhost service, bearer authentication, or any other remote protocol until such a transport is separately implemented and accepted.

## K-Trader boundary

K-Trader is a consumer only. This integration must not expose or invoke K_AI `OrderSend`, risk manager, local executor, authorization, `signal.json`, or broker execution paths.

`KAIMT4MarketContextAdapter` is intentionally transport-neutral at this stage. It accepts an already-delivered canonical payload, validates the K_AI contract, and returns the same payload unchanged. It does not initiate network traffic, access the K_AI workstation, or register itself as a live K-Trader provider.

## Schema handling

- schema `1.0`: exactly `D1/H1/M5`; accepted for backward-compatible read/replay;
- schema `1.1`: exactly `D1/H1/M15/M5` and canonical live transport;
- M15-dependent K-Trader flows must use `require_m15=True` and fail closed on schema `1.0`;
- K-Trader must never synthesize M15 from three M5 candles in this integration;
- canonical live bar depths are `D1=60`, `H1=200`, `M15=300`, `M5=300`;
- all scopes must contain `snapshot_id`, closed strictly chronological bars, exact `bar_depth == len(bars)`, and no duplicate timestamps.

K_AI `required_timeframes` for current Strategy A/Evidence may remain `D1/H1/M5`; that is a decision-scope setting and does not weaken the schema 1.1 transport requirement of exact `D1/H1/M15/M5` scopes.

## K-Trader validation hardening

Before a K_AI payload is accepted, the adapter fails closed on:

- unsupported schema or wrong exact scope set;
- schema `1.0` when `require_m15=True`;
- missing scope `snapshot_id`;
- schema `1.1` timestamp semantics other than `BROKER_SERVER_WALL_CLOCK_OPAQUE`;
- schema `1.1` with missing/non-null `utc_offset_minutes`;
- schema `1.1` source timestamps carrying `Z` or any UTC offset;
- canonical live bar-depth mismatch, including M15 depth other than `300`;
- missing, non-numeric or non-finite market facts;
- `ask < bid`, non-positive `point/tick_value/tick_size/contract_size`, negative `spread/stop_level/freeze_level`, or invalid `digits`;
- missing, non-numeric or non-finite OHLCV values;
- OHLC invariant violations;
- negative volume;
- duplicate or non-chronological bar timestamps;
- `latest_closed_bar_time` not matching the last supplied bar;
- `current_bar_time <= latest_closed_bar_time`.

These are validation-only checks. They do not transform strategy data, alter risk/execution rules, or authorize any broker action.

## Timestamp semantics

Schema 1.1 source timestamps are opaque broker-server wall-clock values:

- `time_source=BrokerServer`;
- `timestamp_semantics=BROKER_SERVER_WALL_CLOCK_OPAQUE`;
- `utc_offset_minutes=null`.

K-Trader must not interpret these values as UTC, append `Z`, fabricate a numeric offset, or convert them to an absolute instant. They are used only as coherent source-time facts under the producer contract.

Schema 1.0 remains backward-compatible and does not retroactively require the schema 1.1 timestamp metadata.

## Activation gate

This branch does not register `kai_mt4` in the production provider registry and does not change the active `binance_usdm` provider.

Activation requires, in order:

1. a separately defined and accepted read-only cross-system delivery transport from K_AI to K-Trader;
2. a live K_AI -> K-Trader end-to-end market-context acceptance using schema 1.1;
3. a separate explicit production-provider decision.

Until all three are complete, this integration remains consumer-contract staging only.