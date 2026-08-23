# Architecture v1.1

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

Core interface responsibilities:

- discover instruments;
- fetch tickers/liquidity inputs;
- fetch historical candles;
- subscribe to live public market data;
- normalize instrument/candle/ticker metadata;
- expose provider capabilities.

Initial implemented adapters are Binance USD-M and Bybit Linear. OKX SWAP, KuCoin Futures and others are future adapters through the same provider contract.

No engine/runtime/API module may depend on provider-native payload formats.

## Provider capability model

Each adapter declares support for items such as:

- perpetual derivatives;
- intervals;
- quote volume;
- trade count;
- taker-buy base/quote volume;
- book ticker;
- open interest;
- WebSocket candles;
- max REST page size and rate-limit metadata.

Missing optional fields remain null/unsupported; they are never fabricated.

## Market-series integrity

A single analysis has exactly one primary `provider_id` and one canonical instrument mapping.

Fallback behavior:

- mark primary source unavailable/stale;
- select next eligible provider;
- bootstrap a new coherent series;
- never splice bars from two providers into one sequence.

Cross-provider comparison may be implemented as a separate confirmation feature, not data fusion.

## Timeframe model

Canonical analysis timeframes:

- 1d
- 4h
- 1h
- 15m
- 5m

Preferred live design:

- REST bootstrap for all required timeframes;
- live provider WebSocket for 5m;
- local UTC aggregation upward;
- periodic REST reconciliation against provider-native candles.

Provider-specific behavior may require direct subscriptions to additional intervals; this is declared by capability/config rather than assumed globally.

## Persistence

v1 uses SQLite WAL in a persistent Docker volume for canonical market/history state.

Primary logical persistent data includes:

- instruments;
- candles;
- bootstrap/scanner audit state;
- future level/VSA/trap/signal history where persistence is required.

Current API-facing universe/candidate/signal state is a process read model, not an independent source of truth.

## Engine boundaries

Exchange-specific code lives only under providers.

Provider-independent modules:

- universe/liquidity normalization;
- candle validation/resampling;
- ATR/MA;
- regime/strength;
- levels;
- trap;
- VSA;
- setup geometry;
- scoring/rating;
- TradingDecision;
- API serialization.

## Runtime Scanner Coordinator

The coordinator is the missing application orchestration layer inserted as Phase 8.5 before deployment.

Responsibilities:

- select/fail over provider without cross-provider fusion;
- refresh universe/liquidity shortlist;
- enforce historical/live readiness;
- obtain coherent MTF candle state;
- run indicators;
- run market structure/levels/session context;
- run Trap/VSA evidence;
- run the Phase 7 Trading Engine;
- isolate failures per symbol;
- rank decisions/signals;
- publish immutable current snapshots into `ApiReadModel`;
- expose scanner status/error state;
- fail closed when mandatory data is stale, gapped or incomplete.

The coordinator does not contain exchange-native parsing and does not duplicate Trading Engine rules.

## API read-model boundary

`ApiReadModel` is a thread-safe in-process projection updated by the runtime coordinator.

It exposes current snapshots of:

- scanner runtime status;
- universe;
- candle series/provenance;
- per-symbol best TradingDecision;
- ranked candidates;
- A/A+ LONG/SHORT signals.

The API never recalculates Entry/SL/TP/RR/ATR-used/Grade/Score.

If a canonical symbol exists on multiple providers, provider omission is treated as ambiguous and returns HTTP 409 rather than silently selecting a source.

## API boundary

The Custom GPT calls a public HTTPS read-only API.

v1 application endpoints are GET-only. No account, order or mutation endpoints exist.

Decimal market values are serialized as strings to preserve exchange precision. Timestamps are UTC ISO-8601.

A fixed-window application rate limiter exists in Phase 8; reverse-proxy hardening is added during deployment.

Custom GPT Actions are an integration layer only; the scanner remains functional without OpenAI.

## Custom GPT Action

`custom_gpt/openapi.yaml` defines stable read-only operation IDs.

Before deployment it intentionally points to `https://api.k-trader.invalid`.

Phase 10 replaces that placeholder with the actual HTTPS API host and configures Action authentication/publication requirements.

## Deployment

GitHub private repository
  -> push to main
  -> self-hosted GitHub Runner on Ubuntu VPS
  -> repository-wide tests
  -> Docker Compose build
  -> scanner coordinator + API services
  -> health/readiness checks

Persistent runtime data/config/logs live under `/opt/k-trader`, outside ephemeral GitHub runner workspaces.

## Security boundary

No exchange credentials are required in v1.
No execution endpoints exist.
The public API is rate-limited and returns only market/scanner outputs.
The API does not trust forwarded client-IP headers without a trusted proxy configuration.
