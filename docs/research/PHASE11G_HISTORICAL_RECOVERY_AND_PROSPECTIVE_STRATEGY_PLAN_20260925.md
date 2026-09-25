# K-Trader research priority: historical reconstruction → independent validation → prospective shadow evaluation

**Owner priority confirmed 2026-09-25.** Historical market-data recovery is the primary research feed for developing and testing strategies. Independently recorded current data validates whether these historical strategies continue to behave as expected under contemporary market conditions, before any separately authorized execution decision. **This is a work plan, not a claim of backtest profitability, a strategy approval or trading authorization.**

## Boundaries that cannot change

1. Independent OCI K-Trader server + Binance USD-M provider only. **HP-OMEN and all direct/indirect K_AI/MT4 dependencies remain prohibited**. Existing first-seen collector, monitor, original 54/100 accepted families, frozen harness, ledger and existing epoch artifacts must not be altered or stopped.
2. No GitHub Actions dependency before the owner-reported quota reset on **2026-10-01**. Perform explicit, logged, exact-SHA tests on the independent K-Trader server and preserve their result manifests. GitHub branches/PR/document commits may be used independently where permitted.
3. Historical provider observations retrieved **today** are retrospective research data. They cannot prove what the K-Trader runtime had actually seen at a past cutoff and cannot be substituted into immutable first-seen cutoffs or prospective family counting.
4. Preserve existing captured M15 records even when the same exchange candle arrives later. Flag `HISTORICAL_RECOVERY` and `LATE_RELATIVE_TO_FIRST_SEEN` separately; record both `requested_as_of_utc` (market-data window boundary) and truthful `retrieved_at_utc` (actual server time). Do not set `retrieved_at_utc` equal to a historical cutoff.

## A. First research priority: isolated historical recovery

**Target initial lookback:** up to six months of available Binance USD-M history, subject to each contract's actual listing date and verified bar continuity. Use the existing validated K-Trader `BinanceUSDMProvider.get_historical_candles`, backward-paginating `collect_deep_provider_history`, dataset checksum machinery and historical robustness tests where compatible, rather than introducing an unreviewed ingestion stack.

**Important existing exporter issue to resolve before using it as evidence:** `research/strategy_benchmark_v1/historical_robustness_dataset_export_v1.py` currently passes the historical `--as-of` value as `fetched_at`. That stamp is a cutoff parameter, not proof of actual fetch time. The research recovery workflow needs a new truthful retrieval timestamp in its own manifest; do not silently modify old frozen historical artifacts.

**Phased capture and acceptance:**
- **H0 — read-only inventory:** current provider, exact symbol/interval support, existing historical bundles and snapshots, available server capacity, measured coverage gaps, incumbent history collector and exact pinned input SHA. Existing service health is independently `read_only`, `binance_usdm`. Initial 2026-09-25 host snapshot reported ~32 GiB free; recheck before any large download.
- **H1 — bounded pilot:** isolated directory `/data/research/phase11g/historical_recovery_v1/`; 5 representative actively available symbols × 5 intervals (`5m/15m/1h/4h/1d`), 7–30-day trial where supported plus enough daily context for the intended model. Small independent HTTP requests with rate limiting; no writes to runtime SQLite, first-seen epoch, or production dataset paths. Capture exact request/response coverage, actual `retrieved_at_utc`, provider symbol, UTC bar open/close, source type, content hashes, gaps/duplicates/unavailable segments and source pagination metadata. Pilot selection is **not** the final backtest universe.
- **H2 — staged expansion:** up to six calendar months for the historical strategy-development universe; prioritize the approved 19-rank independent cohort plus a broader liquid market where historical membership can be established. Extend depth for each timeframe in bounded batches. Do not fill gaps by fabricating candles or silently mixing providers.
- **H3 — quality gate:** verify interval-contiguous fully closed bars, exact price/volume identities, timestamp monotonicity, initial listing availability, duplicate consistency across paginated pages, archive checksums, funding/contract metadata where relevant, bounded disk use and source/ingestion-date provenance. Produce per-symbol/timeframe/day completeness tables with explicit `AVAILABLE`, `UNAVAILABLE`, `GAPPED` and `RECOVERED_RETROSPECTIVE` states.
- **H4 — cross-source checks:** compare overlapping source bars (exchange history against already archived independent K-Trader observations) without changing immutable first-seen records; report price mismatches and first-seen delivery delay distribution, especially `15m` and `5m` delays. A restored historical bar is not retroactively first-seen timely.

**Point-in-time selection caution:** the existing historical exporter resolves symbols from today's exchange instrument listing; applying that list retroactively to six months of backtests can introduce survivorship bias. For periods with saved, dated universe snapshots, use only the snapshot actually available at each cutoff. For earlier periods lacking captured snapshots, historical lagged-liquidity ranking is a separately labeled *reconstructed research universe*, not proof of the original live universe. Record delisted/listing coverage limitations and avoid future-data ranking.

## B. Strategy-development and verification stream

- Freeze a candidate strategy definition, training segment, parameter search budget, trading-timeframe/TTL profile and explicit transaction-cost model *before* evaluation.
- Use time-ordered training / validation / untouched out-of-sample periods, anchored rolling walk-forward checks, cross-symbol portability and stress costs (fees, funding, spread, slippage, execution delay). No lookahead to future closed candles or future liquid-universe rankings.
- Evaluate trade count, profit factor, expectancy after costs, win/loss profile, drawdown, exposure, risk of ruin proxies and sensitivity rather than selecting a strategy from gross profit alone. Detect parameter instability and multiple-testing bias.
- Historical findings are `RETROSPECTIVE_RESEARCH`, never prospective evidence. A result supported only by fitted windows is not sufficient to approve execution.
- Frozen baseline comparisons and performance differences must have independent provenance; no auto-admission of recovered research into the legacy 54/100 denominator.

## C. Independent current prospective stream

- Leave currently running first-seen data-only epoch and hourly/deep monitor operational in parallel. Continue documenting exact cutoff time, rank, first-seen ingestion timestamps and `READY/FAILED` causes without retroactive repair.
- After the historical strategy's independent out-of-sample checks, submit a separate documented **shadow/paper prospective gate** to compare its frozen signals against *new* first-seen data, including realistic execution-cost assumptions and late-data exclusion.
- If approved, run a time-limited, bounded paper trial. Record signal eligibility, slippage assumptions and all missed/expired trades without cherry-picking. Do not infer a guarantee of positive future returns from either historical backtesting or a small prospective sample.
- **Live trading requires a separate explicit owner decision** after results and operational risk checks; this planning document authorizes neither auto-trading nor Phase 12/holdout promotion.

## Work ordering and immediate next gate

`H0 read-only inventory → H1 5×5 bounded historical pilot → H2/H3 six-month expansion+quality → historical candidate walk-forward+OOS → separate first-seen shadow decision`, while current data-only first-seen collection and non-notifying monitoring run independently. H1 execution must check present OCI capacity and enforce a bounded request budget and isolated output. No reminder or automatic action schedule is introduced by this document.
