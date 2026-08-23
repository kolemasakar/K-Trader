# Candle Validation Specification v1.0

## Canonical intervals

Internal interval keys:

- `1d`
- `4h`
- `1h`
- `15m`
- `5m`

User-facing labels may be D1/4H/1H/15m/5m, but storage and provider-independent code use the canonical keys above.

## UTC boundary rules

- all normalized timestamps are timezone-aware UTC;
- `open_time` must align exactly to the interval boundary;
- normalized `close_time = interval_end - 1 ms`;
- sequence ordering is strictly chronological.

## OHLCV integrity

Required checks:

- OHLC finite and positive;
- `low <= open/close <= high`;
- volume fields finite and nonnegative;
- trade count, when present, nonnegative;
- provider, symbol and interval match the requested snapshot.

## Missing bars

Historical bootstrap requires contiguous closed bars.

A missing bar causes fail-closed rejection. K-Trader v1 does not interpolate or synthesize missing provider candles for Trading Engine decisions.

## Freshness

Freshness is evaluated from the latest closed candle.

Operational policy:

`max_age_seconds = interval_seconds × max_age_intervals`

Initial configurable baseline:

`max_age_intervals = 2.0`

This is a data-readiness threshold, not a trading-strategy probability or setup rule.

Stale history is rejected before persistence.
