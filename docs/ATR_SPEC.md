# ATR Specification v1.1

## ATR14

ATR14 uses standard True Range over confirmed closed contiguous candles.

True Range for candle `t`:

`TR_t = max(high_t - low_t, abs(high_t - close_(t-1)), abs(low_t - close_(t-1)))`

For the first available candle without a previous close, `TR = high - low`.

Smoothing is canonical Wilder smoothing:

1. seed ATR = arithmetic mean of the first 14 True Range values;
2. each next ATR = `((previous_ATR * 13) + current_TR) / 14`.

No provider-specific ATR formula is allowed.

## ATR5D

Purpose: estimate recent normal daily movement while excluding abnormal D1 ranges.

Algorithm:

1. Use confirmed closed contiguous canonical `1d` bars only.
2. Calculate the Wilder ATR14 series on D1.
3. Walk backward through D1 bars from the latest closed bar.
4. For each candidate bar calculate `range = high - low`.
5. Use the ATR14 value ending at that same bar as the abnormal-range reference.
6. Reject if `range >= 2.0 * ATR14_at_bar`.
7. Reject if `range <= (1/3) * ATR14_at_bar`.
8. Do not replace, duplicate or interpolate rejected bars.
9. Continue backward until 5 valid observations are collected.
10. `ATR5D = arithmetic mean(valid 5 high-low ranges)`.

Using the ATR14 value from the same historical bar avoids look-ahead when ATR5D is replayed/backtested.

If 5 valid bars cannot be confirmed after ATR14 becomes available, ATR5D is unavailable and the setup cannot pass ATR validation.

The implementation exposes the selected valid ranges/timestamps and rejection counts for deterministic testing/audit.

## ATR used

Phase 4 defines only the mathematical metric:

`ATR_used_pct = abs(move_distance) / ATR5D * 100`

Classification:

- `< 40%` -> `STRONG`
- `40% <= value <= 80%` -> `ACCEPTABLE`
- `> 80%` -> `LATE_REJECT`

The canonical `move_distance` origin is deliberately not chosen in the indicator module.

It SHALL be defined by the Phase 7 Trading Engine setup rule and must be identical in engine output, API output, tests and Custom GPT interpretation.

No GPT-side recalculation may override the engine value.
