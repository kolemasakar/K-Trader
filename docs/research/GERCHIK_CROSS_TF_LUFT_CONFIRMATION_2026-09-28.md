# D1/W1 level confirmation within symmetric luft — user refinement 2026-09-28

Supersedes the **exact-price-only** cross-timeframe matching criterion in `gerchik_cross_tf_v0_1.py`. That module remains a legacy research comparison and is not the new confirmation authority.

## Approved matching rule
Independently qualified D1 and W1 level formations for the same instrument mutually confirm when `abs(D1_price - W1_price) <= luft`, inclusive in either direction. The later formation timestamp is the earliest confirmation time; no backdating. Preserve both original HIGH/LOW-derived tick-aligned prices and both source primary types/provenance. Do not invent a midpoint or reassign the primary type.

Existing project trading-buffer definition is `luft = 0.2 * BaseStop`, tick-rounded upstream. The new matching module accepts the **externally calculated** instrument-specific luft as an explicit argument; it does not compute ATR or stop size, and does not reactivate ATR-based level creation. A separate research decision may be needed if the trading-entry buffer and structural level-matching tolerance should ever diverge.

## Implementation
`scripts/research/gerchik_cross_tf_luft_v0_2.py`; `tests/test_gerchik_cross_tf_luft_v0_2.py`. Only upstream-marked structurally qualified candidates can confirm. Missing luft, unqualified candidates, future observations and ambiguous many-to-one matches cannot yield automatic confirmation. Confirmation is a cross-timeframe evidence finding; downstream global level identity/primary-type consolidation remains unresolved.

**Test status:** test suite committed but not executed/verified at this documentation checkpoint. Do not report it as passing until a separate test run succeeds. No production deployment or live trading authorized.
