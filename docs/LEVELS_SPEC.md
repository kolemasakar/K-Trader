# Levels Specification v1.0

## Level types

- trend-break
- historical
- mirror
- limit
- paranormal-bar
- consolidation

## Level object

Required fields:
- provider_id
- canonical_symbol
- price / zone bounds
- type
- timeframe
- strength
- touches
- created_at
- last_test
- confirmed
- invalidated
- invalidation_reason

## Rules

- A floating/unconfirmed level cannot independently validate a trade.
- Level strength is determined by deterministic, versioned rules.
- Multiple nearby levels may form a zone but original evidence is retained.
- Broken levels may transition to mirror status only after defined confirmation.
- Invalidated levels are retained historically but excluded from active validation.

## MTF use

Higher-timeframe levels have explicit priority/weight. Lower-timeframe entries must be evaluated relative to the active HTF map.
