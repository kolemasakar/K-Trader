# K-Trader Custom GPT Action Guide v1.0

## Role

The Action is a read-only bridge from K_Trader Custom GPT to the K-Trader scanner API.

It is not a trading/execution API and cannot place, modify or cancel orders.

## Preferred operations

For requests such as "find the best setups now":

1. `getHealth` or `getScannerStatus` when data readiness is unknown.
2. `listSignals` for current A/A+ LONG/SHORT signals.
3. `listCandidates` when the user asks why assets were rejected or wants lower grades.

For one symbol:

1. `getAnalysis` for the canonical TradingDecision.
2. `getMarketSnapshot` for latest normalized ticker/liquidity metadata.
3. `getCandles` only when raw confirmed bars are needed, for example to show the latest VSA sequence.

## Provider ambiguity

A canonical symbol may exist on more than one provider.

If an operation returns HTTP 409, repeat it with the explicit `provider_id` supplied by the API response/context.

Never silently substitute another provider.

## Data rules

- API market data has priority over Web Search for current OHLCV/VSA analysis.
- Never mix candle series from different providers.
- Respect `freshness_status`, `data_time`, `last_closed_bar` and `data_age_seconds`.
- Stale/insufficient data cannot be promoted to a trade.
- Decimal market values are serialized as strings to preserve exact exchange precision.
- `Setup Score` is not a statistical probability.
- `estimated_probability` remains null until a calibrated historical model exists.

## Output rule

Use the canonical TradingDecision returned by `getAnalysis`/`listSignals`; do not reconstruct Entry, SL, TP, RR, ATR-used or grade independently.

If the API returns `NO_TRADE`, preserve it and explain `reason_codes` rather than overriding the engine.

## Deployment placeholder

`custom_gpt/openapi.yaml` currently points to `https://api.k-trader.invalid` intentionally.

Phase 10 must replace it with the real HTTPS host before the Action is enabled in the GPT editor.
