# S1 ACHC real execution gate — 2026-10-10

## Verified in this attempt

- GitHub Actions CI #365 on commit bf5890450aff4adbfa27c7053b6cfc90cbf09a6a completed **SUCCESS**.
- Real server `k-trader-prod-vnic`: frozen `ACHC.us` D1 input available to current K-Trader container; current container **does not have** `/app/scripts/research` and therefore cannot import the PR #95 Gerchik detector.
- GitHub Actions runner working checkout at `/opt/k-trader/runner/_work/K-Trader/K-Trader` was inspected without modification; the current source tree does not contain `src/ktrader/s1_equity_levels_replay.py`. A successful CI is not evidence of running the new integration against the frozen server-side corpus.
- Existing `scripts/run_readonly_research.py` on default branch was inspected. Its `validate_paths` requires `dataset_summary.json` at archive root, which does not match the MT4 corpus root. Using it directly for the transferred corpus would fail; changing launcher protections/requirements needs a separate explicitly tested integration rather than an unreviewed bypass.
- No full seven-type `ACHC.us` result, approved trading orders, or backtest outcomes were computed in this attempt. No production/container/data modifications.

## Safe execution route to complete

1. Publish a dedicated isolated research job based on the already tested Landlock launcher, with an explicitly validated **read-only MT4 corpus** input contract (manifest plus 840 series and source hashes); retain unprivileged ktrader, separate results directory, bounded memory/time, source-write denial.
2. Check out exact PR #95 commit in the isolated job and run `s1_equity_levels_replay.candidate_levels()` on ACHC.us D1/W1; emit deterministic candidate counts and provenance, not pretend reviewer approval.
3. Integrate candidate formation evidence, owner-approved ATR5 v2, executable entry/stop sizing and both A/B intrabar paths for an explicitly tagged algorithmic scenario. The existing `s1_research_runner` is only a readiness gate. Actual trade outcomes require completion and test proof.

Status: **CI PASS / REAL SOURCE ACCESS PASS / ISOLATED PR95 REAL-DATA EXECUTION NOT YET COMPLETED**.
