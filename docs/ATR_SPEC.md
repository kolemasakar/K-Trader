# ATR Specification v1.0

## ATR14

ATR14 uses standard True Range over confirmed closed bars. Exact smoothing method SHALL be fixed in implementation tests and configuration/version metadata.

## ATR5D

Purpose: estimate recent normal daily movement while excluding abnormal D1 ranges.

Algorithm:
1. Use confirmed closed D1 bars only.
2. Calculate/reference ATR14 on D1.
3. Walk backward through D1 bars.
4. For each bar calculate range = high - low.
5. Reject abnormal range >= 2.0 * ATR14.
6. Reject abnormal range <= (1/3) * ATR14.
7. Do not replace or duplicate rejected bars.
8. Continue backward until 5 valid observations are collected.
9. ATR5D = arithmetic mean of those 5 valid high-low ranges.

If 5 valid bars cannot be confirmed, ATR5D is unavailable and the setup cannot pass ATR validation.

## ATR used

`ATR_used_pct` SHALL be defined against a canonical move origin in Trading Engine implementation before use in production. The origin and formula must be identical in API output, tests and Custom GPT interpretation.

Classification:
- < 40%: STRONG
- 40% to 80%: ACCEPTABLE
- > 80%: LATE / REJECT

No GPT-side recalculation may override the engine value.
