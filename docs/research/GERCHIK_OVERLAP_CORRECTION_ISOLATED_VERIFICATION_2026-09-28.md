# Overlapping D1/W1 evidence correction: isolated verification

Branch: `research/dual-market-historical-levels-v0-1`.

After the approved change allowing overlapping D1/W1 source candles to reinforce levels, an isolated local reproduction of the corrected historical aggregation and symmetric-luft cross-timeframe code was tested alongside previously reconstructed review-gate and pipeline checks.

Command: `python -m pytest -q tests/test_corrected.py tests/test_pipeline.py tests/test_gate.py`.

Result: **25 passed in 0.12s**. Covered inclusive symmetric luft, overlap acceptance, outside-luft rejection, ambiguity, invalid/missing source intervals, historical overlap acceptance, direct bare-event bypass rejection, duplicate event IDs, review-gate and pipeline chronology. Local test_corrected.py was written for isolated verification and is **not** a byte-identical copy of the full committed GitHub test suite. The original GitHub repository could not be cloned in the runner because DNS for github.com was unavailable. Thus this is an isolated reproduction result, not a claim of full repository CI success.

Production and HP-OMEN were untouched. Existing overlap-exclusion documents are superseded by `GERCHIK_OVERLAPPING_D1_W1_LEVEL_EVIDENCE_CORRECTION_2026-09-28.md`.
