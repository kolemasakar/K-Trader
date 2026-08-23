# Architecture v1.2

## Context

K-Trader consists of two independently evolvable parts:

1. Market-data/scanner backend running continuously on a VPS.
2. Custom GPT acting as the user-facing analysis interface.

The GPT is not the market-data collector and does not connect directly to exchange WebSockets.

## Logical architecture

Public Exchange APIs
  -> Provider Adapters
  -> Normalized Market Data
  -> Universe + Liquidity
  -> Candle Store / MTF State
  -> Indicators
  -> Regime / Levels / Trap / VSA
  -> Setup Scoring / Rating
  -> Runtime Scanner Coordinator
  -> ApiReadModel
  -> Read-only FastAPI HTTPS API
  -> Custom GPT Action
  -> K_Trader

## Provider abstraction

Core provider responsibilities:

- discover instruments;
- fetch tickers/liquidity inputs;
- fetch historical candles;
- subscribe to live public market data;
- normalize instrument/candle/ticker metadata;
- expose provider capabilities.

Initial implemented adapters are Binance USD-M and Bybit Linear. OKX SWAP, KuCoin Futures and others are future adapters through the same provider contract.

No engine/runtime/API module depends on provider-native payload formats.

## Market-series integrity

A single analysis has exactly one primary `provider_id` and one canonical instrument mapping.

Fallback behavior:

- select next eligible provider;
- bootstrap/read a new coherent series;
- atomically replace the old provider API snapshot;
- never splice bars from two providers into one OHLCV sequence.

Cross-provider comparison may be a separate confirmation feature, never data fusion.

## Timeframe model

Canonical analysis timeframes: `1d`, `4h`, `1h`, `15m`, `5m`.

Live design:

- REST bootstrap for all required timeframes;
- public provider WebSocket for 5m;
- local UTC aggregation upward;
- periodic REST reconciliation against provider-native candles.

## Persistence

v1 uses SQLite WAL for canonical market/history state. Persistent deployment data lives outside the GitHub runner workspace.

Current API-facing universe/candidate/signal state is an in-process read projection, not a second source of truth.

## Engine boundaries

Exchange-specific code lives only under providers.

Provider-independent modules include universe/liquidity, candle validation/aggregation, indicators, regime/strength, levels, Trap/VSA, setup geometry, scoring/rating, TradingDecision, runtime coordination and API serialization.

## Runtime Scanner Coordinator

Phase 8.5 implements the application orchestration layer.

Responsibilities:

- select/fail over provider without cross-provider fusion;
- refresh ranked universe/liquidity data each scan cycle;
- analyze a configurable top-N shortlist;
- enforce historical/live readiness;
- invoke atomic MTF bootstrap when required;
- retain/restart the Phase 3 live subscription according to provider/shortlist identity;
- run indicators -> market structure/levels/session -> Trap/VSA -> Phase 7 Trading Engine;
- isolate failures per symbol;
- publish current universe/candles/decisions/status atomically to `ApiReadModel`;
- fail closed on stale, gapped or incomplete data;
- provide explicit `NO_SETUP`/`NO_TRADE` only when data is valid/fresh but no confirmed setup exists.

The coordinator does not duplicate Trading Engine rules.

## API read-model boundary

`ApiReadModel` is thread-safe and receives an atomic scanner-cycle projection.

It exposes current:

- scanner runtime status;
- universe;
- candle series/provenance;
- per-symbol best TradingDecision;
- ranked candidates;
- A/A+ LONG/SHORT signals.

Candle-series provenance supports `provider`, `aggregate` and `mixed`; `mixed` refers only to provider-native history plus local aggregation from the same provider.

On total provider/runtime failure the publishable runtime state is cleared and `data_ready=false`.

The API never recalculates Entry/SL/TP/RR/ATR-used/Grade/Score.

## API boundary

The Custom GPT calls a public HTTPS read-only API. v1 application endpoints are GET-only; no account/order/mutation endpoints exist.

Decimal market values are serialized as strings and timestamps as UTC ISO-8601.

A fixed-window application rate limiter exists; reverse-proxy hardening belongs to deployment.

## Runtime process

Production process entrypoint:

`uvicorn ktrader.runtime.app:app`

It creates the SQLite repository, provider instances, `ApiReadModel`, scanner coordinator and FastAPI app, and owns clean shutdown of live/provider/repository resources.

## Custom GPT Action

`custom_gpt/openapi.yaml` defines stable read-only operation IDs. Before deployment it intentionally points to `https://api.k-trader.invalid`; Phase 10 replaces this with the real HTTPS API host.

## Deployment

GitHub private repository
  -> push to main
  -> self-hosted GitHub Runner on Ubuntu VPS
  -> repository-wide tests
  -> Docker Compose build
  -> runtime scanner + API process
  -> health/readiness/live-provider checks

Persistent runtime data/config/logs live under `/opt/k-trader`.

## Security boundary

No exchange credentials are required in v1.
No execution endpoints exist.
The public API returns only market/scanner outputs and is rate-limited.
The API does not trust forwarded client-IP headers without trusted-proxy configuration.
