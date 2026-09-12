# POSITION W1 Derived Data Contract v0

Status: **PREREGISTERED / RESEARCH ONLY**

Purpose: enable prototype POSITION research without changing the canonical production MTF contract.

Source dataset:

`/data/research/phase11g/profile_research_dataset_v0_20260911T204500Z_adaptive`

## Source

W1 candles are derived only from the dataset's provider-recorded, closed Binance USDM D1 candles.

No external candles, interpolation or cross-provider splicing is allowed.

## Week definition

UTC ISO week:

- open: Monday `00:00:00 UTC`;
- close: Sunday `23:59:59.999 UTC`.

A derived W1 candle is emitted only if:

- exactly seven consecutive closed D1 candles are present for Monday through Sunday;
- all seven D1 source bars belong to the same ISO week;
- the weekly close is strictly before/equal to the dataset `as_of` cutoff.

Partial listing week and current incomplete week are excluded.

## OHLCV aggregation

- open = Monday D1 open;
- high = max high of seven D1 bars;
- low = min low of seven D1 bars;
- close = Sunday D1 close;
- volume/quote volume/trade counts are summed when available.

## Provenance

For every symbol store:

- source D1 manifest/hash;
- source D1 bar count;
- derived W1 count;
- first/last derived W1 timestamps;
- excluded partial-week count;
- W1 payload hash;
- dataset `as_of`.

## Usage boundary

This W1 layer is for POSITION prototype/research only. It does not modify:

- production intervals;
- frozen v2.2;
- FAST/SWING baseline rules;
- holdout authorization.

Current D1 depth is expected to yield only roughly 47–71 complete W1 bars, so W1 is suitable for architecture/prototype checks, not strong statistical promotion evidence.
