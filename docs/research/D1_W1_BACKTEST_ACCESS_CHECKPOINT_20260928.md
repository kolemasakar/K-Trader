# K-Trader D1/W1 backtest access checkpoint — 2026-09-28

## Authorization boundary
The owner suspended access to AI_Trading_System during development. Do not access that system by SentinelX, SSH or any other route. The user explicitly authorized reuse of historical archives **already obtained by K-Trader** for research and backtests. No production trading, live risk gate changes, or remote AI_Trading_System access authorized.

## Current observed K-Trader access
- K-Trader production SentinelX host: `k-trader-prod-vnic`.
- `sentinel_list` for the previously observed in-container archive path `/data/research/phase11g/historical_recovery_v1/approved_seven_year_20260925/bundles` returned `path_not_allowed`. This does not establish that the archive is missing; the path was previously read **inside a Docker container**, not through SentinelX file_ops.
- SentinelX configured read-only host paths include `/opt/k-trader/releases` and `/opt/k-trader/data`. The latter returned zero visible entries on a direct list.
- Do not enlarge privileges automatically or treat a container path as an equivalent host path.

## Research protocol
Run only D1 and W1 strong-level discovery. Lower timeframes H4/H1 are context and M15/M30 are entry timing; no independent lower-TF levels. No ATR in discovery, grouping, zone width or scoring. ATR Energy Engine is separate and downstream.
- First: confirm exact location and SHA256 of K-Trader-owned, already-obtained 7-symbol OHLCV bundles; if necessary, have authorized K-Trader operator export read-only copies into a dedicated research path.
- Second: execute `tests/test_atr_free_level_validation_v1.py` and `scripts/research/atr_free_level_validation_v1.py --timeframes 1d 1w` on the authorized copy.
- Third: inspect sample sizes, early/late split and matched random price controls. W1 only has ~52 bars in a 1-year archive, so the current 20-bar warmup plus 34-bar complete-future-window condition may leave **zero eligible weekly observations**. Report this explicitly and do not misrepresent empty W1 results. Longer authorized history or an explicitly pre-registered weekly protocol will be required.
- Fourth: independently implement structural grouping and entry-signal tests, only after level quality is established. No live orders.

## Status
GitHub runner default corrected to D1/W1. Actual archive-based D1/W1 run **not completed** because host-level read access to the archive is not configured and no authorized copy was found in the current visible host path. Previous exploratory D1 diagnostic remains distinct from the pending independent test.

## Verified 2026-09-28: approved route works
K_Sentinel owner instructions: https://github.com/kolemasakar/K-Trader/pull/87#issuecomment-5870647330. Host /opt/k-trader/data is mounted as /data in existing container k-trader-ktrader-1. SentinelX file_ops remains blocked by Unix permissions; do not change ACLs or privileges. Approved bounded sentinel_exec Docker route read both the canonical manifest.json and validation_report_v1.json successfully on this date. Manifest cohort: 7 crypto symbols, 6 timeframes, 42 files, 2025-09-25 through 2026-09-25 exclusive, RETROSPECTIVE_RECOVERY, research_only=true, not_first_seen=true, FETCH_COMPLETE_NOT_BACKTEST_VALIDATED. Validation report status PASS_WITH_WEEKLY_BOUNDARY_CAVEAT: 42 files previously hash-verified by source audit, zero hash failures and zero internal gaps. The current session has **not independently recomputed file hashes**, nor run the new D1/W1 research script on host.

**Important W1 correction:** source audit says prebuilt W1 excludes opening partial week but includes closing partial week. Before strong-level research, construct causal W1 aggregation from D1 bars including **only fully closed calendar weeks**; crosscheck boundaries rather than treating prebuilt 1w as clean full-week bars. Only 365 daily candles and ~52 weekly candles; flag zero or insufficient W1 test samples, use W1 for context rather than an unsupported standalone reliability claim. D1 is the primary level-validation test.

**Execution recommendation:** the approved container path is `/data/research/phase11g/historical_recovery_v1/approved_seven_year_20260925/bundles`. Have the already-authorized K-Trader research process (not AI_Trading_System) perform an independent source SHA256 check and synthetic tests, then run D1 diagnostics; run W1 only after causal full-week construction. If the new runner is not present inside the production image, do not deploy it silently or alter the healthy production container; use an authorized research runtime with a :ro bind mount of the approved cohort.
