# Data Contract v1.2

## Normalized instrument

Required fields:
- provider_id
- provider_symbol
- canonical symbol (`symbol` in code)
- market_type
- base_asset
- quote_asset
- status
- contract_type
- price/quantity increments where known

## Normalized candle

Required:
- provider_id
- canonical symbol
- interval
- open_time UTC
- close_time UTC
- open
- high
- low
- close
- base volume
- closed flag

Optional, preserved when provider supports them:
- quote_volume
- trade_count
- taker_buy_volume
- taker_buy_quote_volume

Derived fields SHALL NOT overwrite normalized provider fields.

## Live candle event

Phase 3 wraps a normalized candle in a provider-independent live event containing:

- event_time;
- received_at;
- connection_id where available;
- raw topic metadata where useful.

The current open candle is provisional. It may be held in memory for observation but is not persisted as canonical closed history and must not be treated as a closed VSA confirmation.

## Canonical timeframe keys

Provider-independent code uses:

- `1d`
- `4h`
- `1h`
- `15m`
- `5m`

User-facing labels may use D1/4H/1H/15m/5m.

## Time normalization

- UTC is canonical.
- `open_time` aligns exactly to the interval boundary.
- normalized `close_time = interval_end - 1 ms`.
- historical sequences are strictly chronological.

## Derived volume-bar features

Examples:
- spread = high - low
- body = abs(close - open)
- close_location
- relative_volume
- relative_spread
- trade_count_ratio
- taker_buy_ratio
- volume_delta_proxy

Each derived field SHALL declare its formula/version in code/tests.

## Integrity rules

- No synthetic OHLCV values unless explicitly tagged as derived aggregation.
- No interpolation of missing exchange candles for Trading Engine decisions.
- Historical bootstrap requires contiguous closed bars.
- Live parent aggregation requires complete contiguous child-bar coverage.
- Provider bars and locally aggregated bars are distinguishable.
- Cross-provider bar concatenation is forbidden.
- Stale historical/live state fails closed before engine use.

## Persistence precision and provenance

- timestamps: integer epoch milliseconds;
- Decimal market values: textual decimal representation;
- no persistence conversion through binary float;
- provider-native closed bars: `source_kind=provider`;
- local aggregates: `source_kind=aggregate`, with `derived_from_interval` populated.

REST reconciliation may replace a local aggregate or earlier live value with provider-native closed data through the same candle identity.

## Freshness

Every future API snapshot returned to K_Trader includes:
- data_time
- last_closed_bar
- data_age_seconds
- provider_id
- freshness_status: FRESH | STALE | UNKNOWN

Historical freshness is interval-relative. Live WebSocket freshness uses a configurable receive-time timeout. Freshness is a data-readiness gate, not a Setup Score contribution.
