# Phase 11C Checkpoint - Deep History / MTF Replay Bundles

Date: 2026-08-23

Status: VERIFIED.

## Implemented

- optional provider historical-page contract with explicit UTC end cursor;
- Binance USD-M backward kline pagination through `endTime`;
- Bybit Linear backward kline pagination through `end`;
- exact-depth backward collector with page deduplication and cursor-progress checks;
- fail-closed handling for missing pagination support, insufficient depth, gaps and provider identity mismatch;
- deterministic five-timeframe bundle schema `ktrader.mtf_bundle.v1`;
- canonical `1d/4h/1h/15m/5m` bundle identity under one provider/symbol;
- shared UTC `as_of` replay cutoff;
- per-timeframe history SHA-256 digests plus bundle-level SHA-256;
- MTF bundle write/load integrity verification;
- no-lookahead dataset slicing at an explicit replay cutoff;
- public-data deep single-timeframe and MTF export utilities.

## Guardrails

- No OHLCV series mixing across providers.
- No silent provider fallback inside historical archives.
- Deep collection succeeds only when the requested exact closed-bar depth is available.
- Every final history series must be chronological, contiguous and closed.
- Every MTF dataset must belong to the same provider, canonical symbol and provider symbol.
- A bundle rejects any candle closing after its `as_of` cutoff.
- `slice_datasets_asof()` removes later candles before replay, preventing future look-ahead.
- Trading Engine setup rules, Setup Score, RR, ATR-used and `estimated_probability` are unchanged.

## Operator utilities

Single timeframe, automatically deep when requested bars exceed provider page capacity:

```sh
python scripts/export_provider_history.py \
  --provider bybit_linear \
  --symbol SUIUSDT \
  --interval 5m \
  --bars 5000 \
  --output data/history/bybit_linear/SUIUSDT/5m.jsonl
```

Five-timeframe bundle:

```sh
python scripts/export_mtf_history.py \
  --provider bybit_linear \
  --symbol SUIUSDT \
  --bars-1d 500 \
  --bars-4h 1000 \
  --bars-1h 1500 \
  --bars-15m 3000 \
  --bars-5m 5000 \
  --output data/replay/bybit_linear/SUIUSDT/sample
```

These utilities use public exchange market-data endpoints only.

## Verification evidence

PR #6 (`Phase 11C deep history and MTF replay bundles`) passed GitHub Actions CI run:

`32652044967`

Integrated result:

- Python compile: PASS;
- shell syntax validation: PASS;
- repository-wide pytest: **134 passed, 1 dependency deprecation warning**;
- linux/amd64 Docker build/runtime import: PASS;
- linux/arm64 QEMU/Buildx build: PASS;
- ARM64 architecture assertion: PASS;
- ARM64 production ASGI import: PASS;
- packaged target-host acceptance utility on both architectures: PASS.

PR #6 was squash-merged to `main` as:

`0b7fd93246d4d5e6213ab0bf4ab63ee52b5fc007`

## Provider-recorded regression data status

The repository now contains the deterministic capture, validation and bundle contracts required to create provider-recorded regression datasets. CI deliberately uses deterministic mocked provider pages so normal PR verification does not depend on exchange availability or geographic API access.

Actual long provider-recorded bundles are operator-generated artifacts and should not be silently substituted with synthetic candles. The first canonical real-data capture can be performed from an approved network/runtime using `scripts/export_mtf_history.py`; the resulting bundle digest makes that capture reproducible and auditable.

## Remaining hardening

- capture and catalogue canonical real-provider replay bundles;
- bulk chronological replay over those bundles through the full analysis engine;
- connect historical TradingDecision generation to Phase 11B outcome persistence;
- define approved outcome horizons/study cohorts;
- metrics/backup/recovery/runtime-failure hardening;
- statistical calibration remains a separate later approval gate.
