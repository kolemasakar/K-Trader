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
