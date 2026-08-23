# ATR Specification v1.2

## ATR14

ATR14 uses standard True Range over confirmed closed contiguous candles.

`TR_t = max(high_t-low_t, abs(high_t-close_(t-1)), abs(low_t-close_(t-1)))`

For the first available candle without previous close, `TR = high-low`.

Canonical smoothing is Wilder:

1. seed ATR = arithmetic mean of first 14 True Range values;
2. next ATR = `((previous_ATR * 13) + current_TR) / 14`.

## ATR5D

1. Use confirmed closed contiguous canonical `1d` bars.
2. Calculate Wilder ATR14 series on D1.
3. Walk backward from latest closed D1 bar.
4. Candidate range = `high-low`.
5. Compare with ATR14 ending on that same historical bar.
6. Reject range `>= 2.0 * ATR14_at_bar`.
7. Reject range `<= 1/3 * ATR14_at_bar`.
8. Never replace, duplicate or interpolate rejected bars.
9. Continue until five valid D1 ranges are collected.
10. `ATR5D = mean(five valid ranges)`.

Same-bar ATR14 reference avoids look-ahead during replay/backtest.

If five valid ranges cannot be confirmed, ATR5D is unavailable and setup fails closed.

## ATR used - canonical Phase 7 origin

Phase 7 now defines the previously deferred `move_distance` origin.

Daily range context is reconstructed from confirmed closed 5m candles from exactly `00:00 UTC` through the last closed 5m bar of the current UTC day.

LONG proposed Entry:

`move_distance = Entry - observed_UTC_day_low`

SHORT proposed Entry:

`move_distance = observed_UTC_day_high - Entry`

Then:

`ATR_used_pct = abs(move_distance) / ATR5D * 100`

Classification:

- `<40%` -> `STRONG`
- `40% <= value <= 80%` -> `ACCEPTABLE`
- `>80%` -> `LATE_REJECT`

The metric is calculated against the proposed Entry trigger, not the latest close, so luft is included in the exhaustion test.

A partial UTC-day range that does not begin at 00:00 UTC cannot be used for this metric.

GPT-side recalculation must not override the Trading Engine value.
