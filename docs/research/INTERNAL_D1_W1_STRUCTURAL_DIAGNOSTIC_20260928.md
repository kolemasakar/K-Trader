# Internal D1/W1 structural diagnostic — 2026-09-28

Research only; **not a trade backtest, not an out-of-sample test**. Read-only run on K-Trader-owned `historical_expansion_v1_20260905T144500Z/bundles` inside the existing container through the authorized SentinelX one-off script. No AI_Trading_System/external holdout access, no live trading or production edits.

Algorithm in this execution: strict 3-left/3-right pivot on D1 and fully complete UTC Monday–Sunday W1, confirmation after right-hand bars; support and resistance clustered separately with complete price span <=0.3% of minimum price. Grouping is exploratory and not strength calibrated. Run returned code 0 and 19 results. This was an in-memory audit implementation of the same research concept; **do not represent it as executing the committed research runner or its tests**.

| Symbol | D1 pivots | W1 pivots | Zones | D1/W1 mixed |
|---|---:|---:|---:|---:|
| 1000PEPEUSDT | 104 | 11 | 96 | 11 |
| ADAUSDT | 95 | 12 | 91 | 12 |
| AKEUSDT | 67 | 9 | 64 | 8 |
| ARBUSDT | 91 | 11 | 84 | 11 |
| DOGEUSDT | 110 | 11 | 95 | 11 |
| DOTUSDT | 98 | 13 | 90 | 13 |
| ENAUSDT | 103 | 11 | 97 | 11 |
| ETHFIUSDT | 100 | 13 | 92 | 13 |
| IOSTUSDT | 96 | 13 | 91 | 13 |
| METUSDT | 65 | 7 | 60 | 7 |
| NEARUSDT | 103 | 15 | 90 | 13 |
| PUMPUSDT | 74 | 10 | 69 | 10 |
| RAYSOLUSDT | 97 | 11 | 86 | 11 |
| SUIUSDT | 101 | 11 | 95 | 11 |
| TRUMPUSDT | 95 | 14 | 85 | 14 |
| USELESSUSDT | 73 | 9 | 71 | 9 |
| VTHOUSDT | 102 | 12 | 93 | 12 |
| WLDUSDT | 101 | 13 | 91 | 13 |
| XRPUSDT | 99 | 13 | 79 | 13 |
| **TOTAL** | **1774** | **219** | **1619** | **216** |

Interpretation limits: near-coincident D1/W1 pivots may represent the same event rather than independent corroboration. Zone counts are sensitive to grouping bandwidth and sample duration. Current analysis counts all confirmed pivots using complete data; it does not construct time-varying as-of zone snapshots or measure post-formation retests, reactions, intraday entries, costs, or outcomes. The next gate is to run the committed modules' synthetic tests, compare parity with this audit, deduplicate same-event D1/W1 coincidences, and validate prospective as-of formation on own internal data before any reserved external holdout.

## Parity and tests (2026-09-28 continuation)
Fetched the actual three research Python modules from this branch and executed `internal_level_structure_diagnostics_v1.run` in a temporary directory inside the existing container against the 19 internal native D1 sources, read-only. Exit 0, 19/19 `EXPLORATORY_STRUCTURE_ONLY_NOT_BACKTEST`. Exact parity with earlier in-memory audit for all 19 symbols and all four reported metrics: 1,774 D1 pivots, 219 W1 pivots, 1,619 zones, 216 mixed D1/W1 zones.

Both host and container lack pytest. Without installing software, executed the **actual eight repository test functions** from `test_native_internal_d1_w1_v1.py` and `test_structural_level_clusters_v1.py` via an isolated Python harness supplying a minimal `pytest.raises` substitute and temporary path fixtures: 8/8 PASS. This is **not a full pytest suite run** and does not cover other repository tests. Next: same-event deduplication and causal as-of reaction validation before assessing trading performance. No external holdout or production modifications.
