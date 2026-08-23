# Storage Specification v1.1

## Backend

K-Trader v1 uses SQLite with WAL mode.

Operational baseline:

- persistent file path, default `data/ktrader.db` before VPS remapping;
- `PRAGMA journal_mode=WAL`;
- `PRAGMA synchronous=NORMAL`;
- `PRAGMA busy_timeout=5000`;
- `PRAGMA foreign_keys=ON`.

## Schema version

Phase 3 uses SQLite schema version 2.

Existing Phase 2 databases are migrated in place by adding candle provenance columns when absent. Migration does not delete historical candle or bootstrap data.

## Candle identity

Primary key:

`provider_id + symbol + interval + open_time_ms`

This guarantees provider separation and idempotent updates of the same bar.

## Precision

- UTC timestamps are stored as integer epoch milliseconds.
- Decimal market values are stored as TEXT and restored as `Decimal`.
- No conversion through binary float is allowed in persistence.

## Tables

### candles

Stores normalized OHLCV, optional quote volume, trade count, taker-buy fields, closed status and ingestion time.

Phase 3 provenance fields:

- `source_kind`: `provider` or `aggregate`;
- `derived_from_interval`: source child interval for local aggregate, otherwise NULL.

A provider-native REST/WS bar is stored as `provider`. A locally built parent candle is stored as `aggregate`, currently derived from closed `5m` children.

### bootstrap_runs

Stores SUCCESS/FAILED bootstrap audit records, interval counts and error text.

## Write model

A validated MTF bootstrap is flattened and written in one SQLite transaction.

If any timeframe fails validation before persistence, no candle from that bootstrap is written.

Live open candles are not persisted as canonical history. Provider-confirmed closed 5m bars are upserted idempotently.

Locally aggregated parent bars are written only after complete contiguous child coverage. REST reconciliation may subsequently replace a local aggregate with provider-native data and changes provenance to `provider`.

Upsert is allowed for the same candle identity so REST reconciliation and live updates can replace a previously stored version deterministically.
