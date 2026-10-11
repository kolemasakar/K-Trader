# ATR5 outlier clustering and W1 prefix regression — 2026-10-01

Research-only follow-up to `2026-10-01_ITERATIVE_ATR5_19_SYMBOL_HISTORICAL_AUDIT.md`. No live orders or production application changes.

- Added deterministic W1 prefix-stability regression `test_complete_w1_pivots_are_prefix_stable_across_daily_cutoffs` in `tests/test_gerchik_causal_historical_audit_v0_1.py`, commit `e35e3ad09c365a73e62a1fc42b80cff1068fd9d1`; CI run 36920887820 started; final outcome must be checked before marking passed.
- Executed follow-up on the server using the previously staged and CI-approved research modules at `1f5c1f612394dad88a49e0dfa380bcd544d75ba1`, inside the existing Landlock launcher, read-only archive, bounded 512 MiB / 60 CPU sec / 90 wall sec. Diagnostic output: `/data/research/isolated_results/atr5-audit-1f5c1f61/ake_diagnostic.json`.
- AKEUSDT 309 rejected occurrences across rolling D1 cutoffs: 116 LARGE and 193 SMALL. Monthly concentration: 2026-04 58, 2026-07 115, 2026-08 32. On 2026-07-18 cutoff, 87 candidate bars were sequentially rejected. These are rejection occurrences, not unique anomalous candles.
- Other examples of deep replacement: XRPUSDT 2026-08-22 cutoff 47 rejected candidates; ADAUSDT same cutoff 12. Thus this phenomenon is not unique to AKEUSDT.
- AKEUSDT mean daily High-Low range varies substantially by month in the source (e.g. March 2026 0.0000295; July 2026 0.00062705; August 2026 0.0019695); this is descriptive only and does not establish cause of each rejection.

Next research gate: inspect exact selected five ranges and rejection trace at 2026-07-18 AKEUSDT, compare neighboring cutoffs, distinguish expected response to volatility regime changes from pathological replacement depth. Add trace/diagnostic output without changing the owner-approved selection rule; consider a separate research quality flag for exceptionally deep lookback rather than silently accepting it for trading. Test W1 regression in CI before proceeding to strategy backtests.
