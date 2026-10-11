# ATR5 v3 three-bar adaptive regime — first 19-symbol offline experiment

Status: EXPERIMENTAL, NOT APPROVED FOR TRADING. Current owner-approved v2 remains unchanged. Code `scripts/research/gerchik_adaptive_atr5_v3_experiment.py`, tests `tests/test_gerchik_adaptive_atr5_v3_experiment.py`; pinned experiment code commit `c6bb1e76572ac43c7a84b6bc1f077c6006fc7bb8` (CI run 36921969315 pending at report creation).

## Algorithm hypothesis
- Three most recent completed D1 bar ranges must each exceed 2x the median of preceding 10 ranges (expansion), or each be below half that median (contraction). This avoids confirming a regime from one spike.
- Extend contiguous qualifying recent bars backwards against the frozen median. If only 3–4 new-regime bars exist, return `NEW_REGIME_WARMUP` with no ATR5. At 5+, return mean of the five newest coherent bars, without mixing the old regime. Otherwise fall back to existing iterative v2.
- Experimental thresholds 2x/0.5x and median baseline of 10 bars are hypotheses, not owner-approved trading rules. The direct five-bar mean in the confirmed new regime does not yet apply the owner anomaly replacement inside the new regime; this requires additional design review.
- Important limitation: early history below 13 completed bars returns `BASELINE_INSUFFICIENT` even when v2 could already calculate ATR5; a fallback improvement is required before adoption.

## Reproducible run
- Read-only internal native D1 archive, 19 symbols, 8,981 cutoffs; Landlock launcher, 512 MiB / 120 CPU seconds / 180 wall seconds; output isolated at `/data/research/isolated_results/atr5-audit-1f5c1f61/v3_comparison.json`, SHA-256 `1dddd2b6de664acb6daf88a60fabb2d248af2798b36717bfbf1d57a84f19146a`.
- Status totals: V2_BASELINE 8,530; NEW_REGIME_READY 59; NEW_REGIME_WARMUP 164; BASELINE_INSUFFICIENT 228. These are cutoff counts, not independent trades.
- AKEUSDT: 2026-07-17 and 18 WARMUP with 3 and 4 new-regime bars; 2026-07-19 READY, ATR5 0.00072498. Owner v2 on 2026-07-18 had 87 rejected candidates and ATR5 0.00069504.
- XRPUSDT: 2026-08-21 and 22 WARMUP with 3 and 4 new-regime bars; 2026-08-23 READY, ATR5 0.20964. Owner v2 on 2026-08-22 had 47 rejected candidates and ATR5 0.19986.
- No trade-performance conclusions: no S1–S6 backtest, transaction-cost study, or independent holdout conducted for v3.

## Next research gates
1. Preserve v2 availability for early history and report explicit data provenance/quality during transition; compare candidate continuous estimators versus conservative no-value warmup, without silently introducing a trade prohibition.
2. Evaluate sensitivity to baseline length, 3-bar confirmation and regime ratio using separate development/holdout periods, including false regime confirmations and change latency.
3. Decide how the five-bar owner anomaly rules should operate *within* confirmed new regime. Do not silently replace approved algorithm in production.
4. Await CI success and complete independent causal prefix-stability regression for v3 before broader strategy tests.
