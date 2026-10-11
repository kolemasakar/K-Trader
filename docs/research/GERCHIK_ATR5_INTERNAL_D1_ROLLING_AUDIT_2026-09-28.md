# Filtered ATR(5): internal D1 historical rolling audit — 2026-09-28

Status: independent read-only server audit of the v1 reference policy; NOT an execution of the checked-in Python module or pytest. No production or live-trading changes.

Source: running healthy k-trader-ktrader-1 container on independent K-Trader production server, existing /data/research/phase11g/binance_usdm/{SUIUSDT,XRPUSDT}/20260905T144500Z_160000Z/bundle/1d.jsonl. Both files have manifest candle_count=300 and 300 closed D1 records, spanning 2025-11-09 through 2026-09-04 UTC. Manifest cutoff and closed=true enforced; newest-to-oldest as-of rolling cutoffs. No HP-OMEN, K_AI, MT4 or external data.

Reference policy reproduced in an isolated read-only inline Python audit: for each candidate, mean range of candidate and four immediately older completed D1 candles; reject range >= 2 x reference or <= reference / 3; bootstrap shifts backward until starting bar normal; scan older candidates to accept five; cap 250 D1 bars; final mean of accepted five.

Results (each asset 296 attempted as-of cutoffs with >=5 D1 candles):
| Metric | SUIUSDT | XRPUSDT |
|---|---:|---:|
| Closed D1 records | 300 | 300 |
| Successful rolling ATR5 calculations | 292 | 292 |
| Insufficient older history | 4 | 4 |
| Successful cutoffs with at least one rejected bar | 54 | 59 |
| Rejected LARGE bars (across all successful cutoffs) | 54 | 45 |
| Rejected SMALL bars (across all successful cutoffs) | 15 | 25 |
| Latest as-of 2026-09-04 ATR5 | 0.04226 | 0.07802 |

The four insufficient-history cutoffs per asset are expected near the oldest archive boundary: a candidate requires four older bars for its reference, plus five accepted bars. They do not indicate missing dataset files. Rejection counts may exceed cutoffs with rejection because a cutoff can reject multiple bars.

First rejection example for both assets: as-of 2026-09-02 UTC; SMALL rejected; ATR5 SUIUSDT 0.04868 and XRPUSDT 0.0753.

**Access root cause:** SentinelX file-listing /opt/k-trader/data reported empty or rejected parent /opt/k-trader due to configured file paths and differing host/container inspection; allowed `sudo docker exec` revealed /data/research/phase11g/catalogue.json and actual mounted files. No access policy change needed. `sentinel_script_run` could not run sudo (password/TTY required), so the audit ran through allowlisted `sentinel_exec` + `sudo docker exec` with encoded Python inline. No secrets read.

**Limits:** This validates an independent implementation of the proposed formula, not the GitHub module import. The evolving reference is still a proposal, not a book-authoritative formula. Follow-up: run exact checked-in module and pytest against native D1 fixtures, add boundary/causality tests, extend to seven-level detectors separately.
