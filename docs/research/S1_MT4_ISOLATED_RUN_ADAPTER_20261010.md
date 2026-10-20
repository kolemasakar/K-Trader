# S1 MT4 isolated-run update — 2026-10-10

## Implemented
- Extended existing `scripts/run_readonly_research.py` validation to accept either canonical `dataset_summary.json` research archive or the *verified MT4* root containing `full_corpus_series_validation_20261009.csv` and `research_max_available/normalized/`. Existing source/result separation, no-root, Landlock, memory/time and file limits remain unchanged.
- Updated Landlock source-write self-test to select MT4 manifest when canonical summary absent. It reads the manifest and attempts only to open the source for writing; any write permission causes a failed self-test.
- Added regression for MT4 fixture: deliberate rejection of source under `/tmp`, preserving canonical launcher isolation.
- GitHub CI #370 **FAILED** after first test erroneously used a `/tmp` source, violating the launcher's existing security policy. The test was corrected without relaxing that policy in commit `95fcb2a682f8e5b5ad8e2f14db37a9dc9e43d200`. Fresh CI result pending.

## Execution status
- PR #95 research code is not deployed in the current K-Trader production container nor the inspected checked-out runner source. The verified MT4 corpus remains available read-only in the container.
- No safe confirmed means to run the new PR code against host MT4 corpus has been exercised yet. Do **not** claim a full seven-type real-symbol replay, real S1 trades, or b​​acktest outcomes.
- Next actual execution is an isolated PR #95 checked-out job as user `ktrader`, using the bounded launcher and a separate writable result directory, with the frozen data mounted read-only and a prior Landlock source-write-denial self-test.

No production/trading changes.
