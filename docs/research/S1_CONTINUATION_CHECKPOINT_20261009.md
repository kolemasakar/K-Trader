# S1 implementation checkpoint — 2026-10-09 (continuation)

- Verified prior CI #337 PASS on its historical head; current source requires independent new CI.
- Source ACHC.us read-only: D1 2175, H1 2061, M5 2198.
- Added `src/ktrader/s1_setup.py` causal candidate checks: reviewed-level and strengthening evidence, aligned confirmed D1/H1/M5 trend, BPU1/partial BPU2, movement reserve, BPU2 activity, explicit session verification flag. No future BPU2 close used.
- Added `src/ktrader/s1_atr5.py` bounded daily range filter implementation **candidate**, with synthetic tests. It is not claimed equivalent to the full approved ATR5 v2 until historical parity/replacement-edge tests are completed. ATR not used to construct levels.
- `s1_intrabar.py` is only a standalone approximation kernel; full S1 signal/event lifecycle (order timing, cancellations, costs) still not integrated.
- Existing seven-type Gerchik detectors are research candidates, not independently approved level evidence. Missing per-symbol Point/tick-size and reviewed ACHC.us levels are explicit blockers for generating a genuine S1 order.
- Separate no-timezone algorithmic replay is owner-approved; first-session rule remains tagged as unevaluated, not invented PASS.
- No actual S1 trades have been produced. **A data-read preflight with 0 trades is not an S1 strategy backtest**. No returns or profitability assertions.
- No deployment, no live execution, no source writes.

Next gates: test latest CI; verify ATR reference against canonical owner algorithm; provide independently qualified ACHC D1/W1 formations; confirm actual broker price increment for orders or run structural signal-only audit without order sizing; complete two-scenario execution and run full chronological backtest.
