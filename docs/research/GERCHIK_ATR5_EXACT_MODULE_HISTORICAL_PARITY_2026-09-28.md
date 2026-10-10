# Exact GitHub module versus independent D1 historical calculation — 2026-09-28

Status: PASS for exact-source historical parity. Research only. No production deployment or live-trading changes.

Method: fetched scripts/research/gerchik_filtered_atr5_v1.py over HTTPS from the GitHub research branch inside the existing healthy independent K-Trader container, calculated the Git blob SHA from the downloaded bytes and asserted it equals the GitHub fetch_file blob SHA `0d2f14d75b6f03b6ebe9cd7c543b220bad8f6f73`. Compiled/executed the exact fetched module in memory (no host or container file writes). Used internal read-only Phase 11G Binance USD-M SUIUSDT and XRPUSDT 300-candle D1 bundle archives with closed=true and manifest as-of cutoff. For every as-of date with >=5 bars, ran the actual module and a separately written rolling reference implementation, asserting equal ATR within 1e-12, equal rejection counts, and identical ordered rejection reasons. InsufficientHistory was recorded separately.

| Metric | SUIUSDT | XRPUSDT |
|---|---:|---:|
| Closed D1 bars | 300 | 300 |
| Exact module / independent reference matching cutoffs | 292 | 292 |
| Mismatches | 0 | 0 |
| Insufficient older history | 4 | 4 |
| Cutoffs with rejected bar(s) | 54 | 59 |
| Rejected SMALL | 15 | 25 |
| Rejected LARGE | 54 | 45 |

TOTAL 584/584 exact-source historical calculations match. GitHub module blob SHA verified before running. The four insufficient-history cases per asset are expected near the oldest archive boundary. This audit does NOT establish that the experimental reference policy is uniquely prescribed by Gerchik or that a trading strategy is profitable. Repository pytest execution remains separate. No HP-OMEN, K_AI or MT4 historical data used.
