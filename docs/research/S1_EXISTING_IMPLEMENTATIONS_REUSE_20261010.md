# Reuse audit: ATR5 and Gerchik levels (2026-10-10)

**Owner clarification:** Existing owner-approved research algorithms must be reused, not reimplemented.

## Confirmed existing implementation
- Source branch: `research/dual-market-historical-levels-v0-1`, draft PR #94.
- Approved ATR5 v2 decision: `docs/research/ATR5_GERCHIK_OWNER_DECISION_2026-10-01.md`.
- Real code: `scripts/research/gerchik_filtered_atr5_v1.py`; historical filename **v1**, execution policy **iterative-five-selected-recheck-v2**; completed D1 newest-first, exclude anomalous bars inclusive at >=2x or <=1/3x, replace newest abnormal first, recheck all 5, fail closed. Existing historical audit: 19 symbols, 8,981 D1 cutoffs, 8,902 valid, 79 insufficient (not strategy outcomes). Existing full owner policy is authoritative.
- Copied canonical file unchanged from PR #94 to PR #95, and replaced older experimental `src/ktrader/s1_atr5.py` with a compatibility wrapper mapping ascending MT4 D1 `open_time/high/low` records into canonical descending `DailyBar`. The wrapper returns the canonical result and offers audit trace.
- Level detector already exists at `scripts/research/gerchik_seven_types_v0_1.py`, with `detect_all()` and `ResearchPolicy`, plus reviewed rating at `scripts/research/gerchik_level_strength_v0_1.py`. Prior seven-type 24/7 crypto research replay and 107 tests documented. It is **not** a general US-equity engine as-is: `ResearchPolicy.validate()` demands `UTC_CONTINUOUS_24_7` and `detect_all()` checks complete 24h D1 / Monday-start UTC weekly bars. ACHC.us has broker-wall-clock US equity session bars, not this calendar.
- Added `src/ktrader/s1_existing_levels_bridge.py` and a test to reuse `detect_all()` only where supported and reject silent application to US equities. This bridge requires the existing detector dependency tree from PR #94 on a properly merged/ported branch.

## Remaining to run the requested S1 on ACHC.us
1. Session-aware adapter to existing D1/W1 pattern detector (not a new classifier); must handle US-equity session D1 and W1 formation while retaining known_at chronology and witness provenance.
2. Attach verified source levels and admissible strengthening evidence at each M5 cutoff. Research candidates/provisional rating are not equivalent to independently approved review; report diagnostic-only runs distinctly where proof unavailable.
3. Reuse any existing S1 order-formation implementation after locating its actual source and interface; `src/ktrader/s1_setup.py` is currently only a partial gate, and `s1_intrabar.py` is only an execution kernel. No claim full orders implemented.
4. End-to-end S1 algorithmic wall-clock replay for ACHC.us; preserve unknown exchange calendar and transaction-cost caveats; never invent net profitability.

**Status:** reuse integration for ATR5 committed; existing level detector located and bridged with explicit scope protection. Full US-equity S1 backtest remains unexecuted, production unchanged. Verify fresh CI for ATR5 wrapper before promotion.
