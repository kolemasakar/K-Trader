# Levels Specification v1.1

## Level types

Supported evidence types:

- `TREND_BREAK`
- `HISTORICAL`
- `MIRROR`
- `LIMIT`
- `PARANORMAL_BAR`
- `CONSOLIDATION`

Automatic Phase 5 generation is defined for HISTORICAL and CONSOLIDATION. TREND_BREAK and MIRROR are lifecycle evidence. LIMIT and PARANORMAL_BAR require explicit upstream evidence until an automatic geometry rule is versioned.

## Level object

Required fields:

- provider_id
- canonical symbol
- timeframe
- lower/upper zone bounds
- side: SUPPORT / RESISTANCE / ZONE
- status
- evidence types
- touches
- strength
- created_at
- last_test
- break_time where applicable
- invalidation_reason where applicable

## Historical level construction

Historical levels are built from confirmed swing highs/lows.

Same-side swings are clustered with:

`radius = ATR14 * zone_atr_fraction`

Canonical baseline:

`zone_atr_fraction = 0.15`

The original swing evidence is not fused across providers or symbols.

## Confirmation and strength

- 1 touch -> FLOATING / WEAK
- 2 touches -> CONFIRMED / MODERATE
- 3+ touches -> CONFIRMED / STRONG

A FLOATING level cannot independently validate a trade.

## Lifecycle

Canonical statuses:

`FLOATING -> CONFIRMED -> BROKEN -> MIRROR -> INVALIDATED`

- CONFIRMED support breaks on closed close below lower boundary minus buffer.
- CONFIRMED resistance breaks on closed close above upper boundary plus buffer.
- BROKEN level is not active trade-validation support/resistance.
- Broken support may become MIRROR resistance only after retest from below and close below old zone.
- Broken resistance may become MIRROR support only after retest from above and close above old zone.
- Failed mirror is INVALIDATED.
- Invalidated levels remain historical but are excluded from active validation.

Canonical Phase 5 break buffer = 0. Setup-specific buffer may be supplied later only by a versioned Trading Engine rule.

## Consolidation

Canonical Phase 5 detector:

- 12 closed-bar window;
- zone = highest high to lowest low;
- valid consolidation when total width <= 2.0 * ATR14.

The result is a confirmed `ZONE` carrying `CONSOLIDATION` evidence.

## MTF priority

Canonical level ordering:

`1d > 4h > 1h > 15m > 5m`

Higher-timeframe levels have explicit priority for context, but lower-timeframe evidence is retained rather than silently deleted or overwritten.

Nearest support/resistance lookup uses only active CONFIRMED or MIRROR levels. FLOATING, BROKEN and INVALIDATED levels cannot act as active validation levels.

## Source integrity

- Cross-provider level evidence is not merged into one level object.
- Provider/symbol/timeframe identity is preserved.
- Missing/gapped/open candle history cannot create confirmed automatic levels.

See `MARKET_STRUCTURE_SPEC.md` for swing/regime/session context.
