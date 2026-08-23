# Market Structure Specification v1.0

## Scope

Phase 5 converts validated closed market data and Phase 4 indicators into deterministic structural context. It does not produce a trade signal or Setup Score.

## Swing structure

Canonical pivot baseline:

- `left = 2` closed bars;
- `right = 2` closed bars;
- swing high: candidate high is strictly greater than every high in both pivot windows;
- swing low: candidate low is strictly lower than every low in both pivot windows.

Strict comparison avoids ambiguous tied pivots. Pivot windows are configurable but must be versioned with results.

## Per-timeframe regime

Structural direction uses the latest two confirmed swing highs and latest two confirmed swing lows:

- higher high + higher low -> `BULLISH`;
- lower high + lower low -> `BEARISH`;
- otherwise -> `RANGE_OR_TRANSITION`.

MA context uses the configured Phase 4 MA method:

- `close > MA50 > MA200` -> `BULLISH`;
- `close < MA50 < MA200` -> `BEARISH`;
- otherwise -> `NEUTRAL`.

Final timeframe regime:

- structure and MA both `BULLISH` -> `BULLISH`;
- structure and MA both `BEARISH` -> `BEARISH`;
- structure = `RANGE_OR_TRANSITION` and MA = `NEUTRAL` -> `RANGE`;
- all other combinations -> `MIXED`.

MA50/200 therefore confirms structure; it does not create a directional regime by itself.

## MTF regime precedence

Canonical HTF order:

`1d -> 4h -> 1h`

Rules:

1. If `1d` is directional and `4h` agrees, use that direction.
2. If `1d` is not directional and `4h` + `1h` agree directionally, use that direction.
3. If all three are `RANGE`, combined regime = `RANGE`.
4. Otherwise combined regime = `MIXED`.

A conflicting D1/4H context cannot be converted into a directional regime by 1H alone.

## Strength

Strength is not Setup Score and is not probability.

For a directional timeframe, three binary evidence items are evaluated:

- structure direction agrees with regime;
- MA direction agrees with regime;
- relative volume >= configured participation threshold.

Canonical v1 participation threshold:

`relative_volume >= 1.0`

Classification:

- 3 evidence items -> `STRONG`;
- 2 -> `MODERATE`;
- 0-1 -> `WEAK`.

For `RANGE`, strength = `NEUTRAL`. For `MIXED`, strength = `WEAK`.

The strength label is descriptive context only; Phase 7 decides how it contributes to Setup Score.

## Session context

Crypto is 24/7. Session context never opens/closes the market and is not a standalone trade permission.

Canonical v1 conventional liquidity windows are stored in their local IANA timezones:

- TOKYO: `09:00-18:00 Asia/Tokyo`;
- LONDON: `08:00-17:00 Europe/London`;
- NEW_YORK: `08:00-17:00 America/New_York`.

DST is therefore handled by timezone data rather than hardcoded seasonal UTC offsets.

The engine outputs all active session labels and an `overlap` flag. Presentation time defaults to `Europe/Kyiv`.

Session windows are configuration, not immutable strategy constants.

## MTF levels

Canonical automatic Phase 5 evidence:

- historical swing levels;
- consolidation zones;
- trend-break lifecycle events;
- mirror lifecycle events.

`LIMIT` and `PARANORMAL_BAR` types are supported as explicit evidence inputs, but Phase 5 does not invent their geometry because no canonical automatic geometry rule has yet been approved.

Historical swing levels of the same side are clustered using an ATR-scaled radius:

`cluster_radius = ATR14 * zone_atr_fraction`

Canonical baseline:

`zone_atr_fraction = 0.15`

Level confirmation/strength:

- 1 independent swing touch -> `FLOATING`, `WEAK`;
- 2 touches -> `CONFIRMED`, `MODERATE`;
- 3+ touches -> `CONFIRMED`, `STRONG`.

A FLOATING level cannot validate a trade.

## MTF level priority

Canonical ordering:

`1d > 4h > 1h > 15m > 5m`

Priority is used for ordering/context. It does not silently merge or delete lower-timeframe evidence.

## Level lifecycle

Statuses:

`FLOATING -> CONFIRMED -> BROKEN -> MIRROR -> INVALIDATED`

Rules:

- confirmed support breaks when a closed candle closes below the zone lower bound minus configured break buffer;
- confirmed resistance breaks when a closed candle closes above the zone upper bound plus configured break buffer;
- `BROKEN` is not an active validating support/resistance level;
- a broken support becomes mirror resistance only after a retest from below and close back below the old zone;
- a broken resistance becomes mirror support only after a retest from above and close back above the old zone;
- a confirmed mirror that closes through its opposite invalidation boundary becomes `INVALIDATED`.

Canonical Phase 5 break buffer baseline is `0`. Phase 7 may supply a versioned tick/ATR setup buffer, but must not silently alter historical lifecycle calculations.

Invalidated levels remain historical evidence but are excluded from active validation.

## Consolidation

Canonical baseline detector:

- window = 12 closed bars;
- total zone width = highest high - lowest low;
- confirmation if total width <= `2.0 * ATR14`.

A detected consolidation is emitted as a confirmed `ZONE` with `CONSOLIDATION` evidence type.

## Fail-closed rules

Structure/level calculations fail rather than guess when required closed contiguous candles, pivots, MA history, ATR or provider/symbol consistency are missing.
