# Dual-market historical levels — controlled research v0.1
Date 2026-09-28. **Not a strategy backtest** and no production deployment.

## Track A: CRYPTO
Confirmed on-server source: /data/research/phase11g/historical_recovery_v1/approved_seven_year_20260925/bundles/
Seven symbols BTCUSDT, ETHUSDT, SOLUSDT, XRPUSDT, BNBUSDT, ADAUSDT, DOGEUSDT.
2025-09-25 through 2026-09-24, TF 15m/30m/1h/4h/1d/1w; historical retrospective recovery, not first-seen OOS.
Research-only script: scripts/research/historical_level_builder.py. It emits per-symbol independently confirmed two-right-bar pivot prices, confirmation timestamps, TF structural weights, and exact file hashes. A pivot becomes available only after the two following completed bars; no price performance is calculated.

## Track B: EQUITIES + FOREX
Separate market profiles and outputs. Do not fabricate prices or re-use crypto candles. Historical equity/Forex OHLCV coverage was **not confirmed** in the K-Trader server's reviewed research bundle; verify the K_AI MT4 watchlist and existing authorized archive, symbol suffix, broker, session, timezone, adjusted corporate actions for equities, tick value/quote currency for Forex before running. Distinguish regular/extended stock sessions and weekend/holiday gaps; Forex spot tick volume is not consolidated exchange volume. Run only against verified local authorized historical data converted to the documented schema.

## Corrected methodology: ATR is prohibited in level construction
User correction 2026-09-28: anomalously large candles can establish strong levels. Preserve all raw OHLC candles, including outliers. Level candidates derive from market structure, extremal prices, repeated price reactions, consolidation, and verified volume when available. **No ATR for level detection, candidate exclusion, zone merging, zone width or level strength.** The present script outputs confirmed pivots only; future structural clustering must use price-action evidence, not ATR.

ATR research, including the earlier unstable accepted-only baseline and .05/.10/.15/.25 ATR zone-width experiments, is **removed from this level-engine decision path**. Those experiments are historical research artifacts, not current level-engine requirements. Maintain a separate ATR Energy Engine used only after a trade setup exists, to compare realized movement with historical typical range. ATR never guarantees remaining movement or direction.

## Execution and acceptance
For crypto, in an approved read-only research environment with the archive mounted:
```
python scripts/research/historical_level_builder.py --root /data/research/phase11g/historical_recovery_v1/approved_seven_year_20260925/bundles --market CRYPTO --symbols BTCUSDT ETHUSDT SOLUSDT XRPUSDT BNBUSDT ADAUSDT DOGEUSDT --output /data/research/phase11g/historical_levels_crypto_v0_1
```
Run separate EQUITIES and FOREX invocations only after confirming their datasets and converting their input format. The output location must be research-only; no production settings, risk gates, trade execution or historical hypothesis evaluation.

**Status:** source archive and blocking ATR audit confirmed; script and unit tests committed; full seven-symbol output on host **not yet executed** because remote arbitrary script execution was blocked. This is not a completed level-map result.
