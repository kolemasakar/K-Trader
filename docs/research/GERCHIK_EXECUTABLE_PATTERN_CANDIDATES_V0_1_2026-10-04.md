# S1–S6 executable pattern candidates v0.1 — 2026-10-04

Status: PARAMETERIZED ENGINEERING CANDIDATES / NOT OWNER-FROZEN RUN SPECIFICATION.

Implementation: `scripts/research/gerchik_strategy_patterns_v0_1.py`. This completes an executable pattern layer for all six restored identities, not the remaining current-engine parameter migration or automatic level classification. No strategy outcomes were computed.

## Shared executable semantics

The LONG equations below operate in integer ticks. SHORT is the exact sign-reflected version. L is exact confirmed level price; B is explicit positive stop-buffer ticks; E is explicit entry-tolerance ticks; D and P are explicit positive breakout/penetration ticks. None is inferred from contextual D1/W1 tolerance or converted from ATR14.

All bars must be consecutive, fully closed at/before as_of, and have valid integer-tick OHLC. A caller supplies a CONFIRMED D1/W1 Gerchik primary type, formation provenance, known_at, tick size and independent context-admission provenance. The level must have been available before the first qualifying pattern bar opened. This validates declarations and chronology; it does not independently establish whether the upstream formation deserves confirmation, or whether the level was invalidated. Caller must supply its correct historical state.

Each successful candidate emits a frozen execution Setup at the final completed bar end, exact tick stop evidence and pattern bar timestamps. Next-open simulator consumes subsequent bars only. Tick-size conversion occurs at this boundary; simulator still uses floating-point prices. Candidate detector never submits orders or changes production.

An explicit engineering confirmation policy C must be supplied: DIRECTIONAL_CLOSE means current close > current open; CLOSE_BEYOND_PREVIOUS_EXTREME means current close > previous high. These two policies are proposed alternatives, not recovered owner definitions. No default policy is selected by the detector.

| Strategy | Executable LONG predicate | Technical stop | Authority / open choice |
|---|---|---|---|
| S1 level rejection | Before first bar: close > L. First bar low == L and close > L. Second bar low in [L,L+E], close > L, and C(second). | min(first low,second low)-B | Proposed two-bar precision candidate based on known exact-first/tolerant-second distinction; does not claim a complete sourced BSU/BPU state machine. Full confirmation semantics remain to be frozen. |
| S2 breakout continuation | Pre-break close <= L; breakout close >= L+D; next bar close > breakout close and C(next). | L-B | Family restored; confirmation C and migrated D/B remain explicit proposals. |
| S3 breakout and retest | Pre-break close <= L; breakout close >= L+D; retest 1–6 bars later, low in [L-E,L+E], close > L; intermediate closes > L. C applies either on retest bar or next bar, according to supplied resume policy; final close > L. | L-B | Owner stop-beyond-level preserved. Requiring no intervening close back through L, retest tolerance and same/next-bar confirmation are declared engineering choices. |
| S4 one-bar false breakout | Previous close > L; signal low <= L-P; signal close > L. | signal low-B | Restored family; penetration/stop migration needs concrete units and values. |
| S5 multibar false breakout | Prior close > L, then an uninterrupted suffix of 2–N closes < L, then return close > L. Count entire suffix; never truncate an overlong excursion to make it pass. | lowest low of outside+return structure-B | Baseline N=4, max total structure 5; separate up-to-six-total-bars variant N=5, max total 6. All bounds are explicit inputs; no variant chosen automatically. |
| S6 trend range breakout | Signal close > highest high of previous 20 completed bars; EMA50 trend policy either close > EMA50 or rising EMA50. EMA computed over all supplied closes, first-close seed, alpha=2/51; require >=51 bars. | Explicit local-window lowest low-B OR signal close minus supplied ATR-distance ticks. | 20/50 identities restored; trend-policy/seed/local-window branch and ATR-distance migration are declared choices. No archived ATR level/proximity logic is imported. |

The S6 signal bar is excluded from the prior-range bound. Its independently calculated EMA and stop may consume that newly completed signal bar; availability remains at its close. Range-history start is the earliest qualifying pattern timestamp for level admission. ATR-distance is a supplied trade parameter; this module neither calculates ATR nor uses it to create or strengthen levels. If a protocol later uses 1.5×D1 ATR5, that migration must be explicitly specified and validated first.

S5 outside-bar count is separate from total structure length. The six-bar variant is an engineering interpretation of the recovered up-to-six structure, not a claim that five outside closes were unambiguously owner-approved.

## Input/output and remaining work

Use `detect(strategy_id, side, level_context, closed_tick_bars, parameters, as_of=...)`. Every Parameters field is required; no market parameter defaults. Return status is CANDIDATE, NO_PATTERN, INSUFFICIENT_HISTORY, LEVEL_UNAVAILABLE, LEVEL_UNAVAILABLE_AT_PATTERN_START or INVALID_STOP. Malformed/future/gapped inputs raise ValueError. Detector is stateless: setup deduplication, multiple-level conflicts, overlapping exposure and selection of eligible contextual events are caller responsibilities.

The candidate protocol now links code/specification hashes as preparation references. Its executable_spec_sha256 fields remain null because a complete strategy specification also needs the actual selected parameter set and upstream admission policy; candidate artifact references are not a frozen strategy digest. Generic unresolved labels are replaced by per-strategy gaps. Do not clear them merely because synthetic tests pass.

Validation: 13 new test methods cover all six LONG/SHORT patterns, thresholds, precision distinction, retest 6/7 boundary, S3 stop placement, confirmation availability, S5 full suffix/variant, S6 range/ATR branch, causal level admission, future/gap rejection and detector→1R simulator handoff. Combined local suite: 60 passed on Python 3.12; package-import smoke check passed. This is synthetic correctness evidence, not profitable market performance. Previous protocol commit 67d6383 CI run 37199914772 succeeded; new-change CI checked separately.

Remaining scientific run prerequisites are explicit: freeze these proposed predicates with current price/ATR units, source a independently valid causal level ledger, determine study/warmup and execution profile, document historical/proxy costs, enforce declared bounded read-only execution, and then run 1R. Independent untouched control remains a later validation requirement and cannot be replaced with the already inspected year segment.
