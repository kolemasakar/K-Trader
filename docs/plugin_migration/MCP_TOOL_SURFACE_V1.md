# K-Trader MCP / App Tool Surface v1

Status: **IMPLEMENTATION-READY SPEC / READ-ONLY / NO CUTOVER AUTHORIZED**

Date: 2026-09-16

This document defines a packaging-neutral typed tool surface for a future K-Trader Plugin App/Connector/MCP adapter. It is derived from the accepted read-only backend OpenAPI contract and `INTEGRATION_CONTRACT_V1.md`.

It does not select a final ChatGPT packaging format, authentication product, hosting model, or deployment mechanism.

## Global invariants

- backend authority remains `https://ktrader-api.duckdns.org`;
- all tools are read-only;
- no order/create/update/delete/cancel capability;
- no exchange-account capability;
- no generic HTTP proxy;
- no arbitrary shell/filesystem capability;
- provider ambiguity fails closed;
- backend freshness/readiness/errors are preserved;
- no adapter-side trading logic;
- no credential is stored in the skill;
- bounded list/candle limits are mandatory;
- timestamps are UTC/backend-owned;
- `NO_TRADE` is a valid canonical result and must not be converted to an integration failure;
- integration failure must not be converted to LONG/SHORT trade advice.

## Tool 1 — `ktrader_health`

Backend mapping: `GET /health` (`getHealth`)

Authentication: none on the current backend contract.

Parameters: none.

Required response semantics:

- `status`;
- `mode` — expected `read_only`;
- `api_version`;
- `data_ready`;
- `scanner_status`;
- `provider_id` when available;
- `action_auth_enabled`;
- `generated_at`.

The adapter must not treat scanner `DEGRADED` as equivalent to API outage when the backend reports health `ok`.

## Tool 2 — `ktrader_scanner_status`

Backend mapping: `GET /v1/scanner/status` (`getScannerStatus`)

Parameters: none.

Required response semantics include:

- `status`;
- `provider_id`;
- `universe_size`;
- `data_ready`;
- `last_scan_at`;
- `last_error`;
- `cycle_id`;
- `symbols_ready` / `symbols_failed`;
- `live_streaming`;
- `last_cycle_duration_seconds`;
- `started_at`.

Failure mapping:

- `401` -> authentication failure, never `NO_TRADE`.

## Tool 3 — `ktrader_list_universe`

Backend mapping: `GET /v1/universe` (`listUniverse`)

Parameters:

- `provider_id?: string` — required by backend semantics when canonical-symbol/provider ambiguity exists;
- `limit?: integer` — range `1..200`, default `50`.

Response:

- `count`;
- `provider_id` when applicable;
- `items[]` preserving canonical/provider symbol, market type, contract type, status, price/liquidity/provenance/freshness fields.

The adapter must not silently choose a provider where the backend requires disambiguation.

## Tool 4 — `ktrader_market_snapshot`

Backend mapping: `GET /v1/market/{symbol}` (`getMarketSnapshot`)

Parameters:

- `symbol: string` — canonical K-Trader symbol;
- `provider_id?: string`.

Response preserves the backend `UniverseCandidate` semantics, including provider identity, market type, prices, spread/liquidity fields, `data_time`, and `data_age_seconds`.

Failure mapping:

- `401` -> authentication failure;
- `404` -> symbol/snapshot unavailable;
- `409` -> provider ambiguity; caller must retry with explicit `provider_id`.

## Tool 5 — `ktrader_candles`

Backend mapping: `GET /v1/candles/{symbol}` (`getCandles`)

Parameters:

- `symbol: string`;
- `provider_id?: string`;
- `interval?: enum[5m,15m,1h,4h,1d]`, default `5m`;
- `limit?: integer`, range `1..500`, default `100`.

Response preserves:

- provider and canonical symbol;
- interval;
- `source_kind` (`provider`, `aggregate`, or `mixed`);
- candle count;
- candle OHLCV/provenance fields;
- `closed` flag for every candle.

The integration must not synthesize unsupported intervals or silently include an open candle where the caller requests confirmed/closed-bar analysis.

Failure mapping:

- `401` -> authentication failure;
- `404` -> symbol/history unavailable;
- `409` -> provider ambiguity;
- invalid interval/limit -> validation failure, not fallback trade advice.

