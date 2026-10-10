# ATR5 trade evaluation v0.1 — research diagnostics
Date: 2026-10-02. Status: IMPLEMENTED / SYNTHETIC TESTS PASSED / NOT HISTORICALLY VALIDATED.

Owner resumed implementation with «продовж реалізацію». This resumes research development, not live orders, merging PR #94 or production deployment. FREE_ONLY and the HP-OMEN exclusion remain binding.

## Contract
Module: `scripts/research/gerchik_atr5_trade_evaluation_v0_1.py`; entry point: `evaluate_trade`.

- Input: immutable newest-first D1 records with source timestamp, explicit UTC-aware availability time `closed_at`, High/Low; decision cutoff, LONG/SHORT, precomputed technical entry/SL/TP and source identifier.
- Reject future, overlapping, duplicate, naive-time and unordered records. Normalize timestamps to UTC before comparing. A candle whose availability instant equals the cutoff is allowed. Caller supplies truly completed D1 candles and independently verified provenance; the module does not discover session calendars or verify file hashes.
- Calculate binding v2 through the existing module without changing its thresholds or replacement order. Default max_lookback=250 preserves the existing implementation convention, not a newly approved trading restriction.
- Preserve accepted/rejected bars, inspected count and diagnostic deep lookback. Failed assembly returns explicit INSUFFICIENT_HISTORY, null ATR metrics and intact technical geometry.
- Report gross RR, stop distance / ATR5, target distance / ATR5 and optionally observed session High-Low / ATR5. These are descriptive ratios, not probabilities of reaching TP or a directional remaining-energy budget. Do not clamp a session ratio above 1.
- Optional `include_v3=True` produces a separately labelled comparison with NOT_APPROVED_FOR_TRADING. v2 remains present independently, including with 5–12 source bars when v3 lacks baseline history, and during v3 warmup.
- No confidence score, numeric trade gate, sizing, orders, level construction, level shift or alteration of SL/TP. The module is not wired into production analyzer, scoring or execution.
- Historical spread, fees, slippage and funding are not inputs to this gross-geometry diagnostic. Net expectancy must be evaluated by the later frozen backtest protocol.

## Evidence
11 synthetic unittest cases passed locally, plus Python compilation. Cases cover mirrored LONG/SHORT, replacement provenance, same-cutoff invariance, future cutoff, timezone-equivalent duplicate, malformed geometry, v3 opt-in, early-history v2 preservation, warmup separation, insufficient history and session-range ratio above 1.

This is first infrastructure for the planned ATR trade-evaluation role. It is not complete adaptive-v3 integration, proof of profitable strategies or a completed historical/holdout audit. Repository-wide pytest and remote CI have not been verified for this change.

## Next research gate
Restore authoritative executable S1–S6 definitions and prerequisites, resolve contextual tolerance conventions explicitly, freeze causal execution/cost/split protocol and inventory at least six months of executable lower-TF data. Then 1R before 3R, analyze, develop Level Strength v2 and independently validate reserved holdout.
