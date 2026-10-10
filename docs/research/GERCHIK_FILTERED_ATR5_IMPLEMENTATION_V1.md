# Filtered ATR(5) research prototype v1 — 2026-09-28

Status: experimental research implementation, not approved as a Gerchik-prescribed reference formula; no production changes.

Source of truth: GERCHIK_FIXED_LEVEL_CLASSIFICATION_CONTRACT_V0_1.md. Five completed D1 bars, newest-to-oldest. Exclude range >= 2 x reference or <= reference / 3. Preliminary newest-bar bootstrap uses mean of its five consecutive completed bars. If newest is abnormal, shift seed backward until newest is normal.

**Proposed deterministic resolution for remaining four bars:** scan backward, evaluating each candidate against the arithmetic mean of that candidate and its four immediately older completed D1 bars. This window is independent of accepted newer bars. Reject abnormal candidates and continue scanning backward; retain exactly five normal bars. Never re-evaluate accepted candidates. Final ATR(5) is mean of accepted ranges. This is a proposal, NOT uniquely specified by the book and NOT a volatility trading gate.

Maximum inspected input: 250 completed bars; a candidate requires four older reference bars. If fewer than five accepted normal bars are found within this bound, raise InsufficientHistory. Caller must supply only completed D1 bars in newest-to-oldest order; do not include the current unfinished bar. Every selected/rejected candidate logs timestamp, range, reference, and rejection reason.

Worked synthetic examples, newest first:
- [10 x 12] => ATR 10; no rejections.
- [40, 10 x 12] => reject first LARGE, shift bootstrap => ATR 10.
- [1, 10 x 12] => reject first SMALL, shift bootstrap => ATR 10.
- [10,40,10,1,10 x 15] => accept first 10, reject 40 LARGE, reject 1 SMALL, replace older => ATR 10.
- [20,7.5 x 4,10 x 12] => first reference 10, reject 20 at exact 2x threshold.
- [2,7 x 4,10 x 12] => first reference 6, reject 2 at exact 1/3 threshold.

Seven synthetic tests passed in an isolated local execution before GitHub submission. Repository CI and K-Trader native-history verification remain PENDING. Do not treat synthetic examples as historical validation. No HP-OMEN or external K_AI/MT4 data used.
