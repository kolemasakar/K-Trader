# Deep replacement ATR5 trace and research quality metadata — 2026-10-01

Status: TRACE EXECUTED; DIAGNOSTIC CODE COMMITTED; NEW CI PENDING. No trading gate or owner ATR5 rule changes.

## Reproducible trace
Source: 19-symbol internal historical archive, existing separate staging tree `/data/research/isolated_results/atr5-audit-1f5c1f61`. The read-only Landlock launcher ran a bounded diagnostic against the already CI-validated research code from commit `1f5c1f612394dad88a49e0dfa380bcd544d75ba1`. Full trace is stored on the server as `deep_replacement_trace.json` in that isolated tree.

- AKEUSDT 2026-07-17: initial mean 0.00047810, 3 LARGE exclusions, final ATR5 0.00002344; 8 bars inspected.
- AKEUSDT 2026-07-18: initial five ranges 0.0007723, 0.0011210, 0.0005063, 0.0007347, 0.0000164; initial mean 0.00063014. The fifth bar and 86 older candidates are SMALL relative to the dynamically recalculated five-bar mean. The fifth accepted bar is 2026-04-18, final ATR5 0.00069504; **87 rejected, 92 inspected**. This is an observed discontinuity across a sharp volatility regime change, not evidence of a code crash.
- AKEUSDT 2026-07-19: initial five all accepted, ATR5 0.00072498; 5 inspected, zero rejected.
- AKEUSDT 2026-04-12: 32 SMALL rejected, 37 inspected, oldest accepted 2026-03-07.
- XRPUSDT 2026-08-22: 47 SMALL rejected, 52 inspected, oldest accepted 2026-07-02, ATR5 0.19986. On 2026-08-23, zero rejected and ATR5 0.20964.
- ADAUSDT 2026-08-22: 12 SMALL rejected, 17 inspected, oldest accepted 2026-08-06.

## Experimental quality reporting, not a trade rule
Added `atr5_quality_diagnostic(result, deep_lookback_threshold=20)` to research module and regression test. The helper only reports inspected/rejected counts, oldest accepted timestamp, and `deep_lookback` when inspected >20. The value 20 is a provisional reporting threshold; it is NOT an approved exclusion limit, trading filter, or change to the five-selected-bar iterative ATR5 calculation. Commits `5d1cdba7ddbde6749987607a1820f7f8f2a27164` and `7f8227690010a89e884178f14cd2180a9ce0c591`. CI must be checked.

## Research interpretation and next step
Deep backward replacement is caused by the approved mean-relative SMALL criterion when recent accepted large bars coexist with long stretches of older low-volatility bars. The resulting ATR5 can use nonlocal historical context. Flag these cutoffs in research reports and compare downstream sensitivity in offline strategy backtests; do not silently discard them or change the algorithm without an explicit owner decision. Production app and trading configuration remain untouched.
