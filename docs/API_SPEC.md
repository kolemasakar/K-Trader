# API Specification v1.1

## Role

Expose scanner state to K_Trader Custom GPT through a read-only HTTPS API.

The API is an integration/read-model layer. It does not recalculate Trading Engine rules and the scanner must remain able to function without OpenAI.

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

## Read model

`ApiReadModel` is populated internally by the scanner/runtime coordinator.

It stores current read-only snapshots of:

- scanner runtime status;
- universe candidates;
- candle series and source provenance;
- per-symbol best TradingDecision;
- ranked setup candidates/signals.

The API never obtains exchange account credentials and never performs exchange writes.

## Symbol/provider resolution

Canonical symbol alone is accepted only when it resolves unambiguously.

If the same canonical symbol is present on multiple providers and `provider_id` is omitted:

- HTTP `409` is returned;
- the caller must retry with explicit `provider_id`.

The API must never silently choose or substitute a provider.

## Candle contract

Supported canonical intervals:

- `5m`
- `15m`
- `1h`
- `4h`
- `1d`

The response carries:

- provider_id;
- canonical symbol;
- interval;
- `source_kind = provider | aggregate`;
- requested tail of confirmed normalized candles.

Default limit: 100. Maximum: 500.

## Decimal and time serialization

Exchange Decimal values are serialized as JSON strings rather than binary floating-point numbers.

This preserves exact values such as price ticks, prices, volume, ATR and RR.

Timestamps are UTC ISO-8601 strings ending in `Z`.

## TradingDecision contract

`GET /v1/analysis/{symbol}`, `/v1/candidates` and `/v1/signals` expose the canonical Phase 7 TradingDecision.

The API does not independently modify:

- side;
- Grade;
- Setup Score;
- Entry/Luft/SL/TP;
- RR;
- ATR-used;
- reason codes.

`/v1/signals` includes only A/A+ LONG/SHORT decisions.

`/v1/candidates` may include NO_TRADE/B/C outcomes for audit/explanation.

## Freshness

Responses preserve provider/source and data freshness metadata.

Invalid/stale data is not silently substituted. A stale engine result remains stale/NO_TRADE according to engine rules.

## Health/status

`/health` reports API availability plus scanner data readiness.

The endpoint may return HTTP 200 with `status=degraded` while the process is alive but scanner data is not ready. This distinguishes process health from market-data readiness.

## Rate limiting

Phase 8 provides a single-process fixed-window application limiter.

Canonical baseline:

- 120 requests;
- per 60 seconds;
- per direct client address.

HTTP 429 includes `Retry-After`.

The middleware intentionally does not trust `X-Forwarded-For` by itself. Phase 9 deployment may add trusted reverse-proxy enforcement/hardening.

## Custom GPT Action

`custom_gpt/openapi.yaml` is the Action schema.

It contains stable operation IDs:

- `getHealth`
- `getScannerStatus`
- `listUniverse`
- `getMarketSnapshot`
- `getCandles`
- `getAnalysis`
- `listCandidates`
- `listSignals`

The Phase 8 schema intentionally uses the non-routable placeholder server:

`https://api.k-trader.invalid`

Phase 10 replaces this with the deployed HTTPS API host.

Initial Action authentication may be `None` because the API exposes only public-market-derived read-only analysis. HTTPS remains mandatory.

If the GPT is distributed publicly, deployment documentation must include the OpenAI publication/privacy requirements applicable at that time.

## Security boundary

Forbidden v1 API capabilities:

- order placement/modification/cancellation;
- exchange account endpoints;
- exchange API credentials;
- arbitrary SQL/storage access;
- arbitrary URL proxying;
- cross-provider series fusion.
