# D1/W1 association and HISTORICAL candidate research gate — 2026-09-28

## Implemented
- `scripts/research/gerchik_cross_tf_v0_1.py`: read-only exact decimal price association by symbol across independently formed D1/W1 candidates, preserving independent primary types and source events. This is an association VIEW, **not** an irreversible merge or promotion to CONFIRMED. Rejects future events, wrong timeframes, invalid tick identity, and non-UTC as-of.
- `scripts/research/gerchik_historical_candidates_v0_1.py`: conservative HISTORICAL candidate aggregation requiring >=2 distinct source-bar IDs from *externally structurally qualified* D1/W1 HIGH/LOW events at the exact price. Raw pivot discovery is deliberately absent. No auto-confirmation or trading claims. All event IDs and source bars are retained for downstream review.
- Added separate test files for both modules.

## Verification
- Cross-timeframe module: isolated non-production pytest **8/8 passed** before committing the same logic. No HP-OMEN or production change.
- Historical-candidate tests are committed but **not yet executed** in the current turn; do not count as passing.

## Unresolved research gates
- Upstream structural-event qualification is not yet defined/implemented: `structural_qualification` currently expresses an upstream assertion, not independently verified proof. Do NOT feed ordinary local pivots to this detector.
- `HISTORICAL` here is an unconfirmed recurring qualified-price candidate, not a validated Gerchik level. Human-labelled review and confirmation semantics remain mandatory.
- Cross-TF exact-price association does not establish global primary type or rank; symbol-specific authoritative tick-size and D1/W1 session metadata remain necessary.
- No ATR is used for level creation. Cancelled volatility transition gate stays disabled. Archived pivot detectors remain excluded.
