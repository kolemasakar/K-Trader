# ADR-002: Exchange-agnostic provider interface

Status: ACCEPTED
Date: 2026-08-23

## Decision

All exchange connectivity is isolated behind a `MarketDataProvider` interface. The Trading Engine consumes normalized models and has no exchange-specific dependencies.

## Rationale

The project must support Binance, Bybit, OKX, KuCoin and future public sources without rewriting ATR/VSA/levels/scoring logic.

## Validation rule

Phase 1 requires at least two independent provider adapters to pass the same contract tests before provider abstraction is considered proven.

## Consequences

- Provider capability differences are explicit.
- Optional unavailable fields remain null/unsupported.
- One analysis uses one coherent provider series.
