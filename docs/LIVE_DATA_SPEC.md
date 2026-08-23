# Live Market Data Specification v1.0

## Purpose

Phase 3 maintains a continuous read-only market-data state from public exchange WebSockets while preserving the Phase 2 historical integrity rules.

## Base live interval

The canonical live input interval is `5m`.

Provider adapters normalize public WebSocket kline/candle events into `LiveCandleEvent` containing a `NormalizedCandle`, provider identity, event time and receive time.

Initial live providers:

- `binance_usdm`;
- `bybit_linear`.

## Open vs closed candle

The current open 5m candle may be kept in memory for observation but is not persisted into the canonical closed-history store.

Only a provider-confirmed closed 5m candle may enter persistent history.

An open candle must never be treated as a closed VSA/trading confirmation.

## UTC aggregation

Closed 5m candles are locally aggregated to:

- `15m`;
- `1h`;
- `4h`;
- `1d`.

Aggregation requires complete contiguous child coverage and canonical UTC boundaries. Missing child bars cause fail-closed rejection; no interpolation is allowed.

Provider-native and locally aggregated candles remain distinguishable:

- `source_kind=provider`;
- `source_kind=aggregate` with `derived_from_interval=5m`.

## Reconciliation

REST is authoritative for repair/reconciliation of closed history.

Baseline behavior:

- periodic base-5m reconciliation after a configurable number of closed bars;
- immediate REST recovery when a gap between persisted and incoming closed 5m bars is detected;
- dynamic lookback sufficient to cover the detected gap, capped by provider page limits;
- provider-native REST data may replace a locally aggregated/provider-stream value through idempotent upsert.

No cross-provider stitching is allowed during reconciliation.

## Staleness and reconnect

Initial configurable defaults:

- `stale_after_seconds=90`;
- reconnect backoff starts at 1 second;
- maximum reconnect backoff 30 seconds;
- successful event resets backoff.

A stream timeout or transport/provider error triggers reconnect. Per-symbol state tracks last received event and can be marked stale independently.

Stale live data is a data-readiness failure, not a scoring penalty.

## Provider transport notes

Binance USD-M uses its public futures market WebSocket and kline subscription streams.

Bybit Linear uses the public linear WebSocket, `kline.{interval}.{symbol}` topics, and application-level ping heartbeat approximately every 20 seconds in addition to transport keepalive.

Provider-specific transport details stay inside adapters; engine code consumes normalized events only.

## Volume-bar sequence

The future engine/API may expose the recent closed 5m sequence together with a separately labelled current open 5m candle.

The open candle remains provisional and is never merged into closed-history statistics as if final.

## Acceptance

Deterministic tests validate parsers, aggregation, provenance, reconciliation, gap recovery, staleness, migration and idempotency.

Real WebSocket reachability and continuous runtime behavior must still be validated on the target VPS. Offline tests are not proof of regional exchange reachability.