## Tool 6 — `ktrader_analysis`

Backend mapping: `GET /v1/analysis/{symbol}` (`getAnalysis`)

Parameters:

- `symbol: string`;
- `provider_id?: string`.

Canonical response is the backend `TradingDecision` and must be preserved without adapter-side reinterpretation of core decision fields:

- `side` = `LONG | SHORT | NO_TRADE`;
- `grade`;
- `setup_score` and `raw_score`;
- setup/regime/trend context;
- canonical Entry/SL/TP/RR fields when present;
- reason codes;
- data/provider identity;
- `data_time`, `last_closed_bar`, `data_age_seconds`, `freshness_status`;
- `generated_at`, `engine_version`;
- `estimated_probability` only when supplied by backend.

`setup_score` must not be represented as a calibrated probability.

Failure mapping:

- `401` -> authentication failure;
- `404` -> canonical analysis unavailable;
- `409` -> provider ambiguity.

When this tool returns `NO_TRADE`, the Plugin must preserve `NO_TRADE` as a valid canonical result.

## Tool 7 — `ktrader_list_candidates`

Backend mapping: `GET /v1/candidates` (`listCandidates`)

Parameters:

- `provider_id?: string`;
- `grade?: enum[A+,A,B,C]`;
- `limit?: integer`, range `1..200`, default `50`.

Response: `DecisionList` including candidate decisions, including `NO_TRADE` results where returned by the backend.

Candidate membership must not be promoted locally to a tradable signal.

Failure mapping:

- `401` -> authentication failure;
- unsupported grade/limit -> validation failure.

## Tool 8 — `ktrader_list_signals`

Backend mapping: `GET /v1/signals` (`listSignals`)

Parameters:

- `provider_id?: string`;
- `limit?: integer`, range `1..200`, default `50`.

Response: `DecisionList` containing only backend-authorized current signal records according to canonical server semantics.

An empty successful list is a valid canonical **NO TRADE / no active signals** state, not an integration failure.

Failure mapping:

- `401` -> authentication failure.

## Common structured failure contract

The adapter should surface failures as typed failures, preserving at least:

- operation/tool name;
- backend HTTP/error class;
- provider/symbol/interval parameters relevant to the request;
- human-readable backend message when safe;
- whether retry with `provider_id` is required;
- whether the failure is authentication, not-found/history, ambiguity, validation, readiness/freshness, or transport-related.

The Skill may switch to `WATCHLIST ONLY` fallback only when canonical data are insufficient and the fallback policy explicitly allows it. It must not reconstruct canonical LONG/SHORT/Entry/SL/TP/RR from partial failures.

## Authentication boundary

Current legacy path:

`Custom GPT Action -> Bearer KTRADER_ACTION_API_KEY -> backend`

Target integration:

`K-Trader Skill -> Plugin/App authorization -> read-only adapter -> backend`

The final auth mechanism remains intentionally unspecified until the actual account/workspace Plugin/App/MCP creation surface exposes its supported contract.

If an adapter-level service credential is required, it remains server-side, rotatable, and outside the Skill and conversation.

## Permission declaration

Required effective permission set:

- network access only to the accepted K-Trader backend origin or equivalent internal service binding;
- invoke the eight read-only capabilities above;
- no trading/exchange-account writes;
- no unrelated user data;
- no filesystem/shell/generic network proxy.

## Acceptance tests tied to this surface

The replacement integration is not accepted until all are demonstrated:

1. all eight tools are discoverable and callable;
2. no ninth write/order/account/generic-proxy tool is exposed;
3. `health` and scanner status remain distinguishable;
4. empty signals list is handled as valid no-signal state;
5. `NO_TRADE` is preserved;
6. provider ambiguity returns a structured fail-closed result and succeeds only after explicit provider disambiguation;
7. unsupported interval/grade/limit validation fails safely;
8. invalid auth fails;
9. freshness/readiness fields are preserved;
10. adapter output retains backend provider/symbol/time provenance;
11. canonical analysis is not locally overwritten by the Skill/adapter;
12. integration outage cannot generate a canonical trade recommendation.

## Non-goals

This specification does not:

- authorize Plugin cutover;
- activate execution/trading;
- change frozen strategy v2.2;
- alter Phase 11G evidence/governance;
- open holdout;
- define a final MCP manifest format before the product surface is observable.
