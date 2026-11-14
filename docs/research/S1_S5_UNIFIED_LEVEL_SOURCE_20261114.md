# K-Trader unified strong D1/W1 levels (research only)

Owner decision: use the **existing S1-approved** automatic algorithm, unchanged, for every strategy S1/S2A/S2B/S3/S4/S5A/S5B. No second level algorithm and no manual independent level labels.

Recovered from Oracle isolated working copy:
- /tmp/ktrader-bar-only-6ev4_jqg/src/ktrader/automatic_levels.py
- SHA256 8153568884ec6d15780b9c239b0141a01bcf60f46280d105019a6488fec3aca0
- matching Gerchik detector from the same snapshot: scripts/research/gerchik_seven_types_v0_1.py
- SHA256 d8bbfd4fcc43b0f4c969c583cb022aef85710b164bfbada8f07a5aec3f50b960

The S1 function s1_level_book is the sole D1/W1 source in scripts/run_approved_backtest.py. s1_level_active applies causal per-bar availability and invalidation. Strategies differ only in their own signal/entry/exit rules.

Broker execution is prohibited in K-Trader. Explicit --price-quantum is a simulation assumption, not evidence of broker tick/Point. OHLC price/R results cannot be presented as actual fills or net P&L.

Verification status: source recovered and published. The owner explicitly ruled that S1 strategy-result parity testing is NOT REQUIRED for this level-only integration; S1 strategy rules are unchanged by design. This is a waiver, not a test PASS. Shared wiring AST parse and Oracle S1 module import passed. End-to-end S2A/S2B real-bar runs and GitHub CI are NOT YET VERIFIED. Keep the draft PR unmerged until applicable integration tests and S2 evidence are complete.

## Integration continuation, 2026-11-14

- Shared runner fixed to access automatic-level metadata as dictionaries, not object attributes (commit 19eac35).
- Silver/gold strategy classes are mapped to the original S1 `metals` selector convention, without editing the recovered S1 algorithm (commit c22f393).
- Isolated Oracle staging directory: `/tmp/ktrader-s2-shared-20261114`; original S1 snapshot is preserved.
- S2A real-bar XAGUSD replay started with `--asset-class silver --price-quantum 0.01` on read-only historical corpus. This quantum is an explicit simulation assumption only.
- First run exposed unsupported `metals` in strategy luft() and failed; corrected classification, second run started. At checkpoint the process remained running and no backtest.json had been produced. Therefore there is NO verified S2A outcome, no S2B outcome and no S2 approval yet.
- Per owner decision, do not run S1 strategy-result parity checks. Continue S2A/S2B and verify actual outputs before promotion.
