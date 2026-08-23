# Architecture v1.0

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
  -> Candidate + Signal Store
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

Initial adapters may target Binance USD-M, Bybit Linear, OKX SWAP and KuCoin Futures, but no engine module may depend on those names.

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

A single analysis has exactly one primary `provider_id` and one `instrument_id` mapping.

Fallback behavior:

- mark primary source unavailable/stale;
- select next eligible provider;
- bootstrap a new coherent series;
- never splice bars from two providers into one sequence.

Cross-provider comparison may be implemented as a separate confirmation feature, not data fusion.

## Timeframe model

Canonical analysis timeframes:

- D1
- 4H
- 1H
- 15m
- 5m

Preferred live design:

- REST bootstrap for all required timeframes;
- live provider WebSocket for the smallest canonical interval where reliable;
- local aggregation upward using UTC boundaries;
- periodic REST reconciliation against provider-native candles.

Provider-specific behavior may require direct subscriptions to additional intervals; this is declared by capability/config rather than assumed globally.

## Persistence

v1 uses SQLite WAL in a persistent Docker volume.

Primary logical tables:

- providers
- instruments
- candles
- levels
- vsa_events
- trap_events
- candidates
- signals
- scanner_runs
- provider_health

## Engine boundaries

Exchange-specific code lives only under adapters/providers.

Provider-independent modules:

- universe/liquidity normalization;
- candle validation/resampling;
- ATR/MA;
- regime/strength;
- levels;
- trap;
- VSA;
- scoring/rating;
- API serialization.

## API boundary

The Custom GPT calls a public HTTPS read-only API.

v1 API exposes only GET/health-style operations. No account, order or mutation endpoints exist.

Custom GPT Actions are an integration layer only; the scanner remains functional without OpenAI.

## Deployment

GitHub private repository
  -> push to main
  -> self-hosted GitHub Runner on Ubuntu VPS
  -> tests
  -> Docker Compose build
  -> Docker Compose up -d
  -> health check

Persistent runtime data/config/logs live under `/opt/k-trader`, outside ephemeral GitHub runner workspaces.

## Security boundary

No exchange credentials are required in v1.
No execution endpoints exist.
The public API is rate-limited and returns only market/scanner outputs.
