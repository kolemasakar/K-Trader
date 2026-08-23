# Phase 1 Checkpoint

Status: IMPLEMENTATION COMPLETE / LIVE VPS ACCEPTANCE PENDING.
Date: 2026-08-23.

## Implemented

- Exchange-agnostic `MarketDataProvider` abstract contract.
- Provider capability model with explicit unsupported fields.
- Canonical `NormalizedInstrument`, `NormalizedTicker`, `NormalizedCandle` models.
- Native `provider_symbol` separated from canonical symbol so OKX-style names do not leak into engine logic.
- Binance USD-M public REST adapter.
- Bybit Linear public REST adapter with pagination.
- Historical canonical intervals: 5m, 15m, 1h, 4h, 1d.
- Public instrument discovery, tickers, bid/ask inputs and klines.
- Configurable price filter / all-price mode.
- Deterministic quote-turnover liquidity ranking with spread penalty when confirmed bid/ask exists.
- Priority-provider fallback that builds a new coherent snapshot and never merges provider series.
- Offline provider contract, pagination, failover and universe tests.
- Operator public-provider smoke script for VPS acceptance.

## Verified locally

`PYTHONPATH=src pytest -q`

Result: `7 passed`.

`python -m compileall -q src scripts tests`

Result: PASS.

## Remaining live acceptance

The current execution environment cannot perform direct outbound exchange API smoke calls. Do not treat mock tests as proof of regional connectivity.

On the target VPS run:

`PYTHONPATH=src python scripts/provider_smoke.py --providers binance_usdm bybit_linear`

Acceptance requires:

- at least one configured provider responds through public market-data REST;
- candidate universe is returned without credentials;
- fallback is observable when primary is unavailable;
- no cross-provider series mixing occurs;
- actual VPS region complies with provider access rules.
