# K_AI MT4 verified corpus: research-only adapter

Source (container): `/data/kif_research/external/kai_mt4_20261009`.

- Never modify the source or promote its rows to Binance dataset catalogue.
- This adapter requires an explicit `as_of` cutoff and emits only closed candles whose `close_time <= as_of`.
- Use provider identity `mt4` and broker symbol separately from canonical instrument names.
- Source timestamp timezone is not independently established. Verify MT4 server timezone and DST conversion before strategy P&L testing.
- The metadata CSV is trusted only after acceptance; the dataset's four control artifact hashes must be checked independently for production usage.
- Gap/calendar, spread, slippage, commission, stop order semantics, corporate actions and validation split controls remain separate mandatory gates.
- Derived artifacts belong under `/data/research`, never the frozen source directory.
- This module exposes no runtime trading/execution API and does not launch backtests.

## Owner-approved artificial wall-clock algorithmic test mode (2026-10-09)

The purpose of the first S1 run is **algorithm correctness**, not proof of live-session execution accuracy. MT4 header `BROKER_SERVER_WALL_CLOCK_OPAQUE` does not prevent chronological OHLC processing. Use `MT4ResearchCorpus(root, wall_clock_mode=True)`, and pass an `as_of` in the **same broker wall-clock coordinate system**, without claiming these timestamps are UTC. The internal timezone epoch representation in this mode is only a comparison device; do not convert it to exchange time or use it for absolute session schedules.

Retain causality, completed-bar checks, timestamp order, price geometry and two independent intrabar paths. Session-first-hour / exchange-calendar-dependent conditions must be explicitly tagged `NOT_EVALUATED_TIMEZONE_UNKNOWN` rather than silently treated as passing. Backtest outputs must identify `ALGORITHMIC_WALL_CLOCK`, unknown session alignment and uncertain real-world execution/P&L. Verified timezone mode remains available for later fidelity validation. This owner scope correction supersedes the earlier statement that missing broker timezone blocks **all** S1 backtesting.
