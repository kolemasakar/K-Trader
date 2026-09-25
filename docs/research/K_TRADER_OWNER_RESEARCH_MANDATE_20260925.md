# Owner-approved K-Trader research mandate — 2026-09-25

Status: OWNER APPROVED. This supersedes conflicting statements of K-Trader's purpose and research priority in older documents; historical checkpoints remain immutable.

## Role boundary
K-Trader is a research and analytical system. It discovers, tests, validates and issues actionable trade scenarios; it DOES NOT place or manage orders. K_AI alone decides execution and integrates with MT4/MT5. K-Trader's read-only API and existing analytical components remain useful; old descriptions of K-Trader as a trading robot are obsolete.

## Order of work
1. Research and specify asset eligibility, including historical market cap (where applicable), actual liquidity and traded volume during the target trading session, spread and slippage versus ATR/expected move, funding and costs, exchange listing age, data completeness, level interaction noise, volatility, and market-regime coverage. Avoid look-ahead and current-universe survivorship bias. Market cap is informative but not a sufficient futures-liquidity filter.
2. Collect public research and document executable versions of simple strategies, primarily reactions at strong prior daily/weekly/monthly levels: rejection, breakout continuation, breakout and retest, one-bar false breakout, multi-bar false breakout. Test range/trend alternatives as controls. Do not label any strategy effective without cost-inclusive independent tests.
3. Run history-first backtests on at least one year where available; permit longer (e.g. 2–3 years) for weekly/monthly strategies. Separate intraday, multi-day/weekly and multi-week/monthly horizons. Levels must be computed from information available at the decision time, using closed candles. Record exchange timestamps, retrieval time, provenance, gaps, delistings, commissions, spread, slippage and funding. Use chronological development/validation/untouched out-of-sample partitions and walk-forward tests; report sample size, net expectancy, drawdown, sensitivity, stability by asset/regime, and uncertainty.
4. Expand a separate read-only ingestion adapter to K_AI market data (MT4/MT5) when authorized and independently accessible; do not use HP-OMEN directly or indirectly under the standing prohibition.
5. Only after successful historical results, validate frozen candidates on genuinely new market data: Crypto, CFD, Forex, Metals, Energy and Indices. Never reclassify retrospectively fetched data as first-seen.
6. Issue versioned, expiring scenarios with symbol/provider, direction, level provenance, timeframe, trigger and invalidation, proposed entry/SL/TP, cost assumptions, quality metrics and evidence links for K_AI. No order execution in K-Trader.

## Initial approved research cohort
BTCUSDT, ETHUSDT, SOLUSDT, XRPUSDT, BNBUSDT (Binance USD-M); first verify listing history, historic liquidity, data availability and operational budget. DOGEUSDT and ADAUSDT are reserve candidates, not approved for initial download. If a candidate fails eligibility, report and request owner approval before substitution.

## Data acquisition authorization and isolation
Owner approved beginning historic extraction for the initial cohort AFTER eligibility verification. Target initial study window 2025-09-25 through 2026-09-24 inclusive (UTC); older history allowed for longer strategies. Obtain 15m/30m/1h/4h/1d/1w or causally derive higher intervals from verified lower ones. 5m is optional for execution sensitivity only. Reuse already-held verified bundles without rewriting frozen datasets. New data go exclusively to an isolated history research directory and record actual retrieved_at_utc separately from requested_as_of_utc. Begin with bounded pilot, enforce exchange rate and disk limits, expand by stages; do not interrupt first-seen capture or monitoring.

## Safety and governance
Current legacy frozen v2.2 evidence and holdout stay unchanged. Current first-seen data-only collection is independent, not a prerequisite for research. No live trading, no deployment changes, no HP-OMEN direct/indirect, no new prospective families without separate authorization. GitHub Actions quota unavailable through 2026-10-01: use independent OCI exact-SHA validation and retain logs. Preserve existing production contracts until separately reviewed.
