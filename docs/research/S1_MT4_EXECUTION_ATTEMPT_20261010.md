# S1 MT4 isolated execution attempt — 2026-10-10

- Extended the existing bounded research launcher to recognize the verified MT4 manifest + normalized directory; kept source/results non-overlap, non-root and Landlock policy unchanged.
- Landlock self-test now selects the original summary JSON or MT4 CSV manifest for its source write-denial probe.
- Added test preserving explicit prohibition of a canonical source under /tmp. CI #370 failed because an initial synthetic fixture used /tmp and expected acceptance; corrected fixture in commit 95fcb2a682f8e5b5ad8e2f14db37a9dc9e43d200 without relaxing security. CI #372 was still in progress at last observation.
- Read-only source access is available through authorized `sudo docker exec ... python -c` commands. Tried a bounded one-off staging of exact PR #95 level modules into ephemeral in-container /tmp (no archive mutation), to run `candidate_levels()` against the ACHC.us D1 source. The invocation required stdin-enabled docker exec (`-i`) and returned **sudo: a password is required**. Separate sudo one-off script mode likewise denied. No sudo privilege/configuration extension was made.
- Therefore the complete seven-type D1/W1 classifier was NOT run on real ACHC.us at this step. No level counts, trading signals, trades or outcomes were generated; no synthetic output is represented as real.
- Next execution requires an already-authorized repo-checkout research job with source mounted read-only and bounded Landlock child, or administrator approval for an allowed one-off invocation. Do not alter SentinelX allowlist or require HP-OMEN.

Research only. Production, trading and canonical MT4 corpus unchanged.
