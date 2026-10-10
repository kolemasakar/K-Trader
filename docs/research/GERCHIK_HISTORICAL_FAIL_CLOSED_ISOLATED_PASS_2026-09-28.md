# Historical fail-closed direct-call gate — isolated test result

Source branch: `research/dual-market-historical-levels-v0-1`. Local test reproduction reconstructed source from GitHub connector responses, rather than a full byte-identical repository checkout; network git clone unavailable in isolated runner.

- Updated historical candidate regression suite: **11 passed** (`pytest -q tests/test_gerchik_historical_candidates_v0_1.py`).
- Same suite plus three additional isolated wrapper/invalid-review integration checks: **14 passed**. Re-run after UTC timestamp-order fix: **14 passed**.
- The extra three checks were local-only and not committed as a repository test file at this checkpoint. Main 11 regression tests are committed.

Changes: historical entrypoint requires complete source-bar-review bundles, rejects direct untrusted `structural_qualification` assertions, validates review chronology, and the compatibility wrapper delegates to the guarded entrypoint. Historical `available_at` now uses parsed UTC instants instead of lexicographic timestamp comparison.

Limits: caller-supplied review records are not authenticated; true structural-event classification and same physical event appearing as D1/W1 with distinct source-bar IDs require further audit. No production deployment or live trading.
