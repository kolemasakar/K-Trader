# 2026-10-09 S1 ACHC.us integration checkpoint

**Status: partial implementation, S1 backtest not completed. No performance statistics.**

Added `src/ktrader/s1_setup.py` and `tests/test_s1_setup.py` (causal two-left/two-right swing trend, 20-bar activity primitive and explicit fail-closed eligibility). These are NOT the complete S1 strategy. Approved D1/W1 Gerchik level recognition/review, ATR5 v2 full replacement loop, compression/BPU checks, session-exception policy, 30-second signal assembly, broker Point/tick and proper stop risk remain to integrate.

Already staged: read-only MT4 JSONL adapter with explicit synthetic broker wall-clock mode; isolated A/B path kernel; no execution interfaces. Prior CI #335 succeeded before this checkpoint's added files; new tests require fresh CI.

Real verified source read executed on k-trader-prod-vnic inside approved container route. ACHC.us counts: D1 2175, H1 2061, M5 2198. Live research preflight printed `BLOCKED_NO_REVIEWED_LEVELS_AND_BROKER_PRICE_METADATA` and `TRADES_GENERATED 0`. It was **not** a trade-generating S1 simulation; zero must not be represented as a market finding.

Next admission: implement/import the owner-approved level policy with independently verified evidence, causal ATR5 v2 and S1 BPU entry generator; run fixed A/B paths with reproducibility and chronological reporting. Keep frozen corpus immutable, net P&L unknown without costs, no trading or production deploy.
