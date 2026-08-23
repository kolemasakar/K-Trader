# API Specification v1.2

## Role

Expose scanner state to K_Trader Custom GPT through a read-only HTTPS API.

The API is an integration/read-model layer. It does not recalculate Trading Engine rules and the scanner remains independent of OpenAI.

## v1 endpoints

- `GET /health`
- `GET /v1/scanner/status`
- `GET /v1/universe`
- `GET /v1/market/{symbol}`
- `GET /v1/candles/{symbol}`
- `GET /v1/analysis/{symbol}`
- `GET /v1/candidates`
- `GET /v1/signals`

No POST/PUT/PATCH/DELETE application endpoints exist in v1.

## Atomic read model

Phase 8.5 runtime publishes complete scanner cycles through `ApiReadModel.publish_cycle()` under one lock.

A provider switch therefore replaces status, universe, candles and decisions atomically. Old-provider market state is not retained beside the new provider snapshot.

On total provider/runtime failure, current publishable market/decision state is cleared and `data_ready=false`.

## Symbol/provider resolution

Canonical symbol alone is accepted only when it resolves unambiguously.

If the same canonical symbol is present on multiple providers and `provider_id` is omitted:

- HTTP `409` is returned;
- the caller must retry with explicit `provider_id`.

The API never silently chooses or substitutes a provider.

## Candle contract

Supported canonical intervals: `5m`, `15m`, `1h`, `4h`, `1d`.

Series `source_kind` may be:

- `provider` - provider-native history/live bars;
- `aggregate` - locally aggregated bars;
- `mixed` - one retained series contains provider-native bootstrap history plus locally aggregated live parent bars.

`mixed` never means cross-provider OHLCV fusion.

Default candle limit: 100. Maximum: 500.

## Decimal and time serialization

Decimal values are serialized as JSON strings, preserving exact exchange/engine values. Timestamps are UTC ISO-8601 strings ending in `Z`.

## TradingDecision contract

`GET /v1/analysis/{symbol}`, `/v1/candidates` and `/v1/signals` expose canonical TradingDecision fields without API-side recalculation.

`/v1/signals` includes only A/A+ LONG/SHORT decisions.

`/v1/candidates` may include NO_TRADE/B/C outcomes.

Phase 8.5 adds the explicit runtime sentinel `setup_type=NO_SETUP` for a valid/fresh symbol with no confirmed setup:

- side `NO_TRADE`;
- Grade `C`;
- score 0;
- Entry/SL/TP/RR null;
- primary level null;
- reason `NO_CONFIRMED_SETUP`.

This sentinel is never a tradable setup and can never appear in `/v1/signals`.

If mandatory market data is stale/incomplete/invalid, the runtime does not fabricate `NO_SETUP`; that symbol is unavailable for analysis and is reflected in runtime failure status.

## Scanner status

`/v1/scanner/status` includes:

- status;
- provider_id;
- universe_size;
- data_ready;
- cycle_id;
- symbols_ready;
- symbols_failed;
- live_streaming;
- last_scan_at;
- last_cycle_duration_seconds;
- last_error;
- process started_at.

`/health` may return HTTP 200 with `status=degraded` while the process is alive but scanner data is not ready.

## Rate limiting

Canonical Phase 8 baseline:

- 120 requests per 60 seconds per direct client address;
- HTTP 429 with `Retry-After`.

The application does not trust `X-Forwarded-For` by itself. Phase 9 deployment handles trusted reverse-proxy policy.

## Custom GPT Action

`custom_gpt/openapi.yaml` remains the Action schema with stable operation IDs:

- `getHealth`
- `getScannerStatus`
- `listUniverse`
- `getMarketSnapshot`
- `getCandles`
- `getAnalysis`
- `listCandidates`
- `listSignals`

The schema intentionally uses `https://api.k-trader.invalid` until Phase 10 replaces it with the deployed HTTPS host.

Initial Action authentication may be `None` because the API exposes only public-market-derived read-only analysis. HTTPS remains mandatory.

## Security boundary

Forbidden v1 API capabilities:

- order placement/modification/cancellation;
- exchange account endpoints;
- exchange API credentials;
- arbitrary SQL/storage access;
- arbitrary URL proxying;
- cross-provider series fusion.
