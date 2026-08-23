# Storage Specification v1.0

## Backend

K-Trader v1 uses SQLite with WAL mode.

Operational baseline:

- persistent file path, default `data/ktrader.db` before VPS remapping;
- `PRAGMA journal_mode=WAL`;
- `PRAGMA synchronous=NORMAL`;
- `PRAGMA busy_timeout=5000`;
- `PRAGMA foreign_keys=ON`.

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

### bootstrap_runs

Stores SUCCESS/FAILED bootstrap audit records, interval counts and error text.

## Write model

A validated MTF bootstrap is flattened and written in one SQLite transaction.

If any timeframe fails validation before persistence, no candle from that bootstrap is written.

Upsert is allowed for the same candle identity so REST reconciliation and later live updates can replace a previously stored version deterministically.
