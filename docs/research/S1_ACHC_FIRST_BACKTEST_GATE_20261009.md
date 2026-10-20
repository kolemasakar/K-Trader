# S1 / ACHC.us backtest execution gate — 2026-10-09

Status: NOT EXECUTED. No performance claims allowed.

Authoritative S1 specification: `docs/research/GERCHIK_S1_REJECTION_APPROVED_2026-10-05.md` on `research/dual-market-historical-levels-v0-1`. Implementation must be based on this version rather than earlier S1 drafts.

Requested asset: #9 in verified K_AI MT4 manifest order, `ACHC.us` (US equity).

Verified manifest:
- D1 2175 bars; first 2018-02-06 00:00, last 2026-10-05 00:00.
- H1 2061 bars; first 2025-08-04 20:30, last 2026-10-06 21:30.
- M5 2198 bars; first 2026-08-26 16:45, last 2026-10-06 22:50.
- Dataset: `/data/kif_research/external/kai_mt4_20261009` (read-only).
- Results: `/data/research` only.

Mandatory completion gates before a truthful strategy backtest:
1. Load/verify actual source series and temporal/calendar consistency (MT4 timezone/DST and US exchange sessions).
2. Implement approved D1/W1 level strength, strict two-left/two-right pivots and D1/H1/M5 approach direction without future information.
3. Implement S1 BPU1/BPU2 exact contact, limit activation at BPU2 minus 30 seconds, compression/unblocking, ATR5 v2, K activity, remaining range, stop and order cancellation rules.
4. Price US-equity stock's technical SL constraints, exact MT4 Point/tick size/contract specifications; do not invent parameters.
5. Two independent OHLC/OLHC intrabar paths with event ordering, entry/SL/TP protection, censored open positions.
6. Distinguish gross price-only result from uncomputable net result if spread/commission/slippage metadata absent.
7. Discovery/Validation chronological partition: avoid treating the calibration dataset as independent final holdout.
8. Tests for fail-closed incomplete data and deterministic reruns; CI passing isolated adapter tests is not strategy acceptance.
9. Never enable trading or execution interfaces.

Current staged adapter: PR #95, passing its earlier CI #322. It is not yet a complete S1 simulation engine. No S1 trades/outcomes are produced by this document.
