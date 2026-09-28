# ATR-free structural level validation — next stage

Research-only protocol, not strategy backtesting or production execution.

New runner: `scripts/research/atr_free_level_validation_v1.py`; tests: `tests/test_atr_free_level_validation_v1.py`.

Data: the confirmed 7-symbol historical crypto archive. Run D1/H4/H1 independently. A strict 3-left/3-right pivot becomes known only after the rightmost confirming candle **closes**. Preserve SHA256 per file. Anomaly tag = pivot candle high-low > 2x median of **prior** 20 ranges. Do not exclude anomalous candles. No ATR anywhere in level generation or evaluation.

Protocol: separate chronological early (60%) and late (40%) windows, dropping pivots whose entire forward observation would cross the split. Fixed 30-bar future observation, +/-0.3% price return band, >=1% favorable move and <1% adverse extreme over 3 bars after first return. Compare with seeded random price inside the **prior** 20-bar price range at identical pivot confirmation times; this baseline does not preserve price density and must not be treated as final. No claims about actual ordered intrabar reactions or executable trades. No parameter selection by looking at late-period results.

Usage (only in approved research environment with accessible historical archive):
```sh
python -m pytest tests/test_atr_free_level_validation_v1.py -q
python scripts/research/atr_free_level_validation_v1.py \
 --root /data/research/phase11g/historical_recovery_v1/approved_seven_year_20260925/bundles \
 --symbols BTCUSDT ETHUSDT SOLUSDT XRPUSDT BNBUSDT ADAUSDT DOGEUSDT \
 --timeframes 1d 4h 1h \
 --output /data/research/phase11g/atr_free_level_validation_v1/results.json
```

**Current execution status:** implementation and synthetic tests committed; neither host tests nor full D1/H4/H1 historical run has been verified. Remote host access was blocked by tool safety; do not claim new results. Earlier D1 seven-symbol diagnostic remains the only completed ATR-free descriptive test.

**Next gates:** independently run and inspect output, assess cross-TF confluence as-of timestamp, test wick/body/impulse-origin structural clustering, evaluate duplicate events and uncertainty; separately verify EQUITIES+FOREX source data. Do not reuse legacy ATR-cluster score as validation.
