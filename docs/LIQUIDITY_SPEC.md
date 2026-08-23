# Liquidity Specification v1.0

## Goal

Rank eligible instruments by practical tradability using normalized public data.

## Inputs

Preferred inputs, subject to provider capability:
- 24h quote volume
- trade count
- bid/ask spread or book ticker
- optional open interest

Raw base volume alone SHALL NOT define liquidity rank.

## Normalization

Provider-specific raw fields are mapped to comparable normalized metrics. Missing optional metrics reduce confidence but are not fabricated.

## Output

Per instrument:
- quote_volume_24h
- trade_count_24h if available
- spread_abs / spread_bps if available
- open_interest if available
- liquidity_score
- liquidity_rank
- liquidity_confidence

## Rules

- Minimum liquidity thresholds are configuration.
- Liquidity score weights are versioned and testable.
- A provider lacking a metric uses a documented reduced feature set; results retain provider identity.
- Extremely wide spread can hard-reject an otherwise high-volume asset.
