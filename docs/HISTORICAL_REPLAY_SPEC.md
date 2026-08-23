# Historical Replay / Signal Outcome Spec v1.0

## Purpose

Phase 11B adds a reproducible foundation for provider-recorded historical replay and later statistical calibration. It does not convert Setup Score into probability and does not claim win-rate evidence by itself.

## Provider history contract

A history dataset is a coherent series from exactly one provider, canonical symbol and timeframe.

Rules:

- only confirmed closed candles;
- chronological and contiguous;
- UTC timestamps;
- no provider mixing or provider fallback inside a dataset;
- Decimal market values are serialized as strings;
- source kind is `provider`;
- a SHA-256 digest covers canonical candle content;
- requested bar count and actual time range are recorded separately.

Schema version: `ktrader.history.v1`.

The JSONL file starts with one manifest record followed by candle records.

## Historical collection

`collect_provider_history()` uses the existing `MarketDataProvider.get_candles()` contract and captures the latest coherent closed-candle page from one provider.

Phase 11B intentionally keeps collection inside the already verified provider interface. The maximum export depth is therefore one provider-native page (`1500` for Binance USD-M and `1000` for Bybit Linear in the current adapters). Deep multi-page archival pagination is deferred; the versioned dataset contract does not need to change when it is added.

The collector fails closed on gaps, open-only results, provider identity mismatch, unsupported intervals or requests above the provider page capacity.

Operator export:

```sh
python scripts/export_provider_history.py \
  --provider bybit_linear \
  --symbol SUIUSDT \
  --interval 5m \
  --bars 1000 \
  --output data/history/bybit_linear/SUIUSDT/5m-latest.jsonl
```

This utility uses public market-data endpoints only.

## Signal outcome contract

Outcome evaluation is separate from Trading Engine setup generation. It consumes a previously emitted `TradingDecision` and later confirmed candles from the same provider/symbol.

Eligible decisions require:

- side `LONG` or `SHORT`;
- confirmed Entry, Stop and Target geometry.

`NO_TRADE` and missing-geometry decisions are `NOT_ELIGIBLE` and never enter binary calibration samples.

Canonical outcome states:

- `PENDING_ENTRY`;
- `OPEN`;
- `WIN`;
- `LOSS`;
- `AMBIGUOUS`;
- `EXPIRED_NO_ENTRY`;
- `EXPIRED_OPEN`;
- `NOT_ELIGIBLE`.

## Intrabar ambiguity

OHLC candles do not prove intrabar event ordering.

Therefore:

- entry plus Stop/Target touched in the same candle -> `AMBIGUOUS`;
- after entry, Stop and Target touched in the same candle -> `AMBIGUOUS`;
- ambiguous outcomes are excluded from binary WIN/LOSS calibration samples.

No optimistic or pessimistic ordering assumption is allowed.

## Outcome R

`outcome_r` is a planned target/stop touch label, not realized broker PnL:

- target touch -> planned geometry reward/risk multiple;
- stop touch -> `-1R`;
- ambiguous/open/expired/not-eligible -> N/A.

Slippage, fees, funding and execution quality are not modeled in Phase 11B.

## Horizon

The evaluator does not invent a universal holding period. `horizon_end` is explicit and optional.

This keeps outcome observation separate from future Trading Engine policy. A two-hour study can pass an explicit two-hour horizon without redefining canonical entry rules.

## Persistence

`OutcomeRepository` stores outcome observations in SQLite with deterministic `decision_id` fingerprints.

Upserts allow an unresolved observation (`PENDING_ENTRY`/`OPEN`) to be replaced later by a resolved observation for the same decision.

`list_binary_resolved()` exposes only `WIN`/`LOSS` records for future calibration tooling. It intentionally does not calculate a win rate or probability.

## Calibration guardrail

Phase 11B provides data plumbing only.

Before any `Estimated Probability` is introduced, a later phase must define and approve at minimum:

- sufficient sample size;
- train/validation/test separation by time;
- provider/symbol/regime stratification rules;
- survivorship/listing bias handling;
- ambiguous and unresolved outcome policy;
- transaction-cost assumptions;
- calibration metric and confidence intervals;
- out-of-sample validation.

Until then, `estimated_probability` remains N/A/null.
