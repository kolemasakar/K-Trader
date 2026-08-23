# Indicators Specification v1.0

## Scope

Phase 4 indicators are provider-independent calculations over validated, confirmed, closed, contiguous normalized candles.

Indicators never repair missing bars, interpolate OHLCV or use provisional/open candles as confirmed history.

## ATR

Canonical ATR behavior is defined in `ATR_SPEC.md`.

- True Range includes inter-bar gaps.
- ATR14 uses Wilder smoothing.
- ATR5D uses canonical `1d` data and the same-bar ATR14 reference for abnormal-range filtering.

## Moving averages

MA inputs are candle close prices.

Supported methods:

- `sma`
- `ema`

Canonical v1 baseline:

`method = sma`

Periods:

- fast MA = 50
- slow MA = 200

SMA:

`mean(last N closes)`

EMA:

- seed = SMA of the first N closes;
- alpha = `2 / (N + 1)`;
- iterative update over subsequent closes.

The selected `ma_method` must travel with future engine/API outputs. Phase 5/7 may use MA50/200 for regime/trend rules but may not silently change the configured method.

## Volume statistics

Canonical baseline window:

`20` previous closed bars.

The current bar is excluded from its own baseline.

Base-volume metrics:

- `average_volume = mean(previous 20 base volumes)`
- `relative_volume = current base volume / average_volume`

Quote-volume metrics are calculated only if current and all baseline quote-volume values are confirmed:

- `average_quote_volume`
- `relative_quote_volume = current quote volume / average_quote_volume`

If quote volume is incomplete, quote-volume relative metrics are `N/A`; they are never inferred from price.

## VSA candle spread

In Phase 4 `spread` means candle spread/range for VSA:

`spread = high - low`

It is not bid/ask spread.

Baseline:

- `average_spread = mean(previous 20 candle spreads)`
- `relative_spread = current spread / average_spread`

The current candle is excluded from the spread baseline.

## Indicator snapshot

A normalized indicator snapshot contains:

- provider_id
- symbol
- interval
- data_time
- close
- ATR14
- MA method
- MA50
- MA200
- volume statistics
- relative volume
- relative candle spread
- optional relative quote volume

ATR5D is calculated separately from canonical D1 history and is attached by later engine orchestration.

## Fail-closed rules

Indicator calculation fails rather than guessing when:

- candle sequence is empty;
- sequence is open, gapped, non-contiguous or provider/symbol/interval inconsistent;
- insufficient bars exist for a requested period;
- average volume/spread baseline is non-positive;
- ATR5D cannot collect five valid D1 observations.

## ATR-used boundary

The generic Phase 4 helper accepts an explicit `move_distance` and ATR5D.

The semantic origin for `move_distance` is not an indicator concern and remains reserved for Phase 7.
