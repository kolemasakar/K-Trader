# K-Trader unified strong D1/W1 levels (research only)

Owner decision: use the **existing S1-approved** automatic algorithm, unchanged, for every strategy S1/S2A/S2B/S3/S4/S5A/S5B. No second level algorithm and no manual independent level labels.

Recovered from Oracle isolated working copy:
- /tmp/ktrader-bar-only-6ev4_jqg/src/ktrader/automatic_levels.py
- SHA256 8153568884ec6d15780b9c239b0141a01bcf60f46280d105019a6488fec3aca0
- matching Gerchik detector from the same snapshot: scripts/research/gerchik_seven_types_v0_1.py
- SHA256 d8bbfd4fcc43b0f4c969c583cb022aef85710b164bfbada8f07a5aec3f50b960

The S1 function s1_level_book is the sole D1/W1 source in scripts/run_approved_backtest.py. s1_level_active applies causal per-bar availability and invalidation. Strategies differ only in their own signal/entry/exit rules.

Broker execution is prohibited in K-Trader. Explicit --price-quantum is a simulation assumption, not evidence of broker tick/Point. OHLC price/R results cannot be presented as actual fills or net P&L.

Verification status: source recovered and published; regression parity, full S1 and S2A/S2B real-bar replays and GitHub CI are NOT YET VERIFIED. Do not merge the draft PR until tests pass. The original S1 snapshot's outputs must be compared before declaring parity.
