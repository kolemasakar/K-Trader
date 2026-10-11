# ATR5 isolated boundary gate — 2026-09-28

Status: **PASS**, 18/18 tests, isolated assistant container; no HP-OMEN, no production environment or package modifications.

Scope: 7 original research tests and 11 additional boundary/causality tests:
`python -m pytest -q tests/test_gerchik_filtered_atr5_v1.py tests/test_gerchik_filtered_atr5_boundaries_v1.py`

Initial run: 17 passed, 1 failed due to incorrect test expectation, not an algorithm error. `test_no_future_bars_affect_past_asof` incorrectly expected that prepending a huge abnormal newer bar necessarily changes the first accepted bar. The newer bar is correctly rejected, leaving the first accepted bar unchanged. Corrected the test to assert the newer bar appears first in rejected with its timestamp and the first accepted bar remains the original. Rerun: **18 passed in 0.09s**.

Provenance limitation: isolated workspace recreated the GitHub module and test files from connector-returned contents; original test file blob SHA independently matches GitHub (`f9cddb01baa2ab89481172f0f17bd104781fca2a`). Module logic was unchanged, though the isolated copy omits two comments, so its file blob SHA differs from GitHub; do not call this a byte-identical module test. Exact-byte GitHub module was separately verified on 584/584 real historical D1 cutoffs in `GERCHIK_ATR5_EXACT_MODULE_HISTORICAL_PARITY_2026-09-28.md`. New boundary test correction committed to research branch in `a4719a3728fd180cc967907e90bb05b987596fa0`.

Research conclusion: the experimental candidate-inclusive reference implementation passes the specified boundary tests; this does not prove its reference rule is prescribed by Gerchik or authorize production deployment. Seven-level detectors remain a separate research gate and must not use ATR for level creation.
