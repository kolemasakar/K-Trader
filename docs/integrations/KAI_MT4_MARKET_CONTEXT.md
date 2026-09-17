# K_AI -> K-Trader MT4 Market Context

Status: `LIVE_E2E_ACCEPTED / PROVIDER_NOT_ACTIVATED`.

## Decision

The bounded K_AI -> K-Trader MARKET_CONTEXT integration has passed authenticated live E2E acceptance. Phase 11G strategy semantics, frozen v2.2, holdout state, production trading state, and risk/execution logic remain unchanged.

This document does not authorize `kai_mt4` production-provider activation.

## Authoritative K_AI producer source

Repository: `kolemasakar/K_AI-Trading-System`.

The native-M15 implementation was developed and validated on `feature/native-m15-market-context-1.1`:

- architecture review: `b04ef2439fec48f13f85e3a056228f6614bb1f22`;
- implementation: `4ac4e5d5e3b35d6fb0dc2dda252e1b8eb0241b72`.

The repository integration incident is now closed. K_AI `main` contains the native-M15 implementation and subsequent bounded-delivery commits; verified `main` head on 2026-09-17 was `97d6f83e01b919c6e0ad36ac48674ff0af41787b`.

Producer validation remains anchored to the exact commits and recorded live runs rather than to an unpinned branch name.

Native-M15 validation recorded focused `45 passed`, active repository regression `358 passed`, MQ4 v1.9 compile `0 errors, 0 warnings`, runtime `alive_validation_only`, and run `M15LIVE_20260917_135101_433422` for `ETHUSDt` with native M15 depth/count `300`.

## Accepted delivery transport

K_AI acquisition path remains:

`K_AI Python -> market_context_request.json -> MT4 Bridge -> market_context_<run_id>.json -> K_AI validation/import/archive`.

Bounded delivery was added separately:

- boundary: `3e7895e9e74f0f4f9728e92d35ad6b26626a344f`;
- delivery service: `160713e3bdf31010b994a8e515e58820d58b8c90`;
- delivery acceptance/docs: `1c3c9e4eaf0611e28ac4e8ee430e05c19413c13e`.

Accepted live path:

`MT4 -> K_AI schema 1.1 -> 127.0.0.1:8765 -> restricted reverse SSH -> 127.0.0.1:18765 -> K-Trader validator`.

Transport surface:

- `GET /health`;
- authenticated `POST /v1/market-context/acquire`;
- HTTP Bearer token from protected runtime secret `KAI_MARKET_CONTEXT_DELIVERY_TOKEN`;
- immutable canonical MARKET_CONTEXT response only;
- `execution_surface=false`;
- no generic RPC, filesystem, strategy, risk or execution action surface.

Live K-Trader acceptance: workflow run `35236593165`, acquisition `MCTXDELIVERY_20260917_175430_125595_02F8FF75`, result `PASS`.

## K-Trader boundary

K-Trader is a read-only market-context consumer for this integration. It must not expose or invoke K_AI `OrderSend`, risk manager, local executor, authorization, `signal.json`, or broker execution paths.

`KAIMT4MarketContextAdapter` validates canonical payloads and returns the accepted payload unchanged. It is exported as an adapter but is not registered in the production provider registry.

## Schema handling

- schema `1.0`: exactly `D1/H1/M5`; backward-compatible read/replay only;
- schema `1.1`: exactly `D1/H1/M15/M5` for the canonical live path;
- M15-dependent K-Trader flows use `require_m15=True` and fail closed on schema `1.0`;
- K-Trader never synthesizes M15 from three M5 candles;
- canonical depths: `D1=60`, `H1=200`, `M15=300`, `M5=300`;
- all scopes require `snapshot_id`, exact depth, closed strictly chronological bars, and unique timestamps.

## Validation hardening

The adapter fails closed on:

- unsupported schema or wrong exact scope set;
- schema `1.0` when M15 is required;
- missing scope snapshot ID;
- wrong/missing opaque timestamp semantics;
- non-null/fabricated UTC offset semantics;
- source timestamps carrying `Z` or numeric offsets in schema `1.1`;
- canonical depth mismatch;
- malformed, non-numeric or non-finite market facts/OHLCV;
- `ask < bid`;
- invalid `point`, `tick_value`, `tick_size`, `contract_size`, `spread`, `stop_level`, `freeze_level`, or `digits`;
- OHLC invariant violation or negative volume;
- duplicate/non-chronological timestamps;
- `latest_closed_bar_time` mismatch;
- `current_bar_time <= latest_closed_bar_time`.

Live negative contract smoke: `6/6 PASS`.

## Timestamp semantics

Schema `1.1` source timestamps are opaque broker-server wall-clock values:

- `time_source=BrokerServer`;
- `timestamp_semantics=BROKER_SERVER_WALL_CLOCK_OPAQUE`;
- `utc_offset_minutes=null`.

K-Trader must not interpret them as UTC, append `Z`, fabricate a numeric offset, or convert them to an absolute instant.

## Current gate

Completed:

- native M15 implementation/validation;
- bounded read-only delivery transport;
- protected credential wiring;
- authenticated live `K_AI -> K-Trader` E2E;
- negative fail-closed validation.

Still separate and not authorized by this integration acceptance:

- merge of PR #60 into `research-strategy-benchmark-v1`;
- registration/activation of `kai_mt4` as a production provider;
- any strategy, risk, execution, holdout or broker-trading change.

Canonical acceptance checkpoint: `docs/checkpoints/2026-09-17_KAI_MT4_LIVE_E2E_ACCEPTANCE.md`.
