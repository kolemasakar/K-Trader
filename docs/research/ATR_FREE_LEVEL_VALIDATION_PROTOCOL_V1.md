# ATR-free structural level validation — next stage

Research-only protocol, not strategy backtesting or production execution.

New runner: `scripts/research/atr_free_level_validation_v1.py`; tests: `tests/test_atr_free_level_validation_v1.py`.

Data: K-Trader's own authorized historical research datasets only during model development. The previously obtained external archive is reserved as a holdout until the model and internal testing protocol are frozen. Run D1 and W1 for level discovery. Do not use H4/H1/M30/M15 to discover independent levels or test cross-timeframe level confluence during the initial strategy phase. A strict 3-left/3-right pivot becomes known only after the rightmost confirming candle **closes**. Preserve SHA256 per file. Anomaly tag = pivot candle high-low > 2x median of **prior** 20 ranges. Do not exclude anomalous candles. No ATR anywhere in level generation or evaluation.

Protocol: separate chronological early (60%) and late (40%) windows, dropping pivots whose entire forward observation would cross the split. Fixed 30-bar future observation, +/-0.3% price return band, >=1% favorable move and <1% adverse extreme over 3 bars after first return. Compare with seeded random price inside the **prior** 20-bar price range at identical pivot confirmation times; this baseline does not preserve price density and must not be treated as final. No claims about actual ordered intrabar reactions or executable trades. No parameter selection by looking at late-period results.

Usage (only in approved research environment with accessible historical archive):
```sh
python -m pytest tests/test_atr_free_level_validation_v1.py -q
python scripts/research/atr_free_level_validation_v1.py \
 --root <K_TRADER_INTERNAL_DATA_ROOT> \
 --symbols <INTERNAL_AVAILABLE_SYMBOLS> \
 --timeframes 1d 1w \
 --output <INTERNAL_RESEARCH_OUTPUT>/results.json
```

**Current execution status:** implementation and synthetic tests committed; neither host tests nor full D1/W1 historical run has been verified. Remote host access was blocked by tool safety; do not claim new results. Earlier D1 seven-symbol diagnostic remains the only completed ATR-free descriptive test.

**Next gates:** independently run and inspect output, assess D1/W1 confluence as-of timestamp; use H4/H1 only for approach/reaction context and M15/M30 only for intraday entry confirmation, test wick/body/impulse-origin structural clustering, evaluate duplicate events and uncertainty; separately verify EQUITIES+FOREX source data. Do not reuse legacy ATR-cluster score as validation.

## User-approved initial trading strategy correction (2026-09-28)
Initial trading horizon is **intraday**, but trades are considered **only near D1 or more significant W1 levels**. Lower timeframes are not independent sources of levels and must not be used to validate cross-timeframe level matches. H4/H1 may describe approach and reaction; M15/M30 may confirm timing of entry. Level discovery and robustness validation remain D1/W1 only. ATR is a separate prospective energy estimator after a setup exists, never a level-building input. The research runner defaults to 1d/1w. The pivot builder now rejects lower-TF level sources, records confirmation at the rightmost confirming candle close, and has no ATR gate.

## Internal-first implementation checkpoint
- `scripts/research/historical_level_builder.py`: only D1/W1, three bars left/right, confirmation at rightmost candle **close**, no ATR. Legacy output schema changed to v2 and old `confirmed_open_ms` removed; downstream consumers must explicitly migrate.
- `scripts/research/structural_level_clusters_v1.py`: exploratory as-of grouping of **confirmed** D1/W1 pivots by support/resistance separately. Fixed relative band 0.3% is a hypothesis only; complete-link price span prevents transitive chaining. Clusters are not strength ratings or executable trade levels. A singleton has no empirically calibrated zone width.
- Synthetic regression tests added/updated, but **not yet executed in the actual research runtime**. Do not infer PASS from committed tests.
- No source from the reserved external archive should be used for training, tuning, debugging on actual market samples, or intermediate validation before model freeze. The previous historical descriptive report is pre-existing exploratory information and must not be treated as an independent future holdout result.
