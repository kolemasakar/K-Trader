# Strong Levels: first historical descriptive test — 2026-09-28

**Scope:** read-only in-memory evaluation of the existing retrospective K-Trader crypto daily archive (BTCUSDT, ETHUSDT, SOLUSDT, XRPUSDT, BNBUSDT, ADAUSDT, DOGEUSDT), 365 daily candles per symbol, 2025-09-25 to 2026-09-24. No files on production host changed. No ATR was used for level detection, grouping or evaluation. No strategy backtest or trading decisions.

## Fixed exploratory definitions (not calibrated)
- Confirmed D1 swing high/low: 3 prior and 3 subsequent daily bars must be strictly lower/higher than the pivot. Earliest known only after all three right-side candles completed.
- 'Anomalous': pivot candle high-low > 2x median of 20 **prior** daily high-low ranges. This is only an observational tag, never a rejection rule.
- 'Repeat': at least one **earlier confirmed** same-side pivot within 0.3% of price, with no overlap in pivot confirmation windows. Otherwise 'single'. This 0.3% is a preselected price-percentage research tolerance, **not ATR** and not a validated zone width.
- Eligible observations: enough future data for a complete 30-day observation window after confirmation. Search first price overlap with +/-0.3% of the pivot during that window.
- Conservative 'reaction' proxy: following the first touch, over the first up-to-three daily bars, the favorable extreme moves >=1% from the pivot and the adverse extreme never moves >=1%. Because OHLC lacks intrabar sequence, this is **not an entry signal, actual execution, or demonstrated ordered bounce**. Same-day good+bad is rejected. Unreached levels count as not touched, not as failed reactions.
- Repeated pivots can be correlated; no confidence intervals or significance claims. These definitions were selected as an initial diagnostic, not optimized.

## Results
| Group | Eligible level observations | First touch within 30 days | Conservative reaction proxy |
|---|---:|---:|---:|
| Single, ordinary candle | 339 | 239 | 48 |
| Single, anomalous candle | 50 | 31 | 4 |
| Repeat, ordinary candle | 69 | 42 | 8 |
| Repeat, anomalous candle | 5 | 3 | 0 |
| **Total** | **463** | **315** | **60** |

Per-symbol D1 confirmed pivot counts **before** complete-future-window exclusion: BTC 73, ETH 71, SOL 79, XRP 70, BNB 73, ADA 66, DOGE 74.

**Interpretation limits:** The proxy measures one narrow form of reaction only. It does not establish that ordinary pivots outperform anomalous pivots; anomaly and repeat samples are smaller, many price reactions differ from the arbitrary 1%/three-bar proxy, and the 30-day observation window and fixed price tolerance are not independently validated. A level can be meaningful without a return to it within 30 days. No out-of-sample validation or random/baseline level comparison has been performed. Results must not be presented as success rates of trades or probabilities of profitable entries.

## Existing legacy comparison and methodological correction
The earlier `strong_levels_v1/strength_study_summary.json` on the host is explicitly exploratory **in-sample without OOS**, uses 0.25 x D1 ATR14 for clustering and a composite score; its conclusions must not be transferred to the corrected **ATR-free** Strong Levels Engine. It mixes level strength with S1/S4 trade outcomes. Preserve as a legacy comparator only.

## Next controlled research gates
1. Run independent D1/H4/H1 pivot extraction, preserve exact source hashes, session boundaries and as-of confirmation times.
2. Pre-register alternative structural (non-ATR) grouping definitions: exact wick-price, body-edge, repeated-reaction overlap; report sensitivity without selecting by hindsight.
3. Analyze anomalous candle subtypes (long wick, large body, impulse origin) and actual subsequent reactions; do not discard anomaly candles.
4. Create non-overlapping time splits, deduplicate correlated level events, report uncertainty and compare against matched randomly selected non-level price locations.
5. Once independently reliable level maps exist, separately evaluate **entry signals near levels**, then energy estimation through the independent ATR Energy Engine. Do not use trading P&L to retroactively define level quality without separate authorization.

**Status:** initial D1 diagnostic completed; robust/reliable strong-level algorithm **not validated**. Equities and FX history unavailable in this confirmed crypto archive; their track remains data-source verification pending.
