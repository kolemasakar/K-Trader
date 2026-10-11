# US equity Gerchik level adapter — 2026-10-10

Owner requested adaptation of **existing** level algorithms for S1 / ACHC.us. Research-only PR #95.

## Reused, not reimplemented
- Original `scripts/research/gerchik_seven_types_v0_1.py`, `gerchik_strict_candidates_v0_1.py`, `gerchik_level_strength_v0_1.py` sourced from research branch / draft PR #94.
- Same seven source-extremum Gerchik algorithms, one primary type, evidence timestamps and no ATR in level formation.
- Added explicit `US_EQUITY_SESSION_WALL_CLOCK` calendar allowing strictly ordered non-overlapping daily and weekly bars with session gaps.
- Historical 24/7 crypto policy remains unchanged.
- GAP type suppressed for US equity sessions pending separately verified exchange open-gap definitions; do not infer genuine exchange gap from disjoint OHLC ranges without session policy.
- Broker-wall-clock OHLC row conversion in `src/ktrader/s1_equity_level_rows.py`, with weekly groups finalized only after a subsequent ISO week observation.
- `src/ktrader/s1_existing_levels_bridge.py` now dispatches US equities only with explicit matching policy calendar.
- Tests added for session-gap handling, incomplete latest week exclusion and calendar-scoped detector call.

## Scope and safety
- Synthetic wall-clock numeric epoch is a chronology coordinate only; it does not mean UTC actual exchange time.
- Level outputs are `RESEARCH_CANDIDATE`; independent review/tick provenance not falsely asserted.
- No actual trading/order connection or frozen archive change.
- Before full ACHC.us S1 execution: test latest branch CI, run session level detector on real D1/W1 rows, connect level evidence and ATR5 to S1 BPU order lifecycle, validate costs/Point and two fixed intrabar scenarios. No profitability claim until this completes.
