# Trap Specification v1.0

## Goal

Detect failed breaks/liquidity sweeps that can provide setup context.

## Canonical sequence

liquidity level -> sweep -> break -> failure to continue -> return through level -> confirmation

## Output

Each trap event records:
- provider_id
- symbol
- direction
- reference level
- sweep timestamp/distance
- failure timestamp
- return timestamp
- confirmation state
- strength
- invalidation reason

## Rules

- A sweep alone is not a trap confirmation.
- A trap without return/failure evidence cannot validate a setup.
- Trap evidence must be evaluated together with levels, HTF structure and VSA.
- Event state transitions must be replay-testable and deterministic.
