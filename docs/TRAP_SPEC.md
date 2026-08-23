# Trap Specification v1.1

## Goal

Detect failed breaks/liquidity sweeps around confirmed support/resistance that can provide setup context.

A trap is evidence, not a trade signal.

## Eligible levels

Automatic trap detection uses only levels with:

- status `CONFIRMED` or `MIRROR`;
- side `SUPPORT` or `RESISTANCE`;
- matching provider and symbol.

FLOATING, BROKEN, INVALIDATED and generic ZONE levels cannot independently create a trap event.

## Canonical v1 sequence

`confirmed level -> break/sweep -> failure/return -> directional confirmation`

### LONG trap

Against SUPPORT:

1. a closed bar closes below `level.lower - min_break`;
2. the excursion low becomes the sweep extreme;
3. within the return window a closed bar closes back at/above `level.lower`;
4. within the confirmation window a later bar closes above the return bar high.

### SHORT trap

Against RESISTANCE:

1. a closed bar closes above `level.upper + min_break`;
2. the excursion high becomes the sweep extreme;
3. within the return window a closed bar closes back at/below `level.upper`;
4. within the confirmation window a later bar closes below the return bar low.

## Canonical defaults

- `min_break_atr_fraction = 0.05`
- `min_break = ATR14 * 0.05`
- `max_return_bars = 3`
- `max_confirmation_bars = 2`

These are versioned/configurable heuristics and may be changed only through an explicit spec/config update.

## States

- `RETURNED`: break and return occurred but directional confirmation is still absent.
- `CONFIRMED`: break, return and confirmation completed.
- `EXPIRED`: break occurred but price did not return through the level within the configured window.

A sweep/break alone is never a confirmed trap.

## Output

Each `TrapEvent` records:

- provider_id
- symbol
- timeframe
- direction
- level_id / level_side
- reference zone bounds
- break timestamp / close
- sweep extreme / distance
- return timestamp
- confirmation timestamp
- status
- confirmed flag
- reason when incomplete/expired

## Integration rules

- Trap evidence is evaluated together with HTF structure, active MTF levels and VSA.
- Trap confirmation does not produce LONG/SHORT by itself.
- Phase 7 decides trap contribution to Setup Score/rating.
- No cross-provider trap/level fusion is allowed.
