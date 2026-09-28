# Dual-market historical levels — controlled research v0.1
Date 2026-09-28. **Not a strategy backtest** and no production deployment.

## Track A: CRYPTO
Confirmed on-server source: /data/research/phase11g/historical_recovery_v1/approved_seven_year_20260925/bundles/
Seven symbols BTCUSDT, ETHUSDT, SOLUSDT, XRPUSDT, BNBUSDT, ADAUSDT, DOGEUSDT.
2025-09-25 through 2026-09-24, TF 15m/30m/1h/4h/1d/1w; historical retrospective recovery, not first-seen OOS.
Research-only script: scripts/research/historical_level_builder.py. It emits per-symbol independently confirmed two-right-bar pivot prices, confirmation timestamps, TF structural weights, and exact file hashes. A pivot becomes available only after the two following completed bars; no price performance is calculated.

## Track B: EQUITIES + FOREX
Separate market profiles and outputs. Do not fabricate prices or re-use crypto candles. Historical equity/Forex OHLCV coverage was **not confirmed** in the K-Trader server's reviewed research bundle; verify the K_AI MT4 watchlist and existing authorized archive, symbol suffix, broker, session, timezone, adjusted corporate actions for equities, tick value/quote currency for Forex before running. Distinguish regular/extended stock sessions and weekend/holiday gaps; Forex spot tick volume is not consolidated exchange volume. Run only against verified local authorized historical data converted to the documented schema.

## Critical methodological gate
On-server btc_h1_zone_width_methodology_audit.json says accepted-only ATR baseline rejects 58.32% and 63.90% of bars in two BTC H1 yearly samples; 266 and 257 five-reject alerts. It is marked BLOCKED_FOR_PARAMETER_APPROVAL. Therefore this script **does not cluster pivots into ATR-based zones, score level reliability, or claim calibrated level widths**. Prior reference radii .05/.10/.15 ATR5 and legacy .25 are only candidates. Structural TF weights W1=5 D1=4 H4=3 H1=2 M30/M15=1 are organizational weights, not success probabilities.

## Execution and acceptance
For crypto, in an approved read-only research environment with the archive mounted:
```
python scripts/research/historical_level_builder.py --root /data/research/phase11g/historical_recovery_v1/approved_seven_year_20260925/bundles --market CRYPTO --symbols BTCUSDT ETHUSDT SOLUSDT XRPUSDT BNBUSDT ADAUSDT DOGEUSDT --output /data/research/phase11g/historical_levels_crypto_v0_1
```
Run separate EQUITIES and FOREX invocations only after confirming their datasets and converting their input format. The output location must be research-only; no production settings, risk gates, trade execution or historical hypothesis evaluation.

**Status:** source archive and blocking ATR audit confirmed; script and unit tests committed; full seven-symbol output on host **not yet executed** because remote arbitrary script execution was blocked. This is not a completed level-map result.
