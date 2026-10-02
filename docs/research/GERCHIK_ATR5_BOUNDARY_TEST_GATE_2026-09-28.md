# ATR5 v1 boundary validation status — 2026-09-28

New research-only test file: tests/test_gerchik_filtered_atr5_boundaries_v1.py, commit d5a10fe3f1e2f02c45295fecaea86e0a2bbced49.

Added 11 tests: equality and just-inside LARGE/SMALL thresholds, minimum older reference history (8 vs 9 closed bars), bounded lookback, no bootstrap when history too short, invalid ranges including non-finite numbers, reversed timestamps, causal as-of independence from future bars, and deterministic repeatability.

**Execution status:** NOT RUN / NOT VERIFIED. The live K-Trader container does not have pytest installed (ModuleNotFoundError). An alternate remote test execution was blocked; no packages were installed and no production configuration was modified. The prior exact-module historical parity audit (584/584 matching as-of results) remains a separate completed validation and must not be conflated with this unexecuted new test suite.

Next gate: run pytest on a separate authorized non-production environment with the exact research branch checked out, e.g. `python -m pytest -q tests/test_gerchik_filtered_atr5_v1.py tests/test_gerchik_filtered_atr5_boundaries_v1.py`. HP-OMEN remains prohibited. After passing, implement seven-type level research detectors according to the current contract, preserving one primary formation type, causal evidence timestamps, D1/W1 HIGH/LOW sources, and no ATR in level creation.
