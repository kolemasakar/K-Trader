# Historical candidate direct-call bypass closure — 2026-09-28

Research branch: `research/dual-market-historical-levels-v0-1`.

Changes: `historical_candidates()` now requires complete `event/source_bar/review` bundles and runs `verify_reviewed_extremum()` itself before any aggregation. Direct submission of an arbitrary `structural_qualification` assertion is rejected. The `reviewed_historical_candidates()` compatibility wrapper delegates to this guarded public entrypoint. Tests have been rewritten for full evidence bundles and direct-call forgery regression.

Scope: **source-code bypass closure only**. Review records are still caller-provided and not cryptographically authenticated. The structural review process and meaningful swing/BOS definitions require independent specification and labelled validation. This change does not implement automatic level confirmation or authorize live trading. No production/HP-OMEN changes.

Verification status: code and regression tests committed; the updated test suite has not yet been executed against these exact new GitHub commits. Earlier 14/14 tests apply to the previous wrapper-based version only and must not be cited as verification of this closure.
