# Phase 11G — owner-approved history-first strategy research plan (2026-09-25)

Authority: [owner mandate](K_TRADER_OWNER_RESEARCH_MANDATE_20260925.md). Earlier six-month-first and prospective-evidence-first priorities are superseded where they conflict.

## R0 Asset screening
For each approved symbol, query exchange info, 12-month available kline coverage, monthly daily-volume and volatility distribution, funding, age and liquidity proxy. Evaluate spread/order-book depth where historically available; flag unavailable historical spread instead of inferring it. Check level-crossing noise: repeated wick-only crossings, closing-bar rejections and ATR-normalized follow-through. Establish separate thresholds for intraday versus weekly/monthly tests and validate their robustness, rather than treating provisional $100m daily turnover as a universal gate. Record selection as of historical dates to avoid survivorship bias.

## R1 Strategy catalogue
S1 prior D1/W1 level rejection; S2 breakout continuation; S3 breakout + retest; S4 one-bar false breakout; S5 multi-bar false breakout (2–5 closed bars with failed continuation); S6 trend/range controls. Pre-register exact level detection, minimum touch spacing, ATR-normalized level zones, causal triggers, SL/TP/expiry, fees and failure modes before testing. Collect primary studies and public descriptions, distinguish evidence from popular claims. All strategies are hypotheses, not approved performers.

## R2 History and tests
Initial five approved Binance USD-M symbols, one year ending 2026-09-24 UTC, optional 2–3 years for slower strategies. Intervals 15m/30m/1h/4h/1d/1w, optionally 5m for fill simulation. H0 inventory already found historical_robustness and historical_expansion datasets on independent OCI; hash verification and precise overlap/gaps pending. R2a: bounded isolated 5×5 pilot (15m/1h/4h/1d/1w) 7–30 days plus warmup and eligibility check. R2b: stage full-year download with checkpoints and provenance. R2c: reproducible cost-inclusive backtests, chronological walk-forward/OOS and stability checks. 30m can be aggregated from 15m; 1w from 1d only after calendar and boundary validation. Do not rewrite legacy frozen artifacts.

## R3 K_AI market-data interoperability
Define read-only normalized OHLCV/symbol metadata ingestion for authorized MT4/MT5 sources and provenance mapping, broker suffix/spread/trading-hours checks; separate server path, no HP-OMEN use under current exclusion. K_AI exclusively executes.

## R4 Forward validation and scenario API
After independent historical gates, separately authorize forward testing across Crypto/CFD/Forex/Metals/Energy/Indices. Output versioned expiring evidence-linked scenarios, no K-Trader order execution.

## Gates and status
R0 specification approved; five symbols approved for eligibility check and subsequent isolated history download if eligible. R1 catalogue hypotheses specified, external evidence review ongoing. H0 server existence inventory: 19-symbol robustness 386800544 bytes and 19-symbol expansion 84503013 bytes; full checksums/coverage still pending. R2a/R2b NOT YET COMPLETE. Keep current first-seen epoch isolated. No profitability conclusion.
