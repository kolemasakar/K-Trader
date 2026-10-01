# ATR5 — canonical approved rules and experimental boundaries (2026-10-01)

**Status:** Owner-approved ATR5 v2 calculation; adaptive v3 remains research-only and NOT approved for trading or deployment. **OWNER PAUSE:** documentation-only synchronization for new-chat handoff. No new tests, CI requests, server commands, merges, deployments or trading changes are authorized.

Primary source: A. Gerchik, *Kurs aktivnogo treydera*, owner-provided project source (bar abnormality discussion). Numeric abnormality thresholds originate from the source; the precise iterative replacement order and implementation tie-break are K-Trader engineering rules, not verbatim book claims.

## 1. Approved ATR5 v2: exact calculation
1. Work only with **fully closed** candles in descending chronological order. At every newly completed candle, calculate ATR5 anew; never use the forming bar or future bars. The five-bar period is owner-selected.
2. Take the **five newest completed bars**, calculate each bar's High minus Low range and compute the arithmetic mean of these five ranges.
3. Against the **current mean of these exact five selected bars**, mark a bar abnormal if its range is **>= 2 times the mean** (LARGE) or **<= one-third of the mean** (SMALL). Boundary comparisons are inclusive.
4. If an abnormal bar exists, exclude **one** such bar and replace it with the **next older unused fully closed bar**. Recompute the mean of the resulting five selected bars and **recheck all five from the beginning**, including bars that were previously normal. Continue until all five satisfy the limits.
5. If multiple bars are abnormal simultaneously, the current deterministic **engineering tie-break** excludes the **newest abnormal bar first**. This tie-break is not separately approved as a source-derived rule and must remain explicit in tests and provenance.
6. If five valid accepted bars cannot be assembled from available older closed history, **fail closed**: report insufficient history rather than inventing ATR5. Enforce unique descending timestamps and valid positive finite ranges.
7. ATR5 is the mean of the **five finally accepted ranges**. Record accepted and rejected bars, rejection reason, reference mean, count inspected and calculation cutoff for research provenance. A new cutoff requires a new calculation; adding irrelevant older history to an already-resolved cutoff must not alter that result.

Current research implementation: `scripts/research/gerchik_filtered_atr5_v1.py` with output policy `iterative-five-selected-recheck-v2`. The historical source file name retains `v1` for compatibility; the **implemented calculation semantics are v2**. Superseded candidate-inclusive rolling-reference v1 descriptions are NOT current rules.

## 2. ATR5's role in K-Trader
- ATR5 measures recent movement energy and informs trade parameters and **trade evaluation** (distance to target, feasibility of movement, SL/TP suitability, entry context, regime and estimate reliability).
- **ATR5 does not construct or shift D1/W1 price levels**; technical structure has priority for SL. ATR5 must not override the approved level and risk contracts.
- The previously proposed blanket rule 'do not trade or analyze levels during transitional volatility' was **withdrawn**. A missing/low-confidence ATR5 estimate is a data-quality condition to handle explicitly, **not** an automatically approved no-trade rule.
- Future trade-evaluation integration is a **requirement**, not evidence that ATR5 v3 is currently integrated with ScoringAgent, RiskManager or any live execution path.

## 3. Adaptive ATR5 v3 — separately agreed experimental hypothesis, not approved replacement
Purpose: reduce v2's deep backward search when volatility changes sharply. Research prototype: `scripts/research/gerchik_adaptive_atr5_v3_experiment.py`.
- Confirm candidate regime only if **three consecutive newest closed bars** individually support a new scale versus the **median of the preceding ten** closed bars. Initial research hypotheses: >=2x median for expansion or <=0.5x median for contraction; these parameters are **not approved trading thresholds**.
- Extend the contiguous qualifying recent segment backward. With **three or four** bars of the new regime, return explicit `NEW_REGIME_WARMUP`, **no finalized new-regime ATR5**. With **at least five**, the prototype computes the mean of the five newest coherent bars without borrowing from the old regime. Otherwise it falls back to v2.
- **Open design issues:** during warmup, research a provisional estimate with transparent confidence so trade evaluation need not stop automatically; early history below the prototype's 13-bar baseline should preserve any valid v2 estimate; define how owner-approved anomaly rejection operates *inside* the confirmed new regime; validate causal stability, threshold sensitivity and independent holdout. The present prototype's five-bar mean in the new regime **does not yet apply the full v2 anomaly-replacement rule**.
- v3 is **not approved for production or trading**, and no experimental result authorizes replacing v2.

## 4. Historical evidence and limitations
- v2 causal historical audit on the internal archive: **19 symbols**, **8,981** D1 cutoffs, **8,902** valid ATR5 cutoffs, **79** insufficient; **1,526 rolling rejection occurrences** (not unique candles). On AKEUSDT 2026-07-18, 87 SMALL candidates were rejected and 92 bars inspected; on XRPUSDT 2026-08-22, 47 SMALL candidates were rejected and 52 inspected.
- Experimental v3 comparison on the same 19-symbol corpus: **8,530** v2-baseline cutoffs, **164** new-regime warmups, **59** new-regime-ready and **228** baseline-insufficient. These are historical cutoff counts, **not trade outcomes**. No demonstrated improvement to S1–S6 profitability or completed independent holdout.
- Research-only `atr5_quality_diagnostic` reports inspected/rejected counts, oldest accepted bar and provisional `deep_lookback` if inspected >20. **20 is a reporting hypothesis, not a trading gate or owner-approved cap**.

## 5. Development and authorization boundary
Approved order **when owner explicitly resumes work**: canonical state and rules -> formalization of levels/ATR/strategies -> predeclared historical protocol and >=6 months data -> S1–S6 at **1R then 3R** (S3 SL beyond level) -> analyze results -> Level Strength v2 -> independent holdout. Do not insert mandatory 2R without owner approval. FREE_ONLY; HP-OMEN prohibited; research isolated and read-only; draft PR #94 remains unmerged. No additional verification while the owner pause remains in force.

Authoritative transition: `docs/operations/K_TRADER_NEW_CHAT_HANDOFF_2026-10-01_OWNER_PAUSE.md`. Supporting checkpoints: `docs/checkpoints/2026-10-01_ITERATIVE_ATR5_19_SYMBOL_HISTORICAL_AUDIT.md`, `docs/checkpoints/2026-10-01_ATR5_DEEP_REPLACEMENT_TRACE_AND_QUALITY_FLAG.md`, `docs/checkpoints/2026-10-01_ADAPTIVE_ATR5_V3_FIRST_19_SYMBOL_EXPERIMENT.md`.
