# Data Contract v1.0

## Normalized instrument

Required fields:
- provider_id
- exchange
- provider_symbol
- canonical_symbol
- market_type
- base_asset
- quote_asset
- status
- contract_type
- tick_size
- qty_step
- min_qty
- max_qty where known
- price_precision / qty_precision where known
- source_timestamp

## Normalized candle

Required:
- provider_id
- canonical_symbol
- interval
- open_time_utc
- close_time_utc
- open
- high
- low
- close
- base_volume
- is_closed
- received_at_utc

Optional, preserved when provider supports them:
- quote_volume
- trade_count
- taker_buy_base_volume
- taker_buy_quote_volume

Derived fields SHALL NOT overwrite raw provider fields.

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
- Aggregated bars must contain `derived_from_interval` and complete child-bar coverage.
- Provider bars and locally aggregated bars are distinguishable.
- Cross-provider bar concatenation is forbidden.
- UTC is canonical time.

## Freshness

Every snapshot returned to K_Trader includes:
- data_time
- last_closed_bar
- data_age_seconds
- provider_id
- freshness_status: FRESH | STALE | UNKNOWN
