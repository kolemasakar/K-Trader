# ATR5 reference-semantics gate — 2026-10-01

Status: OPEN DESIGN QUESTION / RESEARCH ONLY. Passing CI is not approval of the reference rule.

## Agreed, unambiguous
At each newly CLOSED D1 cutoff, traverse from the newest completed candle backwards, skip paranormal ranges and collect the five most recent accepted normal bars. ATR5 is the arithmetic mean of their five High-Low spans; advancing the cutoff must recalculate the window. Large is >= 2 × reference ATR; small is <= reference ATR / 3. No forming or future bars.

## Critical unresolved distinction
Gerchik's source gives the exclusion thresholds and replacement principle, but does not specify a mathematically unique bootstrap and iterative reference rule for this software. The current experimental implementation uses **candidate + four immediately older raw bars** as its reference at every inspected position, including positions where those four older bars may themselves be anomalous. It does not recalculate the reference from five accepted bars after each replacement. This is a meaningful difference from the owner's requested iterative five-normal-bar approach and must be reviewed rather than hidden behind green CI.

## Reproducible worked examples, newest first
A: [10,10,10,10,10,10] => ATR5=10 at first cutoff. On the next completed normal bar of range 14, newest-first [14,10,10,10,10,10] => ATR5=10.8 if 14 is accepted. ATR5 is **not** constant across cutoffs.
B: [40,10,10,10,10,10,...] => candidate-inclusive reference at newest bar = (40+4*10)/5=16; 40>=32 so reject 40. A baseline from five older normal bars would be 10 and also reject 40. Both yield 10 after replacement here.
C: [20,7.5,7.5,7.5,7.5,10,...] => candidate-inclusive reference for 20 is 10 and rejects 20 at the exact >=2 boundary; an older five-normal-bars bootstrap might choose a different reference and verdict depending on the full older series. Boundary tests currently assert **the experimental candidate-inclusive policy**, not universal compliance.
D: Consecutive abnormal or alternating very small/very large bars can contaminate the raw four-bar reference; therefore rejection outcomes may differ between candidate-inclusive raw and reference computed from accepted normal bars. Compare both implementations on deterministic examples and historical prefixes; quantify divergent cutoffs before selecting a canonical rule.

## Required acceptance gates
1. Document the exact bootstrap window and the reference used when inspecting the first bar; specify how each subsequent reference is updated after rejection and whether the current candidate participates in its own threshold.
2. Ensure five accepted bars are selected in reverse chronological order, with explicit insufficient-history failure when replacement or reference history is missing. Exact-threshold floating-point tests must not rely on accidental rounding.
3. Test at each successive cutoff (ATR5 allowed/expected to change), same-cutoff stability against *irrelevant* older observations, adjacent/alternating anomalies, and no future leakage.
4. Only after these decisions and CI, run the actual read-only historical audit. The D1 continuity preflight (19/19 source files pass) is not that audit.

Until the reference mechanics are approved, preserve the existing algorithm as EXPERIMENTAL; do not use its output for production trading or claim historical validation.
